__author__="Ximena Buller Machado, Jeremy Nelson"
__license__="GNU AFFEROv3"

from api import app, default_graph, AudioObject, tmp_uri
import falcon.testing
import unittest
import rdflib

falcon.testing.create_environ(app=app)

class TestDefaultGraph(unittest.TestCase):

    def test_empty_graph(self):
        default = default_graph()
        self.assertEqual(default.serialize(format='turtle'),
                          b'@prefix owl: <http://www.w3.org/2002/07/owl#> .\n@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n@prefix schema: <http://schema.org/> .\n@prefix xml: <http://www.w3.org/XML/1998/namespace> .\n@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n\n')

class TestTmpURI(unittest.TestCase):

    def test_tmp_uri(self):
        uri = tmp_uri()
        self.assertTrue(str(uri).startswith("http"))
    

class TestBaseObject(unittest.TestCase):

    def test__create__(self):
        

class TestAudioObject(unittest.TestCase):

    def setUp(self):
        self.test_audio_graph = default_graph()


    def test_on_get(self):
        self.assert_(True)

    def test_on_post(self):
        self.assert_(True)

class TestMusicPlaylist(unittest.TestCase):

    def setUp(self):
        self.test_playlist_graph = default_graph()


    def test_on_get(self):
        self.assert_(True)

    def test_on_post(self):
        self.assert_(True)

class TestMusicRecording(unittest.TestCase):

    def setUp(self):
        self.test_recording_graph = default_graph()


    def test_on_get(self):
        self.assert_(True)

    def test_on_post(self):
        self.assert_(True)

class TestMusicGroup(unittest.TestCase):

    def setUp(self):
        self.test_group_graph = default_graph()


    def test_on_get(self):
        self.assert_(True)

    def test_on_post(self):
        self.assert_(True)

class TestPerson(unittest.TestCase):

    def setUp(self):
        self.test_person_graph = default_graph()


    def test_on_get(self):
        self.assert_(True)

    def test_on_post(self):
        self.assert_(True)
        
if __name__ == '__main__':
    unittest.main()



