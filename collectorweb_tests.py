import collectorweb
import unittest
import json

class CollectorWebTestCase(unittest.TestCase):
    def setUp(self):
        self.app = collectorweb.app.test_client()

    def tearDown(self):
        pass

    def test_start_record(self):
        rv = self.app.get('/start_record')
        assert '500' not in rv.data

        # stop_record with no rtpdump running should return '{}'
        rv = self.app.get('/stop_record')
        assert '500' not in rv.data
        assert '{}' in rv.data
        js = json.loads(rv.data)
        assert len(js) == 0

        # a successful rtpdump start returns '{}'
        rv = self.app.get('/start_record')
        assert '500' not in rv.data
        assert '{}' in rv.data
        js = json.loads(rv.data)
        assert len(js) == 0

        rv = self.app.get('/start_record')
        assert '500' not in rv.data
        js = json.loads(rv.data)
        assert js['warning'] == 'rtpplay already running.'

        rv = self.app.get('/stop_record')
        js = json.loads(rv.data)
        assert rv.data == '{}'
        assert len(js) == 0

if __name__ == '__main__':
    unittest.main()
