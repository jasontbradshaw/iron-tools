#!/usr/bin/env python

import os

import flask
from flask import Flask

import util
import rtp

app = Flask(__name__)
rtpplay = rtp.RTPPlay()

glob = util.ThreadedDataStore()

# config variables
RTPPLAY_ADDRESS = "10.98.0.81"
RTPPLAY_PORT = 5008

# directories synced from server
SYNC_DIR = "sync"
DUMP_DIR = os.path.join(SYNC_DIR, "dump")

# create sync directories if they don't exist
try:
    if not os.path.exists(DUMP_DIR):
        os.makedirs(DUMP_DIR)
except OSError:
    # failing means the directories already exist
    pass

def load_commit_time(filename, extension="time"):
    """
    Loads a commit time from a file and return it as an integer.
    
    'filename' is the name of a video file founnd in the dump directory.
    """
    
    dump_file = os.path.join(SYNC_DIR, filename + "." + extension)
    
    # read file time, or 0 if we couldn't
    try:
        with open(dump_file, 'r') as f:
            num = int(f.read())
    except OSError:
        pass
    except ValueError:
        pass
    except IOError:
        pass
    
    # return the default value if we failed to get the time for any reason
    return 0
    
@app.route("/")
def hello():
    return "Receiver Web"

@app.route("/stop")
def stop():
    """
    End playback of any currently running processes.  If none are running,
    it still returns success.
    """
    
    # stop works even on a non-running process
    rtpplay.stop()
    
    # mark playback as stopped
    with glob:
        glob["is_playing"] = False
        glob["armed_file"] = None
    
    return flask.jsonify()

@app.route("/get_file_list")
def get_file_list(extension="time"):
    """
    Returns a list of files found in the dump directory.
    """
    
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
        
        # add them all to the list as a tuple of (filename, found time?, size)
        results.append((f, commit_time_found, size))
    
    return flask.jsonify(file_list=results)

@app.route("/arm/<file_name>")
def arm(file_name):
    """
    Attempts to play the file argument.  Returns success if it could find
    the file and was not already playing, otherwise an error.
    """
    
    # don't arm again if already running
    if rtpplay.isalive():
        return flask.jsonify(warning="rtpplay is already running.")
    
    path = os.path.join(DUMP_DIR, file_name)
    
    # ensure the file exists
    if not os.path.isfile(path):
        return flask.jsonify(error="Could not find file '%s'." % file_name)
    
    # get the commit time from file
    commit_time = load_commit_time(file_name)
    
    # attempt to play the given file
    rtpplay.start(path, RTPPLAY_ADDRESS, RTPPLAY_PORT, start_time=commit_time,
                  wait_start=True)
    
    if not rtpplay.isalive():
        return flask.jsonify(error="rtpplay did not start correctly.")
    
    # save file name for get_status
    with glob:
        glob["armed_file"] = file_name
    
    return flask.jsonify()

@app.route("/play")
def play():
    """
    Starts the actual playback queued up by the arm process.
    """
    
    # warn if rtpplay is not yet running
    if not rtpplay.isalive():
        return flask.jsonify(warning="rtpplay is not alive, no signal sent.")
    
    # send the signal to start playback
    rtpplay.begin_playback()
    
    # mark playback as started
    with glob:
        glob["is_playing"] = True
    
    return flask.jsonify()

@app.route("/get_status")
def get_status():
    """
    Returns helpful status information.
    """
    
    with glob:
        retfile = None
        if "armed_file" in glob and glob["armed_file"] is not None:
            retfile = glob["armed_file"]
            
        playing = False
        if "is_playing" in glob and glob["is_playing"] is not None:
            playing = glob["is_playing"]
    
    return flask.jsonify(file=retfile, is_playing=playing)

if __name__ == "__main__":
    app.secret_key = "replace me as well!"
    app.run(host="127.0.0.1", port=5082, debug=True)
