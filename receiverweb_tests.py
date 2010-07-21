import receiverweb
import unittest
import json
import time
import util
import re

class ReceiverWebTests(unittest.TestCase):
    def setUp(self):
        self.app = receiverweb.app.test_client()

    def tearDown(self):
        """
        We have to basically manually reset state of the app here.  For
        whatever reason, it persists between tests, and to ensure we get
        a blank slate for every test, we have to wipe it ourselves.
        """
        
        # kill rtp* processes
        receiverweb.rtpplay.stop()
        
        # replace data store with a new one (clears all state)
        receiverweb.glob = util.ThreadedDataStore()
    
    def test_home(self):
        rv = self.app.get('/')
        assert '/static/receiver/index.html' in rv.data

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

    def test_commit_time(self):
        """
        Loading a 'fake' commit time returns 'None'.
        """
        
        result = receiverweb.load_commit_time('fake_test')
        assert result == None

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
