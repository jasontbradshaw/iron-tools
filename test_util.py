import util
import unittest
import time

class UtilTests(unittest.TestCase):

    def setUp(self):
        self.max_time = 1
        self.short_time = 0.05

    def testBlockWhileBase(self):
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
    
    def testBlockRaisesExceptionWhenNotGivenAFunction(self):
        """
        Makes sure that block_* throws an exception if if doesn't
        receive a callable function as its first argument.
        """
        
        # giving these a boolean is a common error
        self.assertRaises(AttributeError, util.block_while, False, 1)
        self.assertRaises(AttributeError, util.block_until, False, 1)
    
    '''
    def testBlockWhileInvert(self):
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
    '''

    def testBlockUntilBase(self):
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

    def testGenerateFileNameBase(self):
        """
        Tests proper file name generations
        """

        name = "this_is_a_test"
        file_name = util.generate_file_name(name)
        assert file_name.count(name) > 0

    def testGenerateFileNameExt(self):
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
