__author__ = "Jeremy Nelson"

import argparse
import datetime
import rdflib
from flask import Flask, render_template, session, url_for
from flask import abort, escape, redirect, request
try:
    from simplepam import authenticate
except ImportError:
    def authenticate(username, password):
        return True

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')


# Namespaces
SCHEMA = rdflib.Namespace('http://schema.org/')

# SPARQL Templates

# Helper functions
def default_graph():
    graph = rdflib.Graph()
    graph.namespace_manager.bind('rdf', rdflib.RDF)
    graph.namespace_manager.bind('schema', SCHEMA)
    graph.namespace_manager.bind('owl', rdflib.OWL)
    return graph


def tmp_uri():
    return rdflib.URIRef("{}/{}".format(
        app.config.get(LIBRARY_URL), 
        datetime.datetime.utcnow().timestamp()))
                                  

# Routes
@app.route("/")
def index():
    return render_template(
        "index.html", 
        today=datetime.datetime.utcnow(),
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

