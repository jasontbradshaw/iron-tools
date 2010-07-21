import collectorweb
import unittest
import json
import time
import util

class CollectorWebTests(unittest.TestCase):

    def setUp(self):
        self.app = collectorweb.app.test_client()

    def tearDown(self):
        """
        We have to basically manually reset state of the app here.  For
        whatever reason, it persists between tests, and to ensure we get
        a blank slate for every test, we have to wipe it ourselves.
        """
        
        # kill rtp* processes
        collectorweb.rtpdump.stop()
        collectorweb.rtpplay.stop()
        
        # replace data store with a new one (clears all state)
        collectorweb.glob = util.ThreadedDataStore()
    
    def test_root(self):
        """
        Asserts starting conditions are correct.
        """
        
        rv = self.app.get('/')
        assert '/static/collector/index.html' in rv.data
        
    def test_stop(self):
        """
        See if stopping a playback had the desired effects.
        """
        
        rv = self.app.get('/stop_record')
        js = json.loads(rv.data)
        assert js['seconds_elapsed'] == 0
        assert js['committed_time'] == 0
        assert js['is_recording'] == False   
    
    def test_record(self):
        """
        Try to start something twice.
        """
        
        rv = self.app.get('/start_record')
        assert '{}' in rv.data

        rv = self.app.get('/start_record')
        js = json.loads(rv.data)
        assert js['warning'] == "rtpdump already running."

    def test_elapsed_time(self):
        """
        Make sure elapsed time is being tracked properly.
        """
        
        rv = self.app.get('/get_record_status')
        js = json.loads(rv.data)
        assert js['seconds_elapsed'] == 0
        
        rv = self.app.get('/start_record')
        assert '{}' in rv.data
        
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
    
    def test_commit_nostart(self):
        """
        Make sure we can't commit a time until at least one recordin has
        been started.
        """
        
        rv = self.app.get('/commit_time/0')
        js = json.loads(rv.data)
        assert "error" in js
    
    def test_commit_basic(self):
        """
        Does committing a time work?
        """
        
        self.app.get("/start_record")
        self.app.get("/stop_record")
        
        rv = self.app.get('/get_record_status')
        js = json.loads(rv.data)
        assert 'committed_time' in js
        assert js['committed_time'] == 0
        
        rv = self.app.get('/commit_time/98765')
        assert '{}' in rv.data
        
        rv = self.app.get('/get_record_status')
        js = json.loads(rv.data)
        assert 'committed_time' in js
        assert int(js['committed_time']) == 98765
        
    def test_play_preview_initial(self):
        """
        Try various NZP commit time values.
        """
        
        rv = self.app.get('/play_preview/30')
        js = json.loads(rv.data)
        assert 'error' in js
        assert js['error'] == "no recording started, unable to preview."

    def test_play_preview_param(self):
        """
        Does playing a preview with any parameter work?
        """
        
        self.app.get('/start_record')
        time.sleep(3)
        rv = self.app.get('/stop_record')
        js = json.loads(rv.data)
        
if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(CollectorWebTests)
    unittest.TextTestRunner(verbosity=2).run(suite)
