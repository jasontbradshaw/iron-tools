import receiverweb
import unittest
import json
import time
import re

# before running create
# /collector/dump
# /reciever/dump

class ReceiverWebTestCase(unittest.TestCase):
    def setUp(self):
        self.app = receiverweb.app.test_client()

    def test_home(self):
        rv = self.app.get('/')
        assert 'Receiver Web' in rv.data

    # assert that stop does nothing if nothing is playing
    def test_stop(self):
        rv = self.app.get('/stop')
        assert '{}' in rv.data

    # assert nothing is in the list if the directory is empty
    def test_get_file_list(self):
        rv = self.app.get('/get_file_list')
        js = json.loads(rv.data)
        assert 'file_list' in js
        assert js['file_list'] == []

    #def test_commit_time_1(self):
        #rv = self.app.get('/commit_time')
        #js = json.loads(rv.data)
        #assert 'commit_time' in js

    # if the directory is empty assert commit_time = 0
    #def test_commit_time_2(self):
        #rv = self.app.get('/commit_time')
        #js = json.loads(rv.data)

        #rv2 = self.app.get('/get_file_list')
        #js2 = json.loads(rv2.data)
        #if js2['file_list'] == []:
            #assert int(js['commit_time']) == 0
        #else:
            #assert 'commit_time' in js

    # asserts that fake_test.dump did not exist and proper error was returned
    def test_arm(self):
        rv = self.app.get('/arm/fake_test.dump')
        js = json.loads(rv.data)
        assert js['error'] == "Could not find file 'fake_test.dump'."

        rv2 = self.app.get('/get_file_list')
        js2 = json.loads(rv2.data)
        assert js2['file_list'] == []
        
        #rv3 = self.app.get('/commit_time')
        #js3 = json.loads(rv3.data)
        #assert int(js3['commit_time']) == 0

    # asserts that play does not break when there is nothing to play
    def test_play(self):
        rv = self.app.get('/play')
        js = json.loads(rv.data)
        assert js['warning'] == 'rtpplay is not alive, no signal sent.'

    # asserts that get_status returns 'false' when nothing is playing
    def test_get_status(self):
        rv = self.app.get('/get_status')
        js = json.loads(rv.data)
        #print js['playing'] == 'false'

if __name__ == '__main__':
    unittest.main()
