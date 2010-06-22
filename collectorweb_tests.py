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

		#asserts starting conditions are correct
    def test_01_test(self):
        rv = self.app.get('/')
        assert 'Collector Web' in rv.data
        rv = self.app.get('/stop_record')
				js = json.loads(rv.data)
        assert js['is_recording'] == False
				assert js['seconds_elapsed'] == 0
				assert js['committed_time'] == 0

		#assert start record prevents double starting
    def test_02_record(self):
				self.app.get('/stop_record')

        rv = self.app.get('/start_record')
        assert '{}' in rv.data

        rv = self.app.get('/start_record')
        js = json.loads(rv.data)
        assert js['warning'] == 'rtpdump already running.'

				self.app.get('/stop_record')

		#asserts the time is being tracked properly
    def test_03_elapsed_time(self):
				self.app.get('/stop_record')

        rv = self.app.get('/get_record_status')
        js = json.loads(rv.data)
        assert js['elapsed_time'] == '0'

        rv = self.app.get('/start_record')
        assert '{}' in rv.data

        rv = self.app.get('/get_record_status')
        js = json.loads(rv.data)
        assert 'elapsed_time' in js
        t1 = int(js['elapsed_time'])

        time.sleep(3)

        rv = self.app.get('/get_record_status')
        js = json.loads(rv.data)
        assert 'elapsed_time' in js
        t2 = int(js['elapsed_time'])
        assert 3 <= t2 - t1 <= 4    # close enough

		#
    def test_04_commit(self):
				self.app.get('/stop_record')

        rv = self.app.get('/get_record_status')
        js = json.loads(rv.data)
        assert 'commit_time' in js
        assert js['commit_time'] == 0

        rv = self.app.get('/commit_time/0')
        assert '{}' in rv.data

        rv = self.app.get('/get_record_status')
        js = json.loads(rv.data)
        assert 'commit_time' in js
        assert int(js['commit_time']) == 0

        rv = self.app.get('/commit_time/98765')
        assert '{}' in rv.data

        rv = self.app.get('/get_record_status')
        js = json.loads(rv.data)
        assert 'commit_time' in js
        assert int(js['commit_time']) == 98765

if __name__ == '__main__':
    unittest.main()
