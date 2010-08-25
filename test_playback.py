import unittest
import time
import rtp
from playback import *
from it_exceptions import *

class PlaybackTests(unittest.TestCase):
    def no_side_effects(self):
        self.r.file_exists = lambda f : True
        self.r.file_getsize = lambda f : 1

    def setUp(self):
        self.r = Playback()
        self.r.rtpplay = rtp.RTPPlayEmulator()
        self.r.rtpplay_live = rtp.RTPPlayEmulator()
    
    def tearDown(self):
        pass

    def testGetStatus(self):
        armed_file, is_playing, is_live_playing = self.r.get_status()
        assert armed_file is None
        assert not is_playing

    def testGetFileList(self):
        self.no_side_effects()
        self.r.listdir = lambda dump_dir : ["first", "second"]
        self.r._load_commit_time = lambda filename: 333

        result_files = self.r.get_file_list()
        assert result_files[0] == ("first", 333, 1)
        assert result_files[1] == ("second", 333, 1)

    def testArmWithNoFile(self):
        self.no_side_effects()
        self.r.file_exists = lambda f : False
        self.assertRaises(FileNotFoundError, self.r.arm, "filename.file")

    def testArm(self):
        self.no_side_effects()
        self.r._load_commit_time = lambda filename: 333
        self.r.rtpplay.file_exists = lambda f : True

        armed_file, is_playing, is_live_playing = self.r.get_status()
        assert armed_file is None
        assert not is_playing

        self.r.arm("file.file")

        armed_file, is_playing, is_live_playing = self.r.get_status()
        assert armed_file == "file.file"
        assert not is_playing

    def testArmTwice(self):
        self.no_side_effects()
        self.r._load_commit_time = lambda filename: 333
        self.r.rtpplay.file_exists = lambda f : True

        self.r.arm("file.file")

        armed_file, is_playing, is_live_playing = self.r.get_status()
        assert armed_file == "file.file"
        assert not is_playing

        self.r.arm("file.file")

        armed_file, is_playing, is_live_playing = self.r.get_status()
        assert armed_file == "file.file"
        assert not is_playing

    def testArmTwiceDifferentFile(self):
        self.no_side_effects()
        self.r._load_commit_time = lambda filename: 333
        self.r.rtpplay.file_exists = lambda f : True

        self.r.arm("file.file")

        armed_file, is_playing, is_live_playing = self.r.get_status()
        assert armed_file == "file.file"
        assert not is_playing

        self.r.arm("new.file")

        armed_file, is_playing, is_live_playing = self.r.get_status()
        assert armed_file == "new.file"
        assert not is_playing

    def testPlayBeforeArmed(self):
        self.no_side_effects()
        self.r._load_commit_time = lambda filename: 333
        self.r.rtpplay.file_exists = lambda f : True

        self.assertRaises(InvalidOperationError, self.r.play)

    def testPlay(self):
        self.no_side_effects()
        self.r._load_commit_time = lambda filename: 333
        self.r.rtpplay.file_exists = lambda f : True

        self.r.arm("file.file")
        self.r.play()

        armed_file, is_playing, is_live_playing = self.r.get_status()
        assert armed_file == "file.file"
        assert is_playing

    def testArmWithNoCommitTime(self):
        self.no_side_effects()
        self.r._load_commit_time = lambda filename: None
        self.r.rtpplay.file_exists = lambda f : True

        self.assertRaises(InvalidOperationError, self.r.arm, "new.file")

    def testArmWhilePlaying(self):
        self.no_side_effects()
        self.r._load_commit_time = lambda filename: 333
        self.r.rtpplay.file_exists = lambda f : True

        self.r.arm("file.file")
        self.r.play()
        self.assertRaises(InvalidOperationError, self.r.arm, "new.file")

        armed_file, is_playing, is_live_playing = self.r.get_status()
        assert armed_file == "file.file"
        assert is_playing

        self.r.play()

        armed_file, is_playing, is_live_playing = self.r.get_status()
        assert armed_file == "file.file"
        assert is_playing

    def testStopBeforeAnything(self):
        self.no_side_effects()

        self.r.stop()

        armed_file, is_playing, is_live_playing = self.r.get_status()
        assert armed_file is None
        assert not is_playing

    def testStopTwiceBeforeAnything(self):
        self.no_side_effects()

        self.r.stop()
        self.r.stop()

        armed_file, is_playing, is_live_playing = self.r.get_status()
        assert armed_file is None
        assert not is_playing

    def testStopAfterArm(self):
        self.no_side_effects()
        self.r._load_commit_time = lambda filename: 333
        self.r.rtpplay.file_exists = lambda f : True

        self.r.arm("test.file")
        self.r.stop()

        armed_file, is_playing, is_live_playing = self.r.get_status()
        assert armed_file is None
        assert not is_playing

    def testStopAfterPlay(self):
        self.no_side_effects()
        self.r._load_commit_time = lambda filename: 333
        self.r.rtpplay.file_exists = lambda f : True

        self.r.arm("test.file")
        self.r.play()
        self.r.stop()

        armed_file, is_playing, is_live_playing = self.r.get_status()
        assert armed_file is None
        assert not is_playing

        self.r.stop()

        armed_file, is_playing, is_live_playing = self.r.get_status()
        assert armed_file is None
        assert not is_playing
    
    def testLivePreviewBeforeArm(self):
        armed_file, is_playing, is_live_playing, self.r.get_status()
        assert armed_file is None
        assert not is_playing
        assert not is_live_playing
        
        self.assertRaises(InvalidOperationError,
                          self.r.play_live, "127.0.0.1", 0)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(PlaybackTests)
    unittest.TextTestRunner(verbosity=2).run(suite)
