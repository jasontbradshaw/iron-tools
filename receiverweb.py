#!/usr/bin/env python

import os

import flask
from flask import Flask

import util
import rtp

"""
--WHITEBOARD--
get_file_list -> json[]
play_file(file_name)
get_status -> json (i.e. downloading,startime)
"""

app = Flask(__name__)
#glob = util.ThreadedDataStore()
rtpplay = rtp.RTPPlay()

# config variables
RTPPLAY_ADDRESS = "localhost"
RTPPLAY_PORT = 9002

SYNC_DIR = "receiver/"
DUMP_DIR = os.path.join(SYNC_DIR, "dump")
COMMIT_FILE = os.path.join(SYNC_DIR, "commit_time")

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
    
    return flask.jsonify()

@app.route("/get_file_list")
def get_file_list():
    """
    Returns a list of files found in the dump directory.
    """
    
    # try to fill the list with files in the given path
    dirlist = []
    if os.path.exists(DUMP_DIR):
        dirlist = os.listdir(DUMP_DIR)
    
    # sort directories before returning
    dirlist.sort()
    
    return flask.jsonify(file_list=dirlist)

@app.route("/commit_time")
def commit_time():
    """
    Returns the current commit time found in the sync directory.
    """
    
    # attempt to read commit time from file
    commit_time = 0
    try:
        with open(COMMIT_FILE, 'r') as f:
            commit_time = int(f.read())
    except ValueError:
        return flask.jsonify(error="Non-integer commit time.")
    except IOError:
        # no file means start from 0
        pass
    
    return flask.jsonify(commit_time=commit_time)

@app.route("/play_file/<file_name>")
def play_file(file_name):
    """
    Attempts to play the file argument.  Returns success if it could find
    the file and was not already playing, otherwise an error.
    """
    
    # don't play again if already running
    if rtpplay.isalive():
        return flask.jsonify(warning="rtpplay already running.")
    
    path = os.path.join(DUMP_DIR, file_name)
    
    # ensure the file exists
    if not os.path.isfile(path):
        return flask.jsonify(error="Could not find file '%s'." % file_name)
    
    # try to get the commit time from file
    commit_time = 0
    try:
        with open(COMMIT_FILE, 'r') as f:
            commit_time = int(f.read())
    except ValueError:
        return flask.jsonify(error="Non-integer commit time.")
    except IOError:
        # if there's no file, start from 0
        pass
    
    # attempt to play the given file
    rtpplay.start(path, RTPPLAY_ADDRESS, RTPPLAY_PORT, start_time=commit_time)
    
    if not rtpplay.isalive():
        return flask.jsonify(error="rtpplay is not alive")
    
    return flask.jsonify()

@app.route("/get_status")
def get_status():
    """
    Returns helpful status information.
    """
    
    # TODO: implement status reporting
    return flask.jsonify(playing=rtpplay.isalive())

if __name__ == "__main__":
    app.secret_key = "replace me as well!"
    app.run(debug=True)
