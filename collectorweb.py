import flask
import time

from flask import Flask
from flask import g

import util

app = Flask(__name__)
glob = util.ThreadedDataStore()

@app.route("/")
def hello():
    return "Collector Web"

@app.route("/start_record")
def start_record():
    # save the time we started recording for permanence
    with glob:
        glob["start_time"] = time.time()
        
        # make the time prettier
        string_time = time.asctime(time.localtime(glob["start_time"]))
        
        return "Start time is set to: %s" % string_time

@app.route("/stop_record")
def stop_record():
    raise NotImplementedError("Method not implemented yet.")

@app.route("/get_elapsed_time")
def get_elapsed_time():
    with glob:
        if "start_time" in glob:
            elapsed_time = time.time() - glob["start_time"]
        else:
            return "No start time has been specified."
    
    return "%d seconds have elapsed." % elapsed_time

@app.route("/commit_time/<int:t>")
def commit_time(t):
    with glob:
        glob["commit_time"] = t
        return "Commit time set to: %d seconds" % glob["commit_time"]

@app.route("/get_commit_time")
def get_commit_time():
    with glob:
        if "commit_time" in glob:
            return "Last commit time: %d seconds" % glob["commit_time"]
        else:
            return "No commit time has been specified yet."

if __name__ == "__main__":
    app.secret_key = "replace me!"
    app.run(debug = True)

