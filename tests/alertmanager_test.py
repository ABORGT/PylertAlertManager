import unittest
import time

from alertmanager import AlertManager
from alertmanager import Alert
from alertmanager import Silence

from tests.constants import HOST
from tests.data import TEST_ALERT_POST_DATA
from tests.data import TEST_SILENCE_POST_DATA


class TestAlertManagerMethods(unittest.TestCase):

    def setUp(self):
        self.a_manager = AlertManager(host=HOST)
        self.a_manager.post_alerts(TEST_ALERT_POST_DATA)
        self.alert = Alert.from_dict(TEST_ALERT_POST_DATA)
        self.silence = Silence.from_dict(TEST_SILENCE_POST_DATA)
        self.silence.set_endtime('in 1 minute')

    def tearDown(self):
        self.a_manager.request_session.close()

    def test_get_alerts(self):
        result = self.a_manager.get_alerts()
        self.assertTrue(result)

    def test_get_silences(self):
        result = self.a_manager.get_silences()
        self.assertTrue(result)

    def test_post_alerts(self):
        result = self.a_manager.post_alerts(self.alert)
        self.assertIn(200, result.status)

    def test_get_status(self):
        result = self.a_manager.get_status()
        self.assertIn('ready', result.cluster.status)

    def test_get_receivers(self):
        result = self.a_manager.get_status()
        self.assertIn('ready', result.cluster.status)

    def test_get_alert_groups(self):
        result = self.a_manager.get_alert_groups()
        self.assertTrue(result)

    def test_get_silence(self):
        result = self.a_manager.get_silence()
        self.assertTrue(result)

    def test_post_silence(self):
        result = self.a_manager.post_silence(self.silence)
        print(result)
        self.assertTrue(result)

    def test_delete_silence(self):
        self.a_manager.post_silence(self.silence)
        time.sleep(2)
        silences = self.a_manager.get_silence()
        for silence in silences:
            if silence['status']['state'] == 'active':
                silence_id = silence['id']
        result = self.a_manager.delete_silence(silence_id)
        self.assertIn(200, result.status)
