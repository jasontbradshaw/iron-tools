import collectorweb
import unittest
import json

class CollectorWebTestCase(unittest.TestCase):
    def setUp(self):
        self.app = collectorweb.app.test_client()

    def tearDown(self):
        pass

    def test_test(self):
        rv = self.app.get('/')
        assert 'Collector Web' in rv.data
        rv = self.app.get('/stop_record')
        assert '500' not in rv.data

    def test_stop_record1(self):
        rv = self.app.get('/stop_record')
        assert '{}' in rv.data

    def test_record(self):
        rv = self.app.get('/stop_record')
        assert '{}' in rv.data

        rv = self.app.get('/start_record')
        assert '{}' in rv.data

        rv = self.app.get('/start_record')
        assert 'warning' in rv.data

        rv = self.app.get('/stop_record')
        assert '{}' in rv.data

if __name__ == '__main__':
    unittest.main()
