#!/usr/bin/env python

import flask
from flask import Flask
from flask import flash

import util

"""
--WHITEBOARD--
get_file_list -> json[]
play_file(file_name)
get_status -> json
"""

app = Flask(__name__)
glob = util.ThreadedDataStore()

@app.route("/")
def hello():
    return "Receiver Web"

@app.route("/get_file_list")
def get_file_list():
    return None

@app.route("/play_file")
def play_file(file_name):
    return None

@app.route("/get_status")
def get_status():
    return None

if __name__ == "__main__":
    app.run(debug = True)
