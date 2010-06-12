import collectorweb
import unittest
import json
import time

class CollectorWebTestCase(unittest.TestCase):
    def setUp(self):
        self.app = collectorweb.app.test_client()

    def tearDown(self):
        pass

    def test_test(self):
        rv = self.app.get('/')
        assert 'Collector Web' in rv.data
        rv = self.app.get('/stop_record')
        assert '500' not in rv.data

    def test_stop_record1(self):
        rv = self.app.get('/stop_record')
        assert '{}' in rv.data

    def test_record(self):
        rv = self.app.get('/stop_record')
        assert '{}' in rv.data

        rv = self.app.get('/start_record')
        assert '{}' in rv.data

        rv = self.app.get('/start_record')
        assert 'warning' in rv.data
        js = json.loads(rv.data)
        assert 'warning' in js

        rv = self.app.get('/stop_record')
        assert '{}' in rv.data

    def test_elapsed_time(self):
        rv = self.app.get('/get_elapsed_time')
        assert 'null' in rv.data
        js = json.loads(rv.data)
        assert 'elapsed_time' in js

        rv = self.app.get('/start_record')
        assert '{}' in rv.data

        rv = self.app.get('/get_elapsed_time')
        js = json.loads(rv.data)
        assert 'elapsed_time' in js
        t1 = int(js['elapsed_time'])

        time.sleep(3)

        rv = self.app.get('/get_elapsed_time')
        js = json.loads(rv.data)
        assert 'elapsed_time' in js
        t2 = int(js['elapsed_time'])
        assert 3 <= t2 - t1 <= 4    # close enough

if __name__ == '__main__':
    unittest.main()
