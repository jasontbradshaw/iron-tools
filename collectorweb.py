#!/usr/bin/env python

import os

import flask
from flask import Flask

import util
import rtp

app = Flask(__name__)

# always access the datastore's contents with a 'with' statement!
glob = util.ThreadedDataStore()

# these do the playing and recording
rtpdump = rtp.RTPDump()
rtpplay = rtp.RTPPlay()

# config variables
RTPDUMP_ADDRESS = "localhost"
RTPDUMP_PORT = 9876

# where dump preview gets sent
RTPPLAY_PREVIEW_ADDRESS = "localhost"
RTPPLAY_PREVIEW_PORT = 10000

# location that gets rsync'ed with receivers
SYNC_DIR = "collector/"

# name of the video file to dump to
VIDEO_BASENAME = "sermon"

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
    
    # if rtpdump is already started, return
    if rtpdump.isalive():
        return flask.jsonify(warning="rtpdump already running.")
    
    # try to start it, but return an error if it doesn't succeed
    try:
        fname = os.path.join(SYNC_DIR, VIDEO_BASENAME)
        rtpdump.start(fname, RTPDUMP_ADDRESS, RTPDUMP_PORT)
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

@app.route("/elapsed_time")
def elapsed_time():
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

@app.route("/commit_time")
@app.route("/commit_time/<int:t>")
def commit_time(t=None):
    """
    Sets or returns the current global video start time that gets
    transmitted to all clients.
    """
    
    # return or set depending on whether we got a value for 't'
    if t is not None:
        with glob:
            glob["commit_time"] = t
        
        # write the commit time to file
        with open(os.path.join(SYNC_DIR, "commit_time"), 'w') as f:
            f.write(str(t))
    else:
        # return it if its there, otherwise return 0
        with glob:
            if "commit_time" in glob:
                return flask.jsonify(commit_time=glob["commit_time"])
            else:
                return flask.jsonify(commit_time=0)
    
    # always return success if we made it this far
    return flask.jsonify()

@app.route("/play_preview/<int:start_time>")
@app.route("/play_preview/<int:start_time>/<int:duration>")
def play_preview(start_time, duration=30):
    """
    RTPPlay duration seconds of the current dump starting at time start_time.
    """

    # ensure the file exists
    if not os.path.exists(rtpdump.outputfile):
        return flask.jsonify(error="Could not find file '%s'." %
                rtpdump.outputfile)
    
    # attempt to play the given file
    rtpplay.start(rtpdump.outputfile, RTPPLAY_PREVIEW_ADDRESS,
            RTPPLAY_PREVIEW_PORT, start_time=start_time,
            end_time=start_time+duration)
    
    if not rtpplay.isalive():
        return flask.jsonify(error="rtpplay is not alive")
    
    return flask.jsonify()

if __name__ == "__main__":
    app.secret_key = "replace me!"
    app.run(debug = True, port=5000)
