import os
import logging
import threading
import time

import util
import rtp
import config
from it_exceptions import *

class Playback:
    
    def __init__(self):
        self.__lock = threading.Lock()
        
        self.rtpplay = rtp.RTPPlay()
        self.rtpplay_live = rtp.RTPPlay()
        self.play_address = config.RTPPLAY_ADDRESS
        self.play_port = config.RTPPLAY_PORT

        self.sync_dir = config.SYNC_DIR
        self.dump_dir = config.DUMP_DIR
        
        self.max_block_time = config.MAX_BLOCK_TIME
        
        util.create_dirs(self.sync_dir, self.dump_dir)

        self._is_playing = False
        self._armed_file = None
        self._is_live_playing = False

        # replaced with custom function in unit tests
        self.file_exists = os.path.exists
        self.file_getsize = os.path.getsize
        self.listdir = os.listdir
        
    def _load_commit_time(self, filename, extension=config.COMMIT_FILE_EXT):
        """
        Loads a commit time from a file and return it as an integer.
        
        'filename' is the name of a video file founnd in the dump directory.
        """
        
        commit_file = os.path.join(self.sync_dir, filename + "." + extension)
        
        # read file time, or 0 if we couldn't
        num = 0
        try:
            with open(commit_file, 'r') as f:
                num = int(f.read())
        except OSError:
            num = None
        except ValueError:
            num = None
        except IOError:
            num = None
        
        # return 'None' if we failed to get the time for any reason
        return num
    
    def stop(self):
        """
        End playback of any currently running processes.  Simply resets the
        variables if no process was running.
        """
        
        with self.__lock:
            # stop works even on a non-running process
            self.rtpplay.stop()
            
            if not util.block_while(self.rtpplay.isalive, self.max_block_time):
                msg = "rtpplay did not terminate in the given amount of time."
                raise ProcessOperationTimeoutError(msg)
            
            # mark playback as stopped
            self._is_playing = False
            self._armed_file = None

    def stop_live(self):
        with self.__lock:
            # stop works even on a non-running process
            self.rtpplay_live.stop()
            
            if not util.block_while(self.rtpplay_live.isalive, self.max_block_time):
                msg = "rtpplay did not terminate in the given amount of time."
                raise ProcessOperationTimeoutError(msg)
            
            # mark playback as stopped
            self._is_live_playing = False
    
    def get_file_list(self):
        """
        Returns a list of files found in the dump directory as tuples of:
          (file name, commit_time, file size)
        """
        
        with self.__lock:
            # try to fill the list with files in the given path
            dirlist = []
            if not self.file_exists(self.dump_dir):
                msg = "dump directory does not exist."
                raise FileNotFoundError(msg)

            dirlist = self.listdir(self.dump_dir)
               
            
            # sort directory before returning
            dirlist.sort()
            
            result_files = []
            for f in dirlist:
                # get the size of the current file in bytes
                size = self.file_getsize(os.path.join(self.dump_dir, f))
                
                # determine if we received a commit time for the file
                commit_time = self._load_commit_time(f)
                
                # add them all to the list as a dict of attributes
                status = (f, commit_time, size)
                
                result_files.append(status)
            
            return result_files
    
    def arm(self, file_name):
        """
        Attempts to play the file argument.  Returns success if it could find
        the file and was not already playing, otherwise an error.
        """
        
        with self.__lock:
            # only arm again if currently alive and not playing
            if self.rtpplay.isalive():
                
                # don't allow arming if playback is happening
                if self._is_playing:
                    msg = "cannot arm a file during playback."
                    raise InvalidOperationError(msg)
            
                # same file already armed
                if file_name == self._armed_file:
                    return

                # kill the old armed process and arm a new one
                self.rtpplay.stop()
        
            path = os.path.join(self.dump_dir, file_name)
            
            # ensure the file exists
            if not self.file_exists(path):
                msg = "could not find file '%s' to arm." % file_name
                raise FileNotFoundError(msg)
            
            # get the commit time from file
            commit_time = self._load_commit_time(file_name)
            if commit_time is None:
                msg = "commit time is required to arm process."
                raise InvalidOperationError(msg)
            
            # attempt to play the given file
            self.rtpplay.start(path, self.play_address, self.play_port,
                               start_time=commit_time, wait_start=True,
                               end_wait_time=config.END_WAIT_TIME)
            
            # block for a bit until the process starts
            if not util.block_until(self.rtpplay.isalive, self.max_block_time):
                msg = "rtpplay did not start in the given amount of time."
                raise ProcessOperationTimeoutError(msg)
            
            # save file name for get_status
            self._armed_file = file_name
    
    def play(self):
        """
        Starts the actual playback queued up by the arm process.
        """
        
        with self.__lock:
            # warn if rtpplay is not yet running
            if not self.rtpplay.isalive():
                msg = "rtpplay not running, could not begin playback."
                raise InvalidOperationError(msg)
            
            # send the signal to start playback
            self.rtpplay.begin_playback()
            
            # mark playback as started
            self._is_playing = True
    
    def play_live(self, ip, port, end_wait_time=1):
        """
        Plays a live preview of the current or last armed/playing file to
        the given ip address and port.
        """
        
        with self.__lock:
            # warn if rtpplay is not yet running
            if self.rtpplay_live.isalive():
                msg = "live rtpplay already running, not starting playback."
                raise InvalidOperationError(msg)
            
            # make sure we've been given a file to play
            if self._armed_file is None:
                msg = "no file to view live, arm and/or play a file first."
                raise InvalidOperationError(msg)
            
            # attempt to play the current file
            self.rtpplay_live.start(self._armed_file, ip, port,
                                    skip_to_end=True,
                                    end_wait_time=end_wait_time)
            
            # block for a bit until the process starts
            if not util.block_until(self.rtpplay_live.isalive,
                                    self.max_block_time):
                msg = "rtpplay did not start in the given amount of time."
                raise ProcessOperationTimeoutError(msg)
            
            # mark playback as started
            self._is_live_playing = True
    
    def get_status(self):
        """
        Returns helpful status information.
        """
        
        with self.__lock:
            return self._armed_file, self._is_playing, self._is_live_playing
