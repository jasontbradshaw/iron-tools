import util
import rtp
import logging
import time
import os
import threading

class ProcessAlreadyRunningError(Exception):
    """Indicates an attempt to start the same process twice."""
    pass

class ProcessOperationTimeoutError(Exception):
    """Indicates a process operation that timed out."""
    pass

class NoRecordedFileError(Exception):
    """Indicates an attempt to commit a time without a previous recording."""
    pass

class RecorderState:
    """
    Object used to initialize and store state variables for Recorder.
    """
    
    def __init__(self):
        """
        Initializes the state variables to their default vaules.
        """
        
        # most recently committed time, applies to most recent dump file
        self.__commit_time = None
        
        # unix time recording was started
        self.__start_time = None
        
        # file most recently dumped to
        self.__dump_file = None
    
    def set_commit_time(self, t):
        self.__commit_time = t
    
    def get_commit_time(self):
        return self.__commit_time
    
    def set_start_time(self, t):
        self.__start_time = t
    
    def get_start_time(self):
        return self.__start_time
    
    def set_dump_file(self, f):
        self.__dump_file = f
    
    def get_dump_file(self):
        return self.__dump_file
    
class Recorder:
    """
    Manages processes and state for playing and recording RTP streams.
    """
    
    def __init__(self, logger):
        
        # process managing classes
        self.rtpplay = rtp.RTPPlay()
        self.rtpdump = rtp.RTPDump()
        
        # user-provided logger
        self.logger = logger
        
        # rtpdump parameters
        self.dump_address = "0.0.0.0"
        self.dump_port = 5006
        
        # rtpplay parameters
        self.preview_address = "10.98.0.81"
        self.preview_port = 5008
        
        # directories used when saving/previewing files
        self.sync_dir = "sync"
        self.dump_dir = os.path.join(self.sync_dir, "dump")
        
        # name/file extension of recorded video files
        self.video_basename = "_sermon"
        self.video_file_ext = "dump"
        
        # file extension for commit files (they share the video's name)
        self.commit_file_ext = "commit"
        
        # maximum time we will wait for a process to complete an action
        self.max_block_time = 3
        
        # state class that keeps track of all the variables we need
        self.state = RecorderState()
        
        # make sure we have the directory structure we'll need
        self._create_dirs()
        
        # make sure critical operations are atomic
        self.__lock = threading.Lock()
    
    def _create_dirs(self):
        """
        Creates the sync and dump directories if they don't already exist.
        """
        
        # create sync directory
        if not os.path.exists(self.sync_dir):
            os.makedirs(self.sync_dir)
        
        # create dump directory
        if not os.path.exists(self.dump_dir):
            os.makedirs(self.dump_dir)
    
    def _write_commit_file(self, filename, t):
        """
        Writes the given time to the coresponding file in the sync
        directory.
        """
        
        # create the file name we will write to
        commit_file_name = filename + "." + self.commit_file_ext
        commit_file = os.path.join(self.sync_dir, commit_file_name)
        
        # write a single integer to the file, nothing else
        with open(commit_file, 'w') as cf:
            cf.write(str(t))
    
    def start_record(self):
        """
        Begins dumping the configured stream to disk.  Raises an exception
        if the process fails for any reason.
        """
        
        with self.__lock:
            # don't allow the user to start the record process twice
            if self.rtpdump.isalive():
                msg = "rtpdump process was already running"
                raise ProcessAlreadyRunningError(msg)
        
            # name of the file we're dumping to
            dump_file = os.path.join(self.dump_dir,
                            util.generate_file_name(self.video_basename))
        
            # start the process
            rtpdump.start(dump_file, self.dump_address, self.dump_port)
        
            if not util.block_until(self.rtpdump.isalive, self.max_block_time):
                msg = "rtpdump process failed to start within allotted time"
                raise ProcessOperationTimeoutError(msg)
        
            # set state variables to correspond to new file if process started
            self.state.set_commit_time(None)
            self.state.set_start_time(util.get_time())
            self.state.set_dump_file(dump_file)
    
    def stop_record(self):
        """
        Terminates the current rtpdump process, or does nothing if no
        process was active.  Returns the final elapsed time and the
        dump file name as a tuple on successful exit.
        """
        
        with self.__lock:
            # tell the process to exit
            self.rtpdump.stop()
        
            # wait until it does, or throw an error if it doesn't
            if not util.block_while(rtpdump.isalive, self.max_block_time):
                msg = "rtpdump process failed to end within the allotted time"
                raise ProcessOperationTimeoutError(msg)
        
            # retrieve the final status before resetting it
            final_status = self.get_status()
        
            # since we ended the process, we reset the start time
            self.state.set_start_time(None)
        
        return final_status
    
    def get_status(self):
        """
        Returns a tuple of the current commit time, the amount of time
        elapsed since the current recording started, and whether the
        rtpdump process is currently recording.
        """
        
        commit_time = self.state.get_commit_time()
        elapsed_time = util.get_time() - self.state.get_start_time()
        is_recording = self.rtpdump.isalive()
        
        # we ensure the types of all this outgoing data
        return commit_time, elapsed_time, is_recording
    
    def commit_time(self, t):
        """
        Sets the commit time of the currently recording file, if there is
        one.  Raises an exception otherwise.
        """
    
        with self.__lock:
            # prevent setting a commit time if no file has been dumped yet
            if self.state.get_commit_time() is None:
                msg = ("commit time can only be set if at least one file"
                       "has been recorded this session")
                raise NoRecordedFileError(msg)
        
            # set the actual commit time
            self.state.set_commit_time(t)
        
            # get the base name of the dump file and write a commit file for it
            base_dump_filename = os.path.basename(self.state.get_dump_file())
            self._write_commit_file(base_dump_filename,
                                    self.state.get_commit_time())
    
    def play_preview(self, start_time, duration=30):
        """
        Plays the most recently recorded file from the given time for
        the given duration.
        """
        
        with self.__lock:
            # make sure something has been recorded before previewing
            if self.state.get_dump_file() is None:
                msg = "a recording must have been started to enable preview"
                raise NoRecordedFileError(msg)
        
            # ensure the file we are trying to play exists already
            if not os.path.exists(self.state.get_dump_file()):
                msg = ("could not find dump file '%s' for preview" %
                       self.state.get_dump_file())
                raise IOError(msg)
        
            # end the current preview before starting another one
            rtpplay.stop()
            if not util.block_while(rtpplay.isalive, self.max_block_time):
                msg = "failed to terminate previously running rtpplay process"
                raise ProcessOperationTimeoutError(msg)
        
            # attempt to play the given file
            rtpplay.start(self.state.get_dump_file(), self.preview_address,
                          self.preview_port, start_time=start_time,
                          end_time=start_time + duration)
        
            # wait until the process starts
            if not util.block_until(rtpplay.isalive, self.max_block_time):
                msg = "rtpplay failed to start or exited very quickly"
                raise ProcessOperationTimeoutError(msg)
