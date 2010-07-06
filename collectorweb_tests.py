import collectorweb
import unittest
import json
import time

class CollectorWebTestCase(unittest.TestCase):

    def setUp(self):
        self.app = collectorweb.app.test_client()

    def tearDown(self):
        pass

    #asserts starting conditions are correct
    def test_01_test(self):
        rv = self.app.get('/')
        assert '/static/collector/index.html' in rv.data
        rv = self.app.get('/stop_record')
	js = json.loads(rv.data)
        assert js['seconds_elapsed'] == 0
        assert js['committed_time'] == 0
        assert js['is_recording'] == False

    #assert start record prevents double starting
    def test_02_record(self):
        rv = self.app.get('/start_record')
        with collectorweb.glob:
            assert 'start_time' in collectorweb.glob
            assert collectorweb.glob['commit_time'] == None

        rv = self.app.get('/start_record')
        js = json.loads(rv.data)
        # TODO: this is broken for some unknown reason
        assert js['warning'] == 'rtpdump already running.'

        self.app.get('/stop_record')

    #asserts the time is being tracked properly
    def test_03_elapsed_time(self):       
        rv = self.app.get('/get_record_status')
        js = json.loads(rv.data)
        assert ('elapsed_time' not in rv.data) or (js['elapsed_time'] == '0')

        rv = self.app.get('/start_record')
        with collectorweb.glob:
            assert 'start_time' in collectorweb.glob
            assert collectorweb.glob['commit_time'] == None

        rv = self.app.get('/get_record_status')
        js = json.loads(rv.data)
        assert 'seconds_elapsed' in js
        t1 = int(js['seconds_elapsed'])

        time.sleep(3)

        rv = self.app.get('/get_record_status')
        js = json.loads(rv.data)
        assert 'seconds_elapsed' in js
        t2 = int(js['seconds_elapsed'])
        assert 3 <= t2 - t1 <= 4    # close enough
        
        self.app.get('/stop_record')

    #asserts that commit works correctly for nzp values
    def test_04_commit(self):
        rv = self.app.get('/get_record_status')
        js = json.loads(rv.data)
        assert 'commit_time' in js
        assert js['commit_time'] == 0

        rv = self.app.get('/commit_time/-5')
        js = json.loads(rv.data)
        assert 'error' in js

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

        self.app.get('/stop_record')

    #assert play preview funtions properly with nzp values
    def test_05_play_preview(self):
        rv = self.app.get('/play_preview/30')
        js = json.loads(rv.data)
        assert 'error' in js
        assert js['error'] == "no recording started, unable to preview."

        self.app.get('/start_record')

        rv = self.app.get('/play_preview/-100')
        assert '{}' in rv.data

        rv = self.app.get('/play_preview/0')
        assert '{}' in rv.data

        rv = self.app.get('/play_preview/5')
        assert '{}' in rv.data

        rv = self.app.get('/play_preview/13371337')
        assert '{}' in rv.data

        rv = self.app.get('/play_preview/10/0')
        assert '{}' in rv.data

        rv = self.app.get('/play_preview/0/0')
        assert '{}' in rv.data

        rv = self.app.get('/play_preview/10/-10')
        assert '{}' in rv.data

if __name__ == '__main__':
    unittest.main()
