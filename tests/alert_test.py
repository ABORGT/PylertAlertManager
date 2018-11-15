import unittest

from alertmanager import Alert

from tests.data import TEST_ADD_LABEL_DATA
from tests.data import TEST_ADD_ANNOTATION_DATA
from tests.data import TEST_ALERT_VALIDATE_DATA_1
from tests.data import TEST_ALERT_VALIDATE_DATA_2


class TestAddLabel(unittest.TestCase):

    def setUp(self):
        self.alert = Alert()

    def test_add_label(self):
        self.alert.add_label('alertname', 'alert1')
        self.assertEqual(self.alert, TEST_ADD_LABEL_DATA)


class TestAddAnnotation(unittest.TestCase):

    def setUp(self):
        self.alert = Alert()

    def test_add_annotation(self):
        self.alert.add_annotation('alert_source', 'maas')
        self.assertEqual(self.alert, TEST_ADD_ANNOTATION_DATA)


class TestAlertValidate(unittest.TestCase):

    def setUp(self):
        self.alert = Alert()

    def test_no_labels_key(self):
        alert = self.alert.from_dict(TEST_ALERT_VALIDATE_DATA_1)
        with self.assertRaises(ValueError) as cm:
            alert.validate_and_dump()
        err = cm.exception
        self.assertIn('Object does not validate', str(err))

    def test_no_values_set_for_labels(self):
        alert = self.alert.from_dict(TEST_ALERT_VALIDATE_DATA_2)
        with self.assertRaises(ValueError) as cm:
            alert.validate_and_dump()
        err = cm.exception
        self.assertIn('Object does not validate', str(err))

    def test_validate_alert_good(self):
        alert = self.alert.from_dict(TEST_ADD_LABEL_DATA)
        result = alert.validate_and_dump()
        self.assertTrue(result)
