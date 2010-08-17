import util
import unittest
import time

class UtilTests(unittest.TestCase):
    
    def test_blockWhile_base():
        """
        Test basic use case function of block while
        """

        start_time = time.time()
        util.block_while(true, 5)
        end_time = time.time()

        assert end_time-start_time > 5

        start_time = time.time()
        lambda(x): x + 1 > time.time()
        util.block_while(lambda(start_time), 5)
        end_time = time.time()

        assert end_time-start_time < 5

    def test_blockWhile_invert():
        """
        Test basic function of block while
        """

        start_time = time.time()
        lambda(x): x + 1 > time.time()
        util.block_while(lambda(start_time), 5, true)
        end_time = time.time()

        assert end_time-start_time > 5

        start_time = time.time()
        util.block_while(false, 5, true)
        end_time = time.time()

        assert end_time-start_time < 5

    def test_blockUntil_base():
p        """
        Test basic function of block until, if passes
        should suffice for all other testing via block while
        """

        start_time = time.time()
        util.block_until(false, 5, true)
        end_time = time.time()

        assert end_time-start_time < 5

    def test_generateFileName_base():
        """
        Tests proper file name generations
        """

        name = "this_is_a_test"
        file_name = util.generate_file_name(name)
        assert file_name.count(name) > 0

    def test_generateFileName_ext():
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
