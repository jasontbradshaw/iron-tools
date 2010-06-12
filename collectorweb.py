#!/usr/bin/env python

import flask
from flask import Flask

import util
import rtp

app = Flask(__name__)

# always access the datastore's contents with a 'with' statement!
glob = util.ThreadedDataStore()

# these do the playing and recording
rtpdump = rtp.RTPDump()

# config variables
RTPDUMP_ADDRESS = "localhost"
RTPDUMP_PORT = 9876

"""
Conventions:
  - Returning the empty JSON object {} signifies success.
"""

@app.route("/")
def hello():
    return "Collector Web"

@app.route("/start_record")
def start_record():
    """
    Starts the recording process.
    """
    
    # save the time we started recording
    with glob:
        glob["start_time"] = util.time()
    
    # if rtpplay is already started, return
    if rtpdump.isalive():
        return flask.jsonify(warning="rtpplay already running.")
    
    # try to start it, but return an error if it doesn't succeed
    try:
        rtpdump.start(RTPDUMP_ADDRESS, RTPDUMP_PORT)
        if not rtpdump.isalive():
            raise Exception("Failed to start rtpdump.")
    except Exception as e:
        return flask.jsonify(error=str(e))
    
    return flask.jsonify()

@app.route("/stop_record")
def stop_record():
    """
    Stops the recording process and sets the start time back to 'None'.
    """
    
    rtpdump.stop()
    
    # prevents counting elapsed time while stopped
    with glob:
        glob["start_time"] = None
    
    return flask.jsonify()

@app.route("/get_elapsed_time")
def get_elapsed_time():
    """
    Returns the elapsed time of the current recording in seconds, or 'None'
    if no recording is currently active.
    """
    
    with glob:
        # only return a time if one has been set or reset to 'None'
        if "start_time" in glob and glob["start_time"] is not None:
            elapsed_time = util.time() - glob["start_time"]
        else:
            return flask.jsonify(elapsed_time=None)
    
    return flask.jsonify(elapsed_time=elapsed_time)

@app.route("/commit_time/<int:t>")
def commit_time(t):
    """
    Sets the current global video start time that gets transmitted
    to all clients.
    """
    
    with glob:
        glob["commit_time"] = t
    
    return flask.jsonify()

@app.route("/get_commit_time")
def get_commit_time():
    """
    Returns the time committed by the commit function, or 0 if none has
    been committed yet.
    """
    
    with glob:
        if "commit_time" in glob:
            return flask.jsonify(commit_time=glob["commit_time"])
        else:
            return flask.jsonify(commit_time=0)

if __name__ == "__main__":
    app.secret_key = "replace me!"
    app.run(debug = True)
