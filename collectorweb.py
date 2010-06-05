#!/usr/bin/env python

import flask
from flask import Flask
from flask import flash

import util
import time

app = Flask(__name__)
glob = util.ThreadedDataStore()

@app.route("/")
def hello():
    return "Collector Web"

@app.route("/start_record")
def start_record():
    # save the time we started recording for permanence
    with glob:
        glob["start_time"] = util.time()
        
        # make the time prettier
        string_time = time.asctime(time.localtime(glob["start_time"]))
        
        flash("Start time is set to: %s" % string_time)
        return flask.jsonify()

@app.route("/stop_record")
def stop_record():
    raise NotImplementedError("Method not implemented yet.")

@app.route("/get_elapsed_time")
def get_elapsed_time():
    with glob:
        if "start_time" in glob:
            elapsed_time = util.time() - glob["start_time"]
        else:
            flash("No start time has been specified.")
            return flask.jsonify(elapsed_time=None)
    
    flash("%d seconds have elapsed." % elapsed_time)
    return flask.jsonify(elapsed_time=elapsed_time)

@app.route("/commit_time/<int:t>")
def commit_time(t):
    with glob:
        glob["commit_time"] = t
        flash("Commit time set to: %d seconds" % glob["commit_time"])
        return flask.jsonify()

@app.route("/get_commit_time")
def get_commit_time():
    with glob:
        if "commit_time" in glob:
            flash("Last commit time: %d seconds" % glob["commit_time"])
            return flask.jsonify(commit_time=glob["commit_time"])
        else:
            flash("No commit time has been specified yet.")
            return flask.jsonify(commit_time=None)

if __name__ == "__main__":
    app.secret_key = "replace me!"
    app.run(debug = True)

