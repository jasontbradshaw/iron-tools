import recorder_web
import unittest
import json
import time
import util

class RecorderWebTests(unittest.TestCase):

    def setUp(self):
        self.app = recorder_web.app.test_client()

    def test_2_stop(self):
        """
        See if stopping a playback had the desired effects.
        """
        
        rv = self.app.get('/stop_record')
        js = json.loads(rv.data)
        assert js['seconds_elapsed'] == 0
        assert js['committed_time'] == 0
        assert js['is_recording'] == False   
    
    def test_3_record(self):
        """
        Try to start something twice.
        """
        
        rv = self.app.get('/start_record')
        js = json.loads(rv.data)
        assert 'error' in js

    def test_4_elapsed_time(self):
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
    
    def test_5_commit_nostart(self):
        """
        Make sure we can't commit a time until at least one recordin has
        been started.
        """
        
        rv = self.app.get('/commit_time/0')
        js = json.loads(rv.data)
        for x in js:
            print x
        print len(js)
        #assert "error" in js
    
    def test_6_commit_basic(self):
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
        
    def test_8_stop_end_state(self):
        """
        Checks the changes to the record status caused by /stop_record
        """
        
        self.app.get('/start_record')
        time.sleep(1)
        rv = self.app.get('/stop_record')
        js = json.loads(rv.data)
        assert js['committed_time'] != 0
        assert js['is_recording'] == false

        rv = self.app.get('/get_record_status')
        js = json.loads(rv.data)
        assert js['committed_time'] == 0

    def test_9_start_state_change(self):
        """
        Checks that start_record changes status correctly
        """

        self.app.get('/start_record')
        rv = self.app.get('/get_record_status')
        js = json.loads(rv.data)
        assert js['committed_time'] == 0

        self.app.get('/commit_time/5')
        rv = self.app.get('/get_record_status')
        js = json.loads(rv.data)
        assert js['committed_time'] == 5

        self.app.get('/start_record')
        rv = self.app.get('/get_record_status')
        js = json.loads(rv.data)
        assert js['committed_time'] == 0


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(RecorderWebTests)
    unittest.TextTestRunner(verbosity=2).run(suite)
