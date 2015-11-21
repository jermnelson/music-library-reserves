__author__="Ximena Buller Machado, Jeremy Nelson"
__license__="GNU AFFEROv3"

import argparse
import datetime
import configparser
import falcon
import json
import logging
import re
import rdflib
import requests
from werkzeug.serving import run_simple

try:
    from .instance import config
except (ImportError, SystemError):
    try:
        from instance import config
    except (ImportError, SystemError):
        config = dict()

URL_CHECK_RE = re.compile(
    r'^(?:http|ftp)s?://' # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' # domain...
    r'localhost|' # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|' # ...or ipv4
    r'\[?[A-F0-9]*:[A-F0-9:]+\]?)' # ...or ipv6
    r'(?::\d+)?' # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

app = falcon.API()

# Namespaces
BF = rdflib.Namespace("http://bibframe.org/vocab/")
SCHEMA = rdflib.Namespace('https://schema.org/')
XSD = rdflib.Namespace('http://www.w3.org/2001/XMLSchema#')

REPOSITORY_URL = "http://{}:{}/{}".format(
    config.TOMCAT.get("host", "localhost"),
    config.TOMCAT.get("port", 8080),
    config.FEDORA.get("path", "fedora/rest"))

TRIPLESTORE_URL = "http://{}:{}/{}".format(
    config.BLAZEGRAPH.get("host", "localhost"),
    config.TOMCAT.get("port", 8080),
    config.BLAZEGRAPH.get("path", "bigdata"))

# SPARQL Templates
PREFIX = """PREFIX bf: <{}>
PREFIX rdf: <{}>
PREFIX rdfs: <{}>
PREFIX schema: <{}>
PREFIX xsd: <{}>""".format(
    BF, 
    rdflib.RDF, 
    rdflib.RDFS,
    SCHEMA,
    XSD)	

GET_CLASS_SPARQL = """{}
SELECT DISTINCT ?subject ?name 
WHERE {{{{
 ?subject rdf:type schema:{{}} .
 ?subject schema:name ?name .  
}}}}""".format(PREFIX)

GET_RDFS_LABEL = """{}
SELECT DISTINCT ?label 
WHERE {{{{
  <{{}}> rdfs:label ?label .
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

def add_schema(graph, uri, items):
    for schema_field, value in items:
        if schema_field.endswith("[]"):
            schema_field = schema_field[:-2]
        predicate = rdflib.URIRef(schema_field)
        if type(value) is list:
            for row in value:
                object_ = uri_or_literal(row)
            graph.add((uri, predicate, object_))
        else:
            object_ = uri_or_literal(row)
            graph.add((uri, predicate, object_))



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

def uri_or_literal(value):
    if URL_CHECK_RE.search(value):
        return rdflib.URIRef(value)
    else:
        return rdflib.Literal(value)


class RepositoryUpstreamError(falcon.HTTPBadGateway):

    def __init__(self, title, description, **kwargs):
        super(RepositoryError, self).__init__(
            title, description, 300, **kwargs)



class BaseObject(object):


    def __create__(self, **kwargs):
        uri_response = requests.post(REPOSITORY_URL)
        if uri_response.status_code > 399:
            raise RepositoryUpstreamError(
                "Failed to create object. Repository Error code {}".format(
                    uri_response.status_code),
                "{} Error\n{}".format(REPOSITORY_URL,
                                      uri_response.text))
        url = uri_response.text
        uri = rdflib.URIRef(url)
        graph = default_graph()
        graph.parse(uri_response.text)
        type_of = kwargs.pop('type')
        if check_name(kwargs.get('https://schema.org/name', None), type_of[0]):
            return
        if 'redirect' in kwargs:
            kwargs.pop('redirect')
        for row in type_of:
            graph.add((uri, rdflib.RDF.type, getattr(SCHEMA, row))) 
        add_schema(graph, uri, kwargs.items())
        update_response = requests.put(
            url,
            data=graph.serialize(format='turtle'),
            headers={"Content-Type": "text/turtle"})
        if update_response.status_code > 399:
            raise RepositoryUpstreamError(
                 "Failed to update {}. Repository Error Code {}".format(
                     url,
                     update_response.status_code),
                 "{} Error\n{}".format(
                      REPOSITORY_URL,
                      update_response.text))
          
        return url

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
        super(EducationalEvents, self).__init__("EducationalEvent")



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

    def __create__(self, **kwargs):
        if not 'binary' in kwargs:
            raise falcon.HTTPMissingParam("binary")
        binary = kwargs.pop('binary')
        music_rec_response = requests.post(
            REPOSITORY_URL,
            data=binary,
            headers={"Content-type": "audio/mpeg"})
        if music_rec_response.status_code > 399:
             raise RepositoryUpstreamError(
                "Failed to create object. Repository Error code {}".format(
                    music_rec_response.status_code),
                "{} Error\n{}".format(REPOSITORY_URL,
                                       music_rec_response))
        music_rec_url = music_rec_response.text
        music_rec_meta_url = "{}/{}".format(music_rec_url, "fcr:metadata")
        music_rec_iri = rdflib.URIRef(music_rec_meta_url)
        graph = default_graph()
        graph.parse(music_rec_meta_url)
        type_of = kwargs.pop('type')
        if check_name(kwargs.get('https://schema.org/name', None), type_of[0]):
            return
        add_schema(graph, music_rec_iri, kwargs.items())
        update_response = requests.put(
            music_rec_meta_url,
            data=graph.serialize(format='turtle'),
            headers={"Content-Type": "text/turtle"})
        print("Update Response {} Text {}".format(update_response.status_code, update_response.text))
        if update_response.status_code > 399:
            raise RepositoryUpstreamError(
                 "Failed to update {}. Repository Error Code {}".format(
                     music_rec_meta_url,
                     update_response.status_code),
                 "{} Error\n{}".format(
                      REPOSITORY_URL,
                      update_response.text))
        return music_rec_meta_url


       

            
        
       

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
    debug = (args.debug or False) 
    host = (args.host or "localhost")
    port = (args.port or 8787)
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
    
    #from werkzeug.serving import run_simple
    #run_simple(
    #    '0.0.0.0',
    #    8756,
    #    app,
    #    use_reloader=False)
