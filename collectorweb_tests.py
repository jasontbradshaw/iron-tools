import collectorweb
import unittest
import json
import time

# before running create
# /collector/dump
# /receiver/dump

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

    def test_stop_record(self):
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
        rv = self.app.get('/elapsed_time')
        assert '0' in rv.data
        js = json.loads(rv.data)
        assert 'elapsed_time' in js

        rv = self.app.get('/start_record')
        assert '{}' in rv.data

        rv = self.app.get('/elapsed_time')
        js = json.loads(rv.data)
        assert 'elapsed_time' in js
        t1 = int(js['elapsed_time'])

        time.sleep(3)

        rv = self.app.get('/elapsed_time')
        js = json.loads(rv.data)
        assert 'elapsed_time' in js
        t2 = int(js['elapsed_time'])
        assert 3 <= t2 - t1 <= 4    # close enough

    def test_commit(self):
        rv = self.app.get('/commit_time')
        js = json.loads(rv.data)
        assert 'commit_time' in js
        assert js['commit_time'] == 0

        rv = self.app.get('/commit_time/0')
        assert '{}' in rv.data

        rv = self.app.get('/commit_time')
        js = json.loads(rv.data)
        assert 'commit_time' in js
        assert int(js['commit_time']) == 0

        rv = self.app.get('/commit_time/98765')
        assert '{}' in rv.data

        rv = self.app.get('/commit_time')
        js = json.loads(rv.data)
        assert 'commit_time' in js
        assert int(js['commit_time']) == 98765

if __name__ == '__main__':
    unittest.main()
