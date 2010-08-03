#!/usr/bin/env python

import os
import logging
import threading
import time

import util
import rtp
from it_exceptions import *

class Receiver:
    
    def __init__(self):
        self.__lock = threading.Lock()
    
    def _load_commit_time(filename, extension="time"):
        """
        Loads a commit time from a file and return it as an integer.
        
        'filename' is the name of a video file founnd in the dump directory.
        """
        
        log.debug("load_commit_time(%s, %s)" % (filename, extension))
        
        dump_file = os.path.join(SYNC_DIR, filename + "." + extension)
        
        # read file time, or 0 if we couldn't
        num = 0
        try:
            with open(dump_file, 'r') as f:
                num = int(f.read())
        except OSError:
            num = None
        except ValueError:
            num = None
        except IOError:
            num = None
            
        # return 'None' if we failed to get the time for any reason
        return num
    
    def stop():
        """
        End playback of any currently running processes.  If none are running,
        it still returns success.
        """
        
        log.debug("called /stop")
        
        # stop works even on a non-running process
        rtpplay.stop()
        
        # mark playback as stopped
        with glob:
            glob["is_playing"] = False
            glob["armed_file"] = None
        
        return flask.jsonify()
    
    def get_file_list(extension="time"):
        """
        Returns a list of files found in the dump directory.
        """
        
        log.debug("called /get_file_list")
        
    # try to fill the list with files in the given path
        dirlist = []
        if os.path.exists(DUMP_DIR):
            dirlist = os.listdir(DUMP_DIR)
    
        # sort directories before returning
        dirlist.sort()
    
        results = []
        for f in dirlist:
            # get the size of the current file in bytes
            size = os.path.getsize(os.path.join(DUMP_DIR, f))
            
            # determine if we received a commit time for the file
            commit_file = os.path.join(SYNC_DIR, f + "." + extension)
            commit_time_found = os.path.exists(commit_file)
            
            # add them all to the list as a dict of attributes (jsonify turns it into
            # a javascript object)
            status_obj = {"filename": f,
                          "start_time_received": commit_time_found,
                          "file_size": size}
            
            results.append(status_obj)
        
        return flask.jsonify(file_list=results)
    
    def arm(file_name):
        """
        Attempts to play the file argument.  Returns success if it could find
        the file and was not already playing, otherwise an error.
        """
        
        log.debug("called /arm/%s" % file_name)
        
        # only arm again if currently alive and not playing
        if rtpplay.isalive():
            with glob:
                # don't allow arming if playback is happening
                if glob["is_playing"]:
                    msg = "arm: cannot arm a file during playback."
                    log.error(msg)
                    return flask.jsonify(error=msg)
            
            # kill the old armed process and arm a new one if not playing
            rtpplay.stop()
        
        path = os.path.join(DUMP_DIR, file_name)
        
        # ensure the file exists
        if not os.path.isfile(path):
            log.error("arm: could not find file '%s'." % file_name)
            return flask.jsonify(error="could not find file '%s'." % file_name)
        
        # get the commit time from file
        commit_time = load_commit_time(file_name)
        
        if commit_time is None:
            log.error("arm: no commit time found")
            return flask.jsonify(error="commit_time could not be loaded.")
        
        # attempt to play the given file
        rtpplay.start(path, RTPPLAY_ADDRESS, RTPPLAY_PORT, start_time=commit_time,
                      wait_start=True)
        
        # block for a bit until the process starts
        if not util.block_until(rtpplay.isalive, 3):
            log.error("arm: rtpplay did not start correctly")
            return flask.jsonify(error="rtpplay did not start correctly.")
        
        # save file name for get_status
        with glob:
            glob["armed_file"] = file_name
        
        return flask.jsonify()
    
    def play():
        """
        Starts the actual playback queued up by the arm process.
        """
        
        log.debug("called /play")
        
        # warn if rtpplay is not yet running
        if not rtpplay.isalive():
            log.warning("play: rtpplay not running, no newline sent to process")
            return flask.jsonify(warning="rtpplay is not alive, no signal sent.")
        
        # send the signal to start playback
        rtpplay.begin_playback()
        
        # mark playback as started
        with glob:
            glob["is_playing"] = True
            
        return flask.jsonify()
    
    def get_status():
        """
        Returns helpful status information.
        """
        
        log.debug("called /get_status")
        
        with glob:
            retfile = None
            if "armed_file" in glob and glob["armed_file"] is not None:
                retfile = glob["armed_file"]
            
            playing = False
            if ("is_playing" in glob and glob["is_playing"] is not None and
                rtpplay.isalive()):
                playing = glob["is_playing"]
        
        return flask.jsonify(file=retfile, is_playing=playing)
    
if __name__ == "__main__":
    app.secret_key = "replace me as well!"
    app.run(host="0.0.0.0", port=5082, debug=True)
