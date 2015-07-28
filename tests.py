__author__="Ximena Buller Machado, Jeremy Nelson"
__license__="GNU AFFEROv3"

from api import app, AudioObject
import falcon.testing
import unittest
import rdflib

falcon.testing.create_environ(app=app)

class TestAudioObject(unittest.TestCase):

    def setUp(self):
        self.test_audio_graph = rdflib.Graph()


    def test_on_get(self):
        self.assert_(True)

    def test_on_post(self):
        self.assert_(True)

class TestMusicPlaylist(unittest.TestCase):

    def setUp(self):
        self.test_playlist_graph = rdflib.Graph()


    def test_on_get(self):
        self.assert_(True)

    def test_on_post(self):
        self.assert_(True)

class TestMusicRecording(unittest.TestCase):

    def setUp(self):
        self.test_recording_graph = rdflib.Graph()


    def test_on_get(self):
        self.assert_(True)

    def test_on_post(self):
        self.assert_(True)

class TestMusicGroup(unittest.TestCase):

    def setUp(self):
        self.test_group_graph = rdflib.Graph()


    def test_on_get(self):
        self.assert_(True)

    def test_on_post(self):
        self.assert_(True)

class TestPerson(unittest.TestCase):

    def setUp(self):
        self.test_person_graph = rdflib.Graph()


    def test_on_get(self):
        self.assert_(True)

    def test_on_post(self):
        self.assert_(True)
        
if __name__ == '__main__':
    unittest.main()



