import flask
from flask import Flask

import time

app = Flask(__name__)

@app.route("/")
def hello():
    return "Collector Web"

@app.route("/start_record")
def start_record():
    # save the time we started recording for permanence
    with open("start_record_time.save", 'w') as f:
        start_time = time.time()
        f.write(start_time)
    
    return "Start time is set to %d." % (start_time,)

@app.route("/stop_record")
def stop_record():
    return "Not implemented."

@app.route("/get_elapsed_time")
def get_elapsed_time():
    elapsed_time = time.time() - flask.session['start_time']
    return "%d time has elapsed" % (elapsed_time,)

@app.route("/commit_time/<int:t>")
def commit_time(t):
    flask.session['commit_time'] = t
    return "Commit time set to %d." % (t,)

@app.route("/get_commit_time")
def get_commit_time():
    if 'commit_time' in flask.session:
        return "Last committed time: %d." % (flask.session['commit_time'],)
    return 'No commit time specified.'

@app.route("/jsontest")
def jsontest():
    return flask.jsonify(username="admin", age=42, sex=["male"])

if __name__ == "__main__":
    app.secret_key = 'super random'
    app.debug = True
    app.run(host="0.0.0.0")

