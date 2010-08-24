import util
import unittest
import time

class UtilTests(unittest.TestCase):

    def setUp(self):
        self.max_time = 1
        self.short_time = 0.05

    def test_blockWhile_base(self):
        """
        Test basic use case function of block while
        """

        start_time = time.time()
        f = lambda: True
        result = util.block_while(f, self.max_time)
        end_time = time.time()

        assert end_time-start_time >= self.max_time
        assert not result
	
        start_time = time.time()
        f = lambda: start_time + self.short_time > time.time()
        result = util.block_while(f, self.max_time)
        end_time = time.time()

        assert end_time-start_time < self.max_time
        assert result

    def test_blockWhile_invert(self):
        """
        Test basic function of block while
        """

        start_time = time.time()
        f = lambda: True
        result = util.block_while(f, self.max_time, True)
        end_time = time.time()

        assert end_time-start_time < self.max_time
        assert result
	
        start_time = time.time()
        f = lambda: start_time + self.short_time < time.time()
        result = util.block_while(f, self.max_time, True)
        end_time = time.time()

        assert end_time-start_time >= self.max_time
        assert not result

    def test_blockUntil_base(self):
        """
        Test basic function of block until, if passes
        should suffice for all other testing via block while
        """

        start_time = time.time()
        f = lambda: False
        result = util.block_while(f, self.max_time)
        end_time = time.time()

        assert end_time-start_time < self.max_time
        assert result

    def test_generateFileName_base(self):
        """
        Tests proper file name generations
        """

        name = "this_is_a_test"
        file_name = util.generate_file_name(name)
        assert file_name.count(name) > 0

    def test_generateFileName_ext(self):
        """
        Tests use of the extension variable
        """

        name = "this_is_a_test"
        ext = "tst"
        file_name = util.generate_file_name(name, ext)
        assert file_name.endswith("." + ext)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(UtilTests)
    unittest.TextTestRunner(verbosity=2).run(suite)
