import receiver_web
import unittest
import json
import time
import util
import re

class ReceiverWebTests(unittest.TestCase):
    def setUp(self):
        self.app = receiver_web.app.test_client()
    
    def tearDown(self):
        pass
        
    def test_home(self):
        rv = self.app.get('/')
        assert '/' in rv.data
    
    def test_stop(self):
        """
        Make sure stop does nothing if nothing is playing.
        """
        
        rv = self.app.get('/stop')
        assert '{}' in rv.data
        
        rv2 = self.app.get('/get_status')
        js2 = json.loads(rv2.data)
        assert js2['file'] == None
        assert js2['is_playing'] == False

    def test_get_file_list(self):
        """
        Make sure getting a file list gives us a file list.
        """
        
        rv = self.app.get('/get_file_list')
        js = json.loads(rv.data)
        assert 'file_list' in js

    def test_arm(self):
        """
        Asserts that fake_test.dump did not exist and proper error was
        returned.
        """
        
        rv = self.app.get('/arm/fake_test.dump')
        js = json.loads(rv.data)
        assert js['error'] == "could not find file 'fake_test.dump'."
        
        rv2 = self.app.get('/get_status')
        js2 = json.loads(rv2.data)
        assert js2['file'] == None
        assert js2['is_playing'] == False
 
    def test_play(self):
        """
        Asserts that play does not break when there is nothing to play.
        """
        
        rv = self.app.get('/play')
        js = json.loads(rv.data)
        assert js['warning'] == 'rtpplay is not alive, no signal sent.'
        
        rv2 = self.app.get('/get_status')
        js2 = json.loads(rv2.data)
        assert js2['file'] == None
        assert js2['is_playing'] == False

    def test_get_status(self):
        """
        Asserts that get_status returns False when nothing is playing.
        """
        
        rv = self.app.get('/get_status')
        js = json.loads(rv.data)
        assert js['file'] == None
        assert js['is_playing'] == False

    def test_play(self):
        """
        Assert the status remains unchanged after play and stop.
        """
        
        rv = self.app.get('/play')
        js = json.loads(rv.data)
        
        rv2 = self.app.get('/get_status')
        js2 = json.loads(rv2.data)
        assert js2['file'] == None
        assert js2['is_playing'] == False
        
        rv = self.app.get('/stop')
        js = json.loads(rv.data)
        
        assert js2['file'] == None
        assert js2['is_playing'] == False

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(ReceiverWebTests)
    unittest.TextTestRunner(verbosity=2).run(suite)
