#!/usr/bin/env python

import flask
from flask import Flask
from flask import flash

import util

app = Flask(__name__)
glob = util.ThreadedDataStore()

@app.route("/")
def hello():
    return "Receiver Web"

# create play
@app.route("/play")
def play():
    return None

# Creat stop
@app.route("/stop")
def stop():
    return None

if __name__ == "__main__":
    app.run(debug = True)
