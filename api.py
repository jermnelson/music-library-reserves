__author__="Ximena Buller Machado, Jeremy Nelson"
__license__="GNU AFFEROv3"

import argparse
import datetime
import configparser
import falcon
import json
import logging
import rdflib
import requests
from werkzeug.serving import run_simple

try:
    from .lib.semantic_server.repository import URL_CHECK_RE
    from .lib.semantic_server.repository.resources.fedora import Resource
except (ImportError, SystemError):
    from lib.semantic_server.repository import URL_CHECK_RE
    from lib.semantic_server.repository.resources.fedora import Resource

try:
    from .instance import config
except (ImportError, SystemError):
    try:
        from instance import config
    except (ImportError, SystemError):
        config = dict()

app = falcon.API()

# Create a CONFIG for Semantic Server API calls based on application's
# instance/config.py values.
CONFIG = configparser.ConfigParser()
if hasattr(config, "DEFAULT"):
    CONFIG.read_dict(config.DEFAULT)
else:
    CONFIG.read_string(
    """[DEFAULT]\nhost = localhost\nport = 8756\ndebug = True""")
if hasattr(config, "TOMCAT"):
    CONFIG.read_dict(config.TOMCAT)
else:
    CONFIG.add_section("TOMCAT")
    CONFIG.set("TOMCAT", "port", "8080")
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
if hasattr(config, "LIBRARY"):
    CONFIG.read_dict(config.LIBRARY)
else:
    CONFIG.add_section("LIBRARY")
    CONFIG.set("LIBRARY", "url", "http://www.coloradocollege.edu/library/seay/")

# Namespaces
BF = rdflib.Namespace("http://bibframe.org/vocab/")
SCHEMA = rdflib.Namespace('http://schema.org/')
XSD = rdflib.Namespace('http://www.w3.org/2001/XMLSchema#')

# SPARQL Templates
TRIPLESTORE_URL = "http://{}:{}/{}".format(
    CONFIG.get("BLAZEGRAPH", "host"),
    CONFIG.get("TOMCAT", "port"),
    CONFIG.get("BLAZEGRAPH", "path"))

PREFIX = """PREFIX bf: <{}>
PREFIX rdf: <{}>
PREFIX schema: <{}>
PREFIX xsd: <{}>""".format(
    BF, 
    rdflib.RDF, 
    SCHEMA,
    XSD)	

GET_CLASS_SPARQL = """{}
SELECT DISTINCT ?subject ?name 
WHERE {{{{
 ?subject rdf:type schema:{{}} .
 ?subject schema:name ?name .  
}}}}""".format(PREFIX)

EXISTS_NAME = """{}
SELECT DISTINCT ?subject 
WHERE {{{{
  ?subject schema:name "{{}}"^^xsd:string .
  ?subject rdf:type schema:{{}} .
}}}}""".format(PREFIX)


# Helper functions
def default_graph():
    graph = rdflib.Graph()
    graph.namespace_manager.bind('bf', BF)
    graph.namespace_manager.bind('rdf', rdflib.RDF)
    graph.namespace_manager.bind('schema', SCHEMA)
    graph.namespace_manager.bind('owl', rdflib.OWL)
    return graph


def tmp_uri():
    return rdflib.URIRef("{}/{}".format(
        CONFIG.get("LIBRARY", "url"), 
        datetime.datetime.utcnow().timestamp()))


