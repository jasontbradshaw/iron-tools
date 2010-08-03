import logging
import time
import os
import threading

import util
import rtp
from it_exceptions import *

class Recorder:
    """
    Manages processes and state for playing and recording RTP streams.
    """
    
    def __init__(self):
        
        # process managing classes
        self.rtpplay = rtp.RTPPlay()
        self.rtpdump = rtp.RTPDump()
        
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
        
        # replaced with custom function in unit tests
        self.file_exists = os.path.exists

        # make sure we have the directory structure we'll need
        self._create_dirs()
        
        # make sure critical operations are atomic
        self.__lock = threading.Lock()
        
        # state variables
        self.commit_time = None
        self.start_time = None
        self.dump_file = None
    
    def _create_dirs(self):
        """
        Creates the sync and dump directories if they don't already exist.
        """
        
        # create sync directory
        if not self.file_exists(self.sync_dir):
            os.makedirs(self.sync_dir)
        
        # create dump directory
        if not self.file_exists(self.dump_dir):
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
        Begins dumping the configured stream to disk.
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
            self.rtpdump.start(dump_file, self.dump_address, self.dump_port)
            
            if not util.block_until(self.rtpdump.isalive, self.max_block_time):
                msg = "rtpdump process failed to start within allotted time"
                raise ProcessOperationTimeoutError(msg)
            
            # set state variables to correspond to new file if process started
            self.commit_time = None
            self.start_time = util.get_time()
            self.dump_file = dump_file
    
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
            if not util.block_while(self.rtpdump.isalive, self.max_block_time):
                msg = "rtpdump process failed to end within the allotted time"
                raise ProcessOperationTimeoutError(msg)
            
            # retrieve the final status before resetting it
            final_status = self._get_status()
            
            # since we ended the process, we reset the start time
            self.start_time = None
            
            return final_status
    
    def get_status(self):
        """
        External, thread-safe version of get_status.
        """
        
        with self.__lock:
            return self._get_status()
            
    def _get_status(self):
        """
        Returns a tuple of the current commit time, the amount of time
        elapsed since the current recording started, and whether the
        rtpdump process is currently recording.
        
        Not thread-safe, intended for internal use only.
        """
        
        elapsed_time = None
        if self.start_time is not None:
            elapsed_time = util.get_time() - self.start_time
        
        is_recording = self.rtpdump.isalive()
        
        # we ensure the types of all this outgoing data
        return self.commit_time, elapsed_time, is_recording
    
    def commit_time(self, t):
        """
        Sets the commit time of the currently recording file, if there is
        one.
        """
        
        with self.__lock:
            # prevent setting a commit time if no file has been dumped yet
            if self.dump_file is None:
                msg = ("commit time can only be set if at least one file"
                       "has been recorded this session")
                raise NoRecordedFileError(msg)
            
            # set the actual commit time
            self.commit_time = t
            
            # get the base name of the dump file and write a commit file for it
            base_dump_filename = os.path.basename(self.dump_file)
            self._write_commit_file(base_dump_filename, self.commit_time)
    
    def play_preview(self, start_time, duration=30):
        """
        Plays the most recently recorded file from the given time for
        the given duration.
        """
        
        with self.__lock:
            # make sure something has been recorded before previewing
            if self.dump_file is None:
                msg = "a recording must have been started to enable preview"
                raise NoRecordedFileError(msg)
            
            # ensure the file we are trying to play exists already
            if not self.file_exists(self.dump_file):
                msg = ("could not find dump file '%s' for preview" %
                       self.dump_file)
                raise FileNotFoundError(msg)
            
            # end the current preview before starting another one
            self.rtpplay.stop()
            
            if not util.block_while(self.rtpplay.isalive, self.max_block_time):
                msg = "failed to terminate previously running rtpplay process"
                raise ProcessOperationTimeoutError(msg)
            
            # attempt to play the given file
            self.rtpplay.start(self.dump_file, self.preview_address,
                          self.preview_port, start_time=start_time,
                          end_time=start_time + duration)
            
            # wait until the process starts
            if not util.block_until(self.rtpplay.isalive, self.max_block_time):
                msg = "rtpplay failed to start or exited very quickly"
                raise ProcessOperationTimeoutError(msg)
