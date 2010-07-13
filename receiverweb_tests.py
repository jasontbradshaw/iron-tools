import receiverweb
import unittest
import json
import time
import util
import re

class ReceiverWebTests(unittest.TestCase):
    def setUp(self):
        self.app = receiverweb.app.test_client()

    def test1_home(self):
        rv = self.app.get('/')
        assert '/static/receiver/index.html' in rv.data

    # assert that stop does nothing if nothing is playing
    # assert that flags are properly set after stopped
    def test2_stop(self):
        rv = self.app.get('/stop')
        assert '{}' in rv.data
        with receiverweb.glob:
            assert receiverweb.glob['is_playing'] == False
            assert receiverweb.glob['armed_file'] == None

    # assert that get_file_list returns a 'file_list'
    def test3_get_file_list(self):
        rv = self.app.get('/get_file_list')
        js = json.loads(rv.data)
        assert 'file_list' in js

    def test4_commit_time(self):
        result = receiverweb.load_commit_time('fake_test')
        assert result == None

    # asserts that fake_test.dump did not exist and proper error was returned
    def test5_arm(self):
        rv = self.app.get('/arm/fake_test.dump')
        js = json.loads(rv.data)
        assert js['error'] == "could not find file 'fake_test.dump'."

        rv2 = self.app.get('/get_status')
        js2 = json.loads(rv2.data)
        assert js2['file'] == None
        assert js2['is_playing'] == False
 
    # asserts that play does not break when there is nothing to play
    def test6_play(self):
        rv = self.app.get('/play')
        js = json.loads(rv.data)
        assert js['warning'] == 'rtpplay is not alive, no signal sent.'

    # asserts that get_status returns False when nothing is playing
    def test7_get_status(self):
        rv = self.app.get('/get_status')
        js = json.loads(rv.data)
        assert js['file'] == None
        assert js['is_playing'] == False

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(ReceiverWebTests)
    unittest.TextTestRunner(verbosity=2).run(suite)
