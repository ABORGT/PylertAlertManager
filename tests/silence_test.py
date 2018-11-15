import unittest

from alertmanager import Silence

from tests.data import TEST_ADD_MATCHER_DATA
from tests.data import TEST_SILENCE_VALIDATE_DATA_1
from tests.data import TEST_SILENCE_VALIDATE_DATA_2
from tests.data import TEST_SILENCE_VALIDATE_DATA_3


class TestAddMatcher(unittest.TestCase):

    def setUp(self):
        self.silence = Silence()

    def test_add_matcher(self):
        self.silence.add_matcher('alertname', 'alert1')
        self.silence['endsAt'] = 'some_date_string'
        self.assertEqual(self.silence, TEST_ADD_MATCHER_DATA)


class TestSilenceValidate(unittest.TestCase):

    def setUp(self):
        self.silence = Silence()

    def test_validate_silence_no_matchers_key(self):
        silence = self.silence.from_dict(TEST_SILENCE_VALIDATE_DATA_1)
        with self.assertRaises(ValueError) as cm:
            silence.validate_and_dump()
        err = cm.exception
        self.assertIn('Object does not validate', str(err))

    def test_validate_silence_empty_list(self):
        silence = self.silence.from_dict(TEST_SILENCE_VALIDATE_DATA_2)
        with self.assertRaises(ValueError) as cm:
            silence.validate_and_dump()
        err = cm.exception
        self.assertIn('Object does not validate', str(err))

    def test_validate_silence_empty_dict_in_list(self):
        silence = self.silence.from_dict(TEST_SILENCE_VALIDATE_DATA_3)
        with self.assertRaises(ValueError) as cm:
            silence.validate_and_dump()
        err = cm.exception
        self.assertIn('Object does not validate', str(err))

    def test_validate_silence_good(self):
        silence = self.silence.from_dict(TEST_ADD_MATCHER_DATA)
        result = silence.validate_and_dump()
        self.assertTrue(result)
