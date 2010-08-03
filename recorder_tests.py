import unittest
import time
import rtp
from recorder import *
from it_exceptions import *

class RecorderTests(unittest.TestCase):
    def no_side_effects(self):
        # say that self.r.dump_file "exists"
        self.r.file_exists = lambda f : True
        self.r.rtpplay.file_exists = lambda f : True
        self._write_commit_file = lambda a, b : None

    def setUp(self):
        self.r = Recorder()
        self.r.rtpplay = rtp.RTPPlayEmulator()
        self.r.rtpdump = rtp.RTPDumpEmulator()
    
    def tearDown(self):
        pass
        
    def testGetStatusInitial(self):
        commit_time, elapsed_time, is_recording = self.r.get_status()
        assert commit_time is None
        assert elapsed_time is None
        assert not is_recording
    
    def testStartRecord(self):
        self.r.start_record()
        commit_time, elapsed_time, is_recording = self.r.get_status()
        assert commit_time is None
        assert elapsed_time is not None
        assert is_recording

    def testStartRecordStartRecord(self):
        self.r.start_record()
        self.assertRaises(ProcessAlreadyRunningError, self.r.start_record)

    def testStopRecordBeforeStart(self):
        self.r.stop_record()
        commit_time, elapsed_time, is_recording = self.r.get_status()
        assert commit_time is None
        assert elapsed_time is None
        assert not is_recording

    def testStopRecord(self):
        self.r.start_record()
        commit_time, elapsed_time, is_recording = self.r.get_status()
        assert commit_time is None
        assert elapsed_time is not None
        assert is_recording

        commit_time, elapsed_time, is_recording = self.r.stop_record()
        assert commit_time is None
        assert elapsed_time is not None
        assert not is_recording

    def testPlayPreviewBeforeSetup(self):
        self.assertRaises(NoRecordedFileError, self.r.play_preview, 10)

    def testPlayPreview(self):
        self.r.start_record()
        self.assertRaises(FileNotFoundError, self.r.play_preview, 10)
        
    def testPlayPreview2(self):
        self.no_side_effects()

        self.r.start_record()

        commit_time, elapsed_time, is_recording = self.r.get_status()
        assert commit_time is None
        assert elapsed_time is not None
        assert is_recording

        self.r.play_preview(10)

        commit_time, elapsed_time, is_recording = self.r.get_status()
        assert commit_time is None
        assert elapsed_time is not None
        assert is_recording

        self.r.stop_record()

        commit_time, elapsed_time, is_recording = self.r.get_status()
        assert commit_time is None
        assert elapsed_time is None
        assert not is_recording

    def testCommitTimeWithoutStarting(self):
        self.no_side_effects()

        self.assertRaises(NoRecordedFileError, self.r.commit_time, 345)

    def testCommitTime(self):
        self.no_side_effects()

        self.r.start_record()

        commit_time, elapsed_time, is_recording = self.r.get_status()
        assert commit_time is None
        assert elapsed_time is not None
        assert is_recording

        self.r.commit_time(345)

        commit_time, elapsed_time, is_recording = self.r.get_status()
        assert commit_time == 345
        assert elapsed_time is not None
        assert is_recording

        self.r.commit_time(-39)

        commit_time, elapsed_time, is_recording = self.r.get_status()
        assert commit_time == -39

        self.r.commit_time(0)

        commit_time, elapsed_time, is_recording = self.r.get_status()
        assert commit_time == 0
    
if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(RecorderTests)
    unittest.TextTestRunner(verbosity=2).run(suite)