def check_name(name, type_of):
    if type(name) == list:
        name = name[0]
    sparql = EXISTS_NAME.format(name, type_of)
    result = requests.post(
        TRIPLESTORE_URL+"/sparql",
        data={"query": sparql,
                  "format": "json"})
    if result.status_code < 400:
        print(sparql, result.json())
        if len(result.json().get('results').get('bindings')) > 0:
            return True
    return False


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
        if check_name(kwargs.get('http://schema.org/name', None), type_of[0]):
            return
        if 'redirect' in kwargs:
            kwargs.pop('redirect')
        binary=None
        if 'binary' in kwargs:
            binary = kwargs.pop('binary')
        for row in type_of:
            graph.add((uri, rdflib.RDF.type, getattr(SCHEMA, row))) 
        for schema_field, value in kwargs.items():
            if schema_field.endswith("[]"):
                schema_field = schema_field[:-2]
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

    def __build_fedora_uri__(self, uuid):
        path = uuid.split("-")[0]
        full_path = "http://{}:{}/{}/".format(
            CONFIG.get('TOMCAT', 'host'),
            CONFIG.get('TOMCAT', 'port'),
            CONFIG.get('FEDORA', 'path'))
        for i, char in enumerate(path):
            full_path += char
            if i%2:
                full_path += "/"
        full_path += "{}".format(uuid)
        return full_path

    def __get_triples__(self, uuid, properties):
        fedora_uri = self.__build_fedora_uri__(uuid)
        sparql = "{}\nSELECT DISTINCT ".format(PREFIX)
        sparql += ' '.join(["?o{}".format(i) for i in range(len(properties))])
        sparql += "\nWHERE {\n"
        for i, predicate in enumerate(properties):
            sparql += "<{}> <{}> ?o{} .\n".format(fedora_uri, predicate, i)
        sparql = sparql[:-2]
        sparql += "\n}"
        print(TRIPLESTORE_URL)
        result = requests.post(TRIPLESTORE_URL+"/sparql",
            data={"query": sparql,
                  "format": "json"})
        if result.status_code <= 399:
            bindings = result.json().get('results').get('bindings')
            return json.dumps(bindings)
            

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

    def on_get(self, req, resp):
        resp.body = self.__get_partition__(req.args.get('count', 0))
        resp.status = falcon.HTTP_200


class AudioObject(BaseObject):

    def on_get(self, req, resp, uid):
        resp.body = '{"message": "AudioObject"}'
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp):
        resp.body = '{"message": "Created AudioObject"}'
        resp.status = falcon.HTTP_201

class AudioObjects(PluralObject):

    def __init__(self):
        super(AudioObjects, self).__init__('AudioObject')

    def on_get(self, req, resp):
        resp.body = self.__get_partition__(req.params.get('count', 0))
        resp.status = falcon.HTTP_200


class EducationalEvent(BaseObject):

    def on_get(self, req, resp):
        
        __build_fedora_uri__
        resp.body = '{"message": "EducationEvent"}'
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp):
        resp.body = '{"message": "Created EducationEvent"}'
        resp.status = falcon.HTTP_201


class EducationalEvents(PluralObject):

    def __init__(self):
        super(EducationalEvents, self).__init__("EducationalEvents")



class MusicPlaylist(BaseObject):

    def on_get(self, req, resp, uid):
        resp.body = self.__get_triples__(
            uid, 
            [SCHEMA.isPartOf, SCHEMA.name, SCHEMA.track])
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp):
        resp.body = '{"message": "Created MusicPlaylist"}'
        resp.status = falcon.HTTP_201

class MusicPlaylists(PluralObject):

    def __init__(self):
        super(MusicPlaylists, self).__init__("MusicPlaylist")


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

   

app.add_route("/AudioObjects", AudioObjects())
app.add_route("/AudioObject/{uid}", AudioObject())
app.add_route("/MusicGroup", MusicGroup())
app.add_route("/MusicRecordings", MusicRecordings())
app.add_route("/MusicRecording/{uid}", MusicRecording())
app.add_route("/MusicPlaylists", MusicPlaylists())
app.add_route("/MusicPlaylists/{uid}", MusicPlaylist())
app.add_route("/Persons", Persons())
app.add_route("/Persons/{uid}", Person()) 

def main(args):
    debug = args.debug or CONFIG.getboolean('DEFAULT', 'debug') 
    host = args.host or CONFIG.get('DEFAULT', 'host')
    port = args.port or CONFIG.getint('DEFAULT', 'port')
    logging.basicConfig(
        filename='errors.log',
        format='%(asctime)-15s %(message)s',
        level=logging.ERROR)
    print("Starting Music Library Reserves API\n\turl={}:{}\n\tDebug={}".format(
       host, port, debug)) 
    run_simple(host, port, app, use_reloader=debug)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--host', 
        help='Host for Music Library Reserves API, defaults to localhost')
    parser.add_argument(
        '--port',
        help='Port for Music Library Reserves API, defaults to 8756')
    parser.add_argument(
        '--debug',
        help='Debug mode for Music Library Reserves API')
    args = parser.parse_args()
    main(args)
    
if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple(
        '0.0.0.0',
        8756,
        app,
        use_reloader=False)
