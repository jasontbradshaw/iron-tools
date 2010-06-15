import receiverweb
import unittest
import json
import time

# before running create
# /collector/dump
# /reciever/dump

class ReceiverWebTestCase(unittest.TestCase):
    def setUp(self):
        self.app = receiverweb.app.test_client()

    def test_home(self):
        rv = self.app.get('/')
        assert 'Receiver Web' in rv.data

    # if there is nothing to stop it should return {}
    def test_stop(self):
        rv = self.app.get('/stop')
        assert '{}' in rv.data

    # even when the directory is empty it will not return {}
    def test_get_file_list(self):
        rv = self.app.get('/get_file_list')
        assert '{}' not in rv.data

if __name__ == '__main__':
    unittest.main()
