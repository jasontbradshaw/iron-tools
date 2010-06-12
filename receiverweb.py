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

@app.route("/")
def hello():
    return "Receiver Web"

@app.route("/stop")
def stop():
    if not rtpplay.isalive():
        return flask.jsonify(error = "rtp is not alive")
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

@app.route("/play_file/<string:file_name>")
def play_file(file_name):
    rtpplay.start(file_name, 'localhost', 9000)
    
    if not rtpplay.isalive():
        return flask.jsonify(error = "rtplay is not alive")
    
    return flask.jsonify()

@app.route("/get_status")
def get_status():
    return None

if __name__ == "__main__":
    app.secret_key = "replace me as well!"
    app.run(debug = True)
