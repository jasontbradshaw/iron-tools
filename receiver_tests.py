import unittest
import time
import rtp
from receiver import *
from it_exceptions import *

class ReceiverTests(unittest.TestCase):
    def no_side_effects(self):
        self.r.file_exists = lambda f : True
        self.r.file_getsize = lambda f : 1

    def setUp(self):
        self.r = Receiver()
        self.r.rtpplay = rtp.RTPPlayEmulator()
    
    def tearDown(self):
        pass

    def testGetStatus(self):
        armed_file, is_playing = self.r.get_status()
        assert armed_file is None
        assert not is_playing

    def testGetFileList(self):
        self.no_side_effects()
        self.r.listdir = lambda dump_dir : ["first", "second"]
        self.r._load_commit_time = lambda filename: 333

        result_files = self.r.get_file_list()
        assert result_files[0] == ("first", 333, 1)
        assert result_files[1] == ("second", 333, 1)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(ReceiverTests)
    unittest.TextTestRunner(verbosity=2).run(suite)
