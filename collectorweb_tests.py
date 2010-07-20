import collectorweb
import unittest
import json
import time

class CollectorWebTests(unittest.TestCase):

    def setUp(self):
        self.app = collectorweb.app.test_client()

    def tearDown(self):
        del self.app

    #asserts starting conditions are correct
    def test0A_root(self):
        rv = self.app.get('/')
        assert '/static/collector/index.html' in rv.data
        
    def test0B_stop(self):
        rv = self.app.get('/stop_record')
        js = json.loads(rv.data)
        assert js['seconds_elapsed'] == 0
        assert js['committed_time'] == 0
        assert js['is_recording'] == False   


    """#assert start record prevents double starting
    def test0C_record(self):
        rv = self.app.get('/start_record')
        assert '{}' in rv.data

        rv = self.app.get('/start_record')
        js = json.loads(rv.data)
        print js 
        for x in js:
            print x + "   " + js[x]
        assert js['warning'] == "rtpdump already running. 

    #asserts the time is being tracked properly
    def test0D_elapsed_time(self):
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
        assert 3 <= t2 - t1 <= 4    # close enough"""

    
    def test0E_commit_nostart(self):
        rv = self.app.get('/commit_time/0')
        js = json.loads(rv.data)
        assert "error" in js
    
    """def test0F_commit_basic(self):
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
        assert int(js['committed_time']) == 98765"""
        
    
    #assert play preview funtions properly with nzp values
    def test0G_play_preview_initial(self):
        rv = self.app.get('/play_preview/30')
        js = json.loads(rv.data)
        assert 'error' in js
        assert js['error'] == "no recording started, unable to preview."


    #assert play preview funtions properly with nzp values
    def test0H_play_preview_param(self):
        self.app.get('/start_record')

        rv = self.app.get('/play_preview/10')
        assert '{}' in rv.data

        rv = self.app.get('/play_preview/13371377')
        assert '{}' in rv.data

        rv = self.app.get('/play_preview/10/10')
        assert '{}' in rv.data
    
if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(CollectorWebTests)
    unittest.TextTestRunner(verbosity=2).run(suite)
