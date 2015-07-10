__author__="Ximena Buller Machado, Jeremy Nelson"
__license__="GNU AFFEROv3"

import falcon

class AudioObject(object):

    def on_get(self, req, resp):
        resp.body = '{"message": "AudioObject"}'
        resp.status = falcon.HTTP_200

class MusicPlaylist(object):

    def on_get(self, req, resp):
        resp.body = '{"message": "MusicPlaylist"}'
        resp.status = falcon.HTTP_200

class MusicRecording (object):

    def on_get(self, req, resp):
        resp.body = '{"message": "MusicRecording"}'
        resp.status = falcon.HTTP_200

class MusicGroup(object):
    
     def on_get(self, req, resp):
        resp.body = '{"message": "MusicGroup"}'
        resp.status = falcon.HTTP_200
        
        


    
