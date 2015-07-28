__author__="Ximena Buller Machado, Jeremy Nelson"
__license__="GNU AFFEROv3"

import falcon
import rdflib

app = falcon.API()

class AudioObject(object):

    def on_get(self, req, resp):
        resp.body = '{"message": "AudioObject"}'
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp):
        resp.body = '{"message": "Created AudioObject"}'
        resp.status = falcon.HTTP_201

app.add_route("/AudioObject", AudioObject())

class MusicPlaylist(object):

    def on_get(self, req, resp):
        resp.body = '{"message": "MusicPlaylist"}'
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp):
        resp.body = '{"message": "Created MusicPlaylist"}'
        resp.status = falcon.HTTP_201

app.add_route("/MusicPlaylist", MusicPlaylist())

class MusicRecording (object):

    def on_get(self, req, resp):
        resp.body = '{"message": "MusicRecording"}'
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp):
        resp.body = '{"message": "Created MusicRecording"}'
        resp.status = falcon.HTTP_201

app.add_route("/MusicRecording", MusicRecording())

class MusicGroup(object):
    
     def on_get(self, req, resp):
        resp.body = '{"message": "MusicGroup"}'
        resp.status = falcon.HTTP_200

     def on_post(self, req, resp):
        resp.body = '{"message": "Created MusicGroup"}'
        resp.status = falcon.HTTP_201

app.add_route("/MusicGroup", MusicGroup())

class Person(object):

    def on_get(self, req, resp):
        resp.body = '{"message": "Person"}'
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp):
        resp.body = '{"message": "Created Person"}'
        resp.status = falcon.HTTP_201

app.add_route("/Person", Person()) 
        
        


    
