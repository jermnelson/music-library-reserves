__author__ = "Jeremy Nelson"

import argparse
import datetime
import rdflib
from flask import Flask, render_template, session, url_for
from flask import abort, escape, jsonify, redirect, request
from api import *
try:
    from simplepam import authenticate
except ImportError:
    def authenticate(username, password):
        return True

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')


# Routes
@app.route("/")
def index():
    return render_template(
        "index.html", 
        today=datetime.datetime.utcnow(),
        organizations=Organizations().__get_partition__(),
        persons=Persons().__get_partition__(),
        tracks=MusicRecordings().__get_partition__(),
        user=session.get('username', None))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get('username', None)
        password = request.form.get('password', None)
        print("Before authenticate {} {}".format(username, password))
        if authenticate(str(username), str(password)):
            session['username'] = username
            return redirect(url_for("index"))
        else:
            abort(403)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route("/create", methods=["POST"])
def create():
    if not 'username' in session:
        return redirect(url_for("login"))
    object_type = request.form.get('type')
    info = dict()
    info.update(request.form)
    if object_type.startswith("MusicRecording"):
        new_object = MusicRecording()
    elif object_type.startswith("MusicPlaylist"):
        new_object = MusicPlaylist()
    elif object_type.startswith("Person"):
        new_object = Person()
    elif object_type.startswith("Organization"):
        new_object = Organization()
    else:
        abort(404)
    music_file =  request.files.get('music-file', None)
    if music_file:
        info['file'] = music_file
    url = new_object.__create__(**info) 
    return jsonify({"url": url})

    
@app.route("/delete", methods=["POST"])
def delete():
    if not 'username' in session:
        return redirect(url_for("login"))


@app.route("/update", methods=["POST"])
def update():
    if not 'username' in session:
        return redirect(url_for("login"))
     
    

@app.route("/<token>")
def stream(token):
    print("Streaming Token is {}".format(token))
    return "Not implemented"


# Main handler
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'action',
        choices=['run'],
        help='Action choices: run')
    args = parser.parse_args()
    if args.action.startswith('run'):
        print("Running application in debug mode")
        app.run(host='localhost', port=20156, debug=True) 

