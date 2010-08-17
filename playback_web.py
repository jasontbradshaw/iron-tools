#!/usr/bin/env python

import os
import logging

import flask

import util
import rtp
import playback

app = flask.Flask(__name__)
playback_obj = playback.Playback()

# set up logging
PLAYBACK_LOG_FILENAME = "playback.log"
logging.basicConfig(filename=PLAYBACK_LOG_FILENAME, level=logging.NOTSET,
                    format="%(asctime)s\t%(name)s:%(levelname)s\t%(message)s")
log = logging.getLogger("playback")

# config variables
RTPPLAY_ADDRESS = "127.0.0.1"#"10.98.0.81"
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

@app.route("/")
def index():
    log.debug("called /")
    
    return flask.render_template("playback.html")

@app.route("/dev")
def devinterace():
    
    html = "Dev Interface<hr />"
    
    static_links = ["/get_file_list", "/stop", "/arm/test.dump", "/play",
                    "/get_status"]
    
    for link in static_links:
        html += '<a href="%s">%s</a><br />' % (link, link)
    
    return html

@app.route("/stop")
def stop():
    """
    End playback of any currently running processes.  If none are running,
    it still returns success.
    """
    
    log.debug("called /stop")
    
    # stop works even on a non-running process
    try:
        playback_obj.stop()
    except Exception, e:
        return flask.jsonify(error=str(e))
    
    return flask.jsonify()

@app.route("/get_file_list")
def get_file_list(extension="time"):
    """
    Returns a list of files found in the dump directory.
    """
    
    log.debug("called /get_file_list")
    
    try:
        results = playback_obj.get_file_list()
    except Exception, e:
        return flask.jsonify(error=str(e))

    # format results to API spec
    formatted_list = []
    for file_name, commit_time, file_size in results:
        d = {"filename": file_name,
             "start_time_received": commit_time is not None,
             "file_size": file_size}
        
        formatted_list.append(d)
    
    return flask.jsonify(file_list=formatted_list)

@app.route("/arm/<file_name>")
def arm(file_name):
    """
    Attempts to play the file argument.  Returns success if it could find
    the file and was not already playing, otherwise an error.
    """
    
    log.debug("called /arm/%s" % file_name)

    try:
        playback_obj.arm(file_name)
    except Exception, e:
        return flask.jsonify(error=str(e))
    
    return flask.jsonify()

@app.route("/play")
def play():
    """
    Starts the actual playback queued up by the arm process.
    """

    log.debug("called /play")
    
    try:
        playback_obj.play()
    except Exception, e:
        return flask.jsonify(error=str(e))
    
    return flask.jsonify()

@app.route("/get_status")
def get_status():
    """
    Returns helpful status information.
    """
    
    log.debug("called /get_status")
    
    try:
        armed_file, is_playing = playback_obj.get_status()
    except Exception, e:
        return flask.jsonify(error=str(e))
    
    return flask.jsonify(file=armed_file, is_playing=is_playing)

if __name__ == "__main__":
    app.secret_key = "replace me as well!"
    app.run(host="0.0.0.0", port=5082, debug=True)
