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

    def test_test(self):
        rv = self.app.get('/')
        assert 'Receiver Web' in rv.data

if __name__ == '__main__':
    unittest.main()
