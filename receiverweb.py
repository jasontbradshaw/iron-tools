#!/usr/bin/env python

import flask
import os

from flask import Flask

import rtp
import util

"""
--WHITEBOARD--
get_file_list -> json[]
play_file(file_name)
get_status -> json (i.e. downloading,startime)
"""

app = Flask(__name__)

# always use 'with' to access data store's data!
glob = util.ThreadedDataStore()

rtpplay = rtp.RTPPlay('localhost', 9000, "dummy.dump")

@app.route("/")
def hello():
    return "Receiver Web"

@app.route("/play_file")
def play_file(file_name):
    """
    Plays the given file.
    """
    
    rtpplay.address = None # TODO: specify ip address
    rtpplay.inputfile = file_name
    if not rtpplay.isalive():
        return flask.jsonify(error = "rtplay is not alive")
    
    # can't paly a file if rtpplay isn't working
    if not rtpplay.isalive():
        return flask.jsonify(error="rtp is not alive")
    
    rtpplay.start()
    return flask.jsonify()

@app.route("/stop_playback")
def stop():
    if not rtpplay.isalive():
        return flask.jsonify(error="rtp is not alive")
    rtpplay.stop()
    return flask.jsonify()

@app.route("/get_file_list")
def get_file_list():
    path = "" # TODO: specify path name
    if os.path.exists(path):
        dirList = os.listdir(path)
    else:
        dirList = []
    return flask.jsonify(file_list = dirList)

@app.route("/load_file/<file_name>")
def load_file(file_name):
    return flask.jsonify()

@app.route("/get_status")
def get_status():
    return None

if __name__ == "__main__":
    app.secret_key = "replace me as well!"
    app.run(debug = True)
