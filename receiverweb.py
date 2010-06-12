#!/usr/bin/env python

import flask
import rtp
import os
from flask import Flask
from flask import flash

import util

"""
--WHITEBOARD--
get_file_list -> json[]
play_file(file_name)
get_status -> json (i.e. downloading,startime)
"""

app = Flask(__name__)
glob = util.ThreadedDataStore()
rtpplay = rtp.RTPPlay()

# config variables
RTPPLAY_ADDRESS = "localhost"
RTPPLAY_PORT = 9000
SYNC_DIR = "receiver/"

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
    
    path = "" # TODO: specify path name
    dirlist = []
    if os.path.exists(path):
        dirList = os.listdir(path)
    
    return flask.jsonify(file_list=dirList)

@app.route("/play_file/<file_name>")
def play_file(file_name):
    """
    Attempts to play the file argument.  Returns success if it could find
    the file, otherwise an error.
    """

    # ensure the file exists
    if not os.path.exists(file_name):
        return flask.jsonify(error="Could not find file '%s'." % file_name)
    
    # attempt to play the given file
    rtpplay.start(file_name, RTPPLAY_ADDRESS, RTPPLAY_PORT)
    
    if not rtpplay.isalive():
        return flask.jsonify(error="rtpplay is not alive")
    
    return flask.jsonify()

@app.route("/get_status")
def get_status():
    """
    Returns helpful status information.
    """
    
    # TODO: implement status reporting
    return flask.jsonify()

if __name__ == "__main__":
    app.secret_key = "replace me as well!"
    app.run(debug=True)
