#!/usr/bin/env python

import os
import time
import logging

import flask
from flask import Flask

import util
import rtp

app = Flask(__name__)

# set up logging
COLLECTOR_LOG_FILENAME = "collector.log"
logging.basicConfig(filename=COLLECTOR_LOG_FILENAME, level=logging.NOTSET)
log = logging.getLogger("collector")

# always access the datastore's contents with a 'with' statement!
glob = util.ThreadedDataStore()

# these do the playing and recording
rtpdump = rtp.RTPDump()
rtpplay = rtp.RTPPlay()

# config variables
RTPDUMP_ADDRESS = "0.0.0.0"
RTPDUMP_PORT = 5006

# where dump preview gets sent
RTPPLAY_PREVIEW_ADDRESS = "10.98.0.81"
RTPPLAY_PREVIEW_PORT = 5008

# location that gets synced with receivers
SYNC_DIR = "sync"
DUMP_DIR = os.path.join(SYNC_DIR, "dump")

# create sync directories if they don't exist
try:
    if not os.path.exists(DUMP_DIR):
        os.makedirs(DUMP_DIR)
except OSError:
    # failing means the directories already exist
    pass

# text to include after the time in dumped files
VIDEO_BASENAME = "_sermon"

"""
Conventions:
  - Returning the empty JSON object {} signifies success.
"""

def write_commit_file(filename, t, extension="time"):
    """
    Writes the given time to the given dump file name and saves it to the
    sync directory.
    """
    
    log.debug("called write_commit_file(%s, %s, %s)" %
              (str(filename), str(t), str(extension)))
    
    # write the time to its file
    commit_file = os.path.join(SYNC_DIR, filename + "." + extension)
    with open(commit_file, 'w') as f:
        f.write(str(t))
        log.debug("write_commit_file: file written.")

@app.route("/")
def index():
    log.debug("called /")
    
    return flask.redirect("/static/collector/index.html")

@app.route("/dev")
def devinterface():
    """
    A super-simple development interface for simple interaction with the
    application.
    """
    
    html = "Dev Interface<hr />"
    
    # static links we want to link to (those without parameters)
    static_links = ["/start_record", "/stop_record", "/get_record_status",
                    "/play_preview/0", "/commit_time/30"]
    
    for link in static_links:
        html += '<a href="%s">%s</a><br />' % (link, link)
    
    return html
    
@app.route("/start_record")
def start_record():
    """
    Starts the recording process.
    """
    
    log.debug("called /start_record")
    
    # if rtpdump is already started, return
    if rtpdump.isalive():
        log.debug("start_record: rtpdump already running.")
        return flask.jsonify(warning="rtpdump already running.")
    
    # save the time we started recording, clear previous commit time
    with glob:
        glob["start_time"] = util.get_time()
        glob["commit_time"] = None
    
    # try to start it, but return an error if it doesn't succeed
    try:
        dump_file = os.path.join(DUMP_DIR,
                                 util.generate_file_name(VIDEO_BASENAME))
        rtpdump.start(dump_file, RTPDUMP_ADDRESS, RTPDUMP_PORT)
        
        with glob:
            glob["dump_file"] = dump_file
        
        # give rtpdump a chance to start, and return an error if it didn't
        if not util.block_until(rtpdump.isalive, 1):
            raise Exception("Failed to start rtpdump.")
        
    except Exception as e:
        log.error("start_record: %s" % str(e))
        return flask.jsonify(error=str(e))
    
    return flask.jsonify()

@app.route("/stop_record")
def stop_record():
    """
    Stops the recording process and sets the start time back to 'None'.
    """
    
    log.debug("called /stop_record")
    
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
    
    log.debug("called /get_record_status")
    
    # retrieve commit time, elapsed time, and recording status
    with glob:
        commit_time = 0
        if "commit_time" in glob and glob["commit_time"] is not None:
            commit_time = glob["commit_time"]
        
        elapsed_time = 0
        if "start_time" in glob and glob["start_time"] is not None:
            elapsed_time = util.get_time() - glob["start_time"]
    
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
    
    log.debug("called /commit_time/%d" % t)

    # set commit time
    with glob:
        # make sure 
        if "dump_file" not in glob:
            log.error("commit_time: no file was recording, no time set.")
            return flask.jsonify(
                error="no currently recording file, no commit time set.")
        
        # set current commit time
        glob["commit_time"] = t
        
        # get file name to write this commit time to
        dump_file = glob["dump_file"]
    
    # write the commit file to disk
    base_filename = os.path.basename(dump_file)
    write_commit_file(base_filename, t)
    
    return flask.jsonify()
        
@app.route("/play_preview/<int:start_time>")
@app.route("/play_preview/<int:start_time>/<int:duration>")
def play_preview(start_time, duration=30):
    """
    RTPPlay duration seconds of the current dump starting at time start_time.
    """

    log.debug("called /play_preview/%d/%d" % (start_time, duration))

    # get last started record
    with glob:
        if "dump_file" not in glob:
            log.info("play_preview: no recording started, unable to preview.")
            return flask.jsonify(
                error="no recording started, unable to preview.")
        
        dump_file = glob["dump_file"]
    
    # ensure the file exists
    if not os.path.exists(dump_file):
        log.error("play_preview: could not find file '%s'." % dump_file)
        return flask.jsonify(error="could not find file '%s'" % dump_file)
    
    # stop the current preview
    rtpplay.stop()
    
    # wait until it dies before starting another, but only to a limit
    if not util.block_while(rtpplay.isalive, 3):
        log.error("play_preview: rtpplay took too long to stop.")
        return flask.jsonify(
            error="rtpplay did not stop in a reasonable amount of time")
    
    # attempt to play the given file
    rtpplay.start(dump_file, RTPPLAY_PREVIEW_ADDRESS,
            RTPPLAY_PREVIEW_PORT, start_time=start_time,
            end_time=start_time + duration)
    
    # wait until it starts, or fails to start
    if not util.block_until(rtpplay.isalive, 1):
        log.error("play_preview: rtpplay did not start correctly.")
        return flask.jsonify(error="rtpplay is not alive")
    
    return flask.jsonify()

if __name__ == "__main__":
    app.secret_key = "replace me!"
    app.run(host="0.0.0.0", port=5081, debug=True)
