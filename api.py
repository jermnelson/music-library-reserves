__author__="Ximena Buller Machado, Jeremy Nelson"
__license__="GNU AFFEROv3"

import datetime
import configparser
import falcon
import rdflib
import requests

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
TRIPLESTORE_URL = "http://{}:{}/{}".format(
    CONFIG.get("BLAZEGRAPH", "host"),
    CONFIG.get("TOMCAT", "port"),
    CONFIG.get("BLAZEGRAPH", "path"))

PREFIX = """PREFIX rdf: <{}>
PREFIX schema: <{}>""".format(rdflib.RDF, SCHEMA)	

GET_CLASS_SPARQL = """{}
SELECT DISTINCT ?subject ?name 
WHERE {{{{
 ?subject rdf:type schema:{{}} .
 ?subject schema:name ?name .  
}}}} LIMIT 100""".format(PREFIX)



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

    def __uri_or_literal__(self, value):
        if URL_CHECK_RE.search(value):
            return rdflib.URIRef(value)
        else:
            return rdflib.Literal(value)


    def __create__(self, **kwargs):
        uri = tmp_uri()
        graph = default_graph()
        type_of = kwargs.pop('type')
        binary=None
        if 'file' in kwargs:
            binary = kwargs.pop('file')
        for row in type_of:
            graph.add((uri, rdflib.RDF.type, getattr(SCHEMA, row))) 
        for schema_field, value in kwargs.items():
            predicate = rdflib.URIRef(schema_field)
            if type(value) is list:
                for row in value:
                    object_ = self.__uri_or_literal__(row)
                    graph.add((uri, predicate, object_))
            else:
                object_ = self.__uri_or_literal__(row)
                graph.add((uri, predicate, object_))
        new_object = Resource(config=CONFIG)
        if binary:
            object_url = new_object.__create__(rdf=graph, binary=binary)
        else:
            object_url = new_object.__create__(rdf=graph)
        return object_url

class PluralObject(object):

    def __init__(self, type_of):
        self.type_of = type_of


    def __get_partition__(self, count=0):
        sparql = GET_CLASS_SPARQL.format(self.type_of)
        result = requests.post(
            TRIPLESTORE_URL+"/sparql",
            data={"query": sparql,
                  "format": "json"})
        if result.status_code < 400:
            return result.json().get('results').get('bindings')

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

class MusicRecordings(PluralObject):

    def __init__(self):
        super(MusicRecordings, self).__init__("MusicRecording")

    def on_get(self, req, resp):
        resp.body = self.__get_partition__(req.args.get('count', 0))
        resp.status = falcon.HTTP_200


class MusicGroup(BaseObject):
    
     def on_get(self, req, resp):
        resp.body = '{"message": "MusicGroup"}'
        resp.status = falcon.HTTP_200

     def on_post(self, req, resp):
        resp.body = '{"message": "Created MusicGroup"}'
        resp.status = falcon.HTTP_201


class Organization(BaseObject):

    def on_get(self, req, resp):
        resp.body = '{"message": "Organization"}'
        resp.status = falcon.HTTP_200


class Organizations(PluralObject):

    def __init__(self):
        super(Organizations, self).__init__("Organization")

    def on_get(self, req, resp):
        resp.body = self.__get_partition__(req.args.get('count', 0))
        resp.status = falcon.HTTP_200


class Person(BaseObject):

    def on_get(self, req, resp):
        resp.body = '{"message": "Person"}'
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp):
        resp.body = '{"message": "Created Person"}'
        resp.status = falcon.HTTP_201

class Persons(PluralObject):

    def __init__(self):
        super(Persons, self).__init__("Person")

   
    def on_get(self, req, resp):
        count = req.args.get('count', 0)
        resp.body = self.__get_partition__(count)
        resp.status = falcon.HTTP_200
 

app.add_route("/AudioObject", AudioObject())
app.add_route("/Person", Person()) 
app.add_route("/Persons", Persons())
app.add_route("/MusicGroup", MusicGroup())
app.add_route("/MusicRecording", MusicRecording())
app.add_route("/MusicPlaylist", MusicPlaylist())
