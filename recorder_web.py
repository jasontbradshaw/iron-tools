#!/usr/bin/env python

import logging

import flask

import recorder
import config

app = flask.Flask(__name__)
recorder_obj = recorder.Recorder()

# set up logging
logging.basicConfig(filename=config.RECORDER_LOG_FILENAME,
                    level=logging.NOTSET,
                    format="%(asctime)s\t%(name)s:%(levelname)s\t%(message)s")
log = logging.getLogger("recorder")

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

    log.debug("called /start_record")
    try:
        recorder_obj.start_record()
        return flask.jsonify()
    except Exception, e:
        log.error("start_record: %s" % str(e))
        return flask.jsonify(error=str(e)) 

@app.route("/stop_record")
def stop_record():
    """
    Stops the recording process and sets the start time back to 'None'.
    """

    log.debug("called /stop_record")

    try:
        commit_time, elapsed_time, is_recording = recorder_obj.stop_record()
        
        if commit_time == None:
            commit_time = 0
        if elapsed_time == None:
            elapsed_time = 0
        
        return flask.jsonify(seconds_elapsed=elapsed_time,
                             committed_time=commit_time,
                             is_recording=is_recording)
    except Exception, e:
        log.error(str(e))
        return flask.jsonify(error=str(e))

@app.route("/get_record_status")
def get_record_status():
    """
    Returns the status of the recording, including elapsed time, whether
    a recording is happending, and what the commit time is set to.
    """
    
    try:
        log.debug("called /get_record_status")
        commit_time, elapsed_time, is_recording = recorder_obj.get_status()
        
        if commit_time == None:
            commit_time = 0
        if elapsed_time == None:
            elapsed_time = 0
            
        return flask.jsonify(seconds_elapsed=elapsed_time,
                             committed_time=commit_time,
                             is_recording=is_recording)
    except Exception, e:
        log.error(str(e))
        return flask.jsonify(error=str(e))

@app.route("/commit_time/<int:t>")
def commit_time(t):
    """
    Sets the current global video start time that gets transmitted to
    all clients.
    """

    log.debug("called /commit_time/%d" % t)

    try:
        recorder_obj.commit_time(t)
        return flask.jsonify()
    except Exception, e:
        log.error(str(e))
        return flask.jsonify(error=str(e))

@app.route("/play_preview/<int:start_time>")
@app.route("/play_preview/<int:start_time>/<int:duration>")
def play_preview(start_time, duration=30):
    """
    RTPPlay duration seconds of the current dump starting at time start_time.
    """

    log.debug("called /play_preview/%d/%d" % (start_time, duration))

    try:
        recorder_obj.play_preview(start_time, duration)
        return flask.jsonify()
    except Exception, e:
        log.error(str(e))
        return flask.jsonify(error=str(e))

if __name__ == "__main__":
    app.secret_key = "replace me!"
    app.run(host="0.0.0.0", port=5081, debug=True)
