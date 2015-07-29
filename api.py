__author__="Ximena Buller Machado, Jeremy Nelson"
__license__="GNU AFFEROv3"

import datetime
import configparser
import falcon
import rdflib

try:
    from .lib.semantic_server.repository import URL_CHECK_RE
    from .lib.semantic_server.repository.resources.fedora import Resource
    from .instance import config
except (ImportError, SystemError):
    from lib.semantic_server.repository import URL_CHECK_RE
    from lib.semantic_server.repository.resources.fedora import Resource
    from instance import config

app = falcon.API()

# Create a CONFIG for Semantic Server API calls based on application's
# instance/config.py values.
CONFIG = configparser.ConfigParser()
if hasattr(config, "DEFAULT"):
    CONFIG.read_dict(config.DEFAULT)
else:
    CONFIG.read_string("""[DEFAULT]\nhost = localhost\ndebug = True""")
if hasattr(config, "TOMCAT"):
    CONFIG.read_dict(config.TOMCAT)
else:
    CONFIG.add_section("TOMCAT")
    CONFIG.set("TOMCAT", "port", 8080)
if hasattr(config, "FEDORA"):
    CONFIG.read_dict(config.FEDORA)
else:
    CONFIG.add_section("FEDORA")
    CONFIG.set("FEDORA", "path", "fedora")
if hasattr(config, "BLAZEGRAPH"):
    CONFIG.read_dict(config.BLAZEGRAPH)
else:
    CONFIG.add_section("BLAZEGRAPH")
    CONFIG.set("BLAZEGRAPH", "path", "/bigdata")

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
        config.LIBRARY_URL, 
        datetime.datetime.utcnow().timestamp()))


class BaseObject(object):

    def __create__(self, **kwargs):
        uri = tmp_uri()
        graph = default_graph()
        for schema_field, value in kwargs.items():
            predicate = rdflib.URIRef(schema_field)
            if URL_CHECK_RE.search(value):
                object_ = rdflib.URIRef(value)
            else:
                object_ = rdflib.Literal(value)
            graph.add((uri, predicate, object_))
        new_object = Resource(config=CONFIG)
        object_url = new_object.__create__(rdf=graph)
        return object_url


class AudioObject(BaseObject):

    def on_get(self, req, resp):
        resp.body = '{"message": "AudioObject"}'
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp):
        resp.body = '{"message": "Created AudioObject"}'
        resp.status = falcon.HTTP_201


class MusicPlaylist(BaseObject):

    def on_get(self, req, resp):
        resp.body = '{"message": "MusicPlaylist"}'
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp):
        resp.body = '{"message": "Created MusicPlaylist"}'
        resp.status = falcon.HTTP_201


class MusicRecording(BaseObject):

    def on_get(self, req, resp):
        resp.body = '{"message": "MusicRecording"}'
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp):
        resp.body = '{"message": "Created MusicRecording"}'
        resp.status = falcon.HTTP_201


class MusicGroup(BaseObject):
    
     def on_get(self, req, resp):
        resp.body = '{"message": "MusicGroup"}'
        resp.status = falcon.HTTP_200

     def on_post(self, req, resp):
        resp.body = '{"message": "Created MusicGroup"}'
        resp.status = falcon.HTTP_201


class Person(BaseObject):

    def on_get(self, req, resp):
        resp.body = '{"message": "Person"}'
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp):
        resp.body = '{"message": "Created Person"}'
        resp.status = falcon.HTTP_201

app.add_route("/AudioObject", AudioObject())
app.add_route("/Person", Person()) 
app.add_route("/MusicGroup", MusicGroup())
app.add_route("/MusicRecording", MusicRecording())
app.add_route("/MusicPlaylist", MusicPlaylist())
