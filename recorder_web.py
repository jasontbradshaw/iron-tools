import os
import time
import logging

import flask
from flask import Flask

import recorder

app = Flask(__name__)

# set up logging
RECORDER_LOG_FILENAME = "recorder.log"
logging.basicConfig(filename=RECORDER_LOG_FILENAME, level=logging.NOTSET,
                    format="%(asctime)s\t%(name)s:%(levelname)s\t%(message)s")
log = logging.getLogger("recorder")

# config variables
RTPDUMP_ADDRESS = "0.0.0.0"
RTPDUMP_PORT = 5006

# where dump preview gets sent
RTPPLAY_PREVIEW_ADDRESS = "10.98.0.81"
RTPPLAY_PREVIEW_PORT = 5008

# location that gets synced with receivers
SYNC_DIR = "sync"
DUMP_DIR = os.path.join(SYNC_DIR, "dump")

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
    
    recorder.write_commit_file(filename, t, extension="time")

@app.route("/")
def index():
    log.debug("called /")

    return flask.render_template("recorder.html")

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

    recorder.start_record()

@app.route("/get_record_status")
def get_record_status():
    """
    Returns the status of the recording, including elapsed time, whether
    a recording is happending, and what the commit time is set to.
    """

    log.debug("called /get_record_status")
    status = recorder._get_status()
    return flask.jsonify(seconds_elapsed=status[1],
                         committed_time=status[0],
                         is_recording=status[2])

if __name__ == "__main__":
    app.secret_key = "replace me!"
    app.run(host="0.0.0.0", port=5081, debug=True)
