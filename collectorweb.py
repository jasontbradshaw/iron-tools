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
RTPDUMP_ADDRESS = "0.0.0.0"
RTPDUMP_PORT = 5004

# where dump preview gets sent
RTPPLAY_PREVIEW_ADDRESS = "10.98.0.80"
RTPPLAY_PREVIEW_PORT = 5006

# location that gets rsync'ed with receivers
SYNC_DIR = "collector"
DUMP_DIR = os.path.join(SYNC_DIR, "dump")
COMMIT_FILE = os.path.join(SYNC_DIR, "commit_time")

# create rsync directories if they don't exist
try:
    if not os.path.exists(DUMP_DIR):
        os.makedirs(DUMP_DIR)
except OSError:
    # failing means the directories already exist
    pass

# name of the video file to dump to
VIDEO_BASENAME = "sermon_"

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
        # TODO: make file naming more flexible
        dump_file = os.path.join(DUMP_DIR,
                                 util.generate_file_name(VIDEO_BASENAME))
        rtpdump.start(dump_file, RTPDUMP_ADDRESS, RTPDUMP_PORT)
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
    
    # save the final status for return after varaible reset
    final_status = get_record_status()
    
    # prevents counting elapsed time while stopped
    with glob:
        glob["start_time"] = None
    
    return final_status

@app.route("/get_record_status")
def get_record_status():
    """
    Returns the status of the recording, including elapsed time, whether
    a recording is happending, and what the commit time is set to.
    """
    
    # retrieve commit time, elapsed time, and recording status
    with glob:
        commit_time = 0
        if "commit_time" in glob and glob["commit_time"] is not None:
            commit_time = glob["commit_time"]
        
        elapsed_time = 0
        if "start_time" in glob and glob["start_time"] is not None:
            elapsed_time = util.time() - glob["start_time"]
    
    is_recording = rtpdump.isalive()
    
    return flask.jsonify(seconds_elapsed=elapsed_time,
                         committed_time=commit_time,
                         is_recording=is_recording)
    
@app.route("/commit_time/<int:t>")
def commit_time(t):
    """
    Sets the current global video start time that gets transmitted to
    all clients.
    """
    
    # set commit time
    with glob:
        glob["commit_time"] = t
    
    # write the commit time to file
    with open(COMMIT_FILE, 'w') as f:
        f.write(str(t))

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
            end_time=start_time + duration)
    
    if not rtpplay.isalive():
        return flask.jsonify(error="rtpplay is not alive")
    
    return flask.jsonify()

if __name__ == "__main__":
    app.secret_key = "replace me!"
    app.run(debug=True, port=5000)
