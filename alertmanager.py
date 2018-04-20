from requests.compat import urljoin
import requests
import logging
import json
import copy


class AlertManager(object):

    def __init__(self, host, port=9093, req_obj=None):
        self.hostname = host
        self.port = port
        self._req_obj = req_obj

    @property
    def request_session(self):
        """
        This property is intended to be called by the _make_request method
        so we are always working with request.Sessions, allowing good
        customization for end users


        :return: _req_obj: a Request session object to allow developer
        manipulation
        """
        if not self._req_obj:
            self._req_obj = requests.Session()

        return self._req_obj

    def _make_request(self, method="GET", route="/", **kwargs):
        _host = "{}:{}".format(self.hostname, self.port)
        route = urljoin(_host, route)
        r = self.request_session.request(method, route, **kwargs)

        return r

    def get_alerts(self):
        route = "/api/v1/alerts"
        r = self._make_request("GET", route)
        return Alert.from_dict(r.json())

    def post_alerts(self):
        # http://10.255.238.146:9093/api/v1/alerts
        pass

    def get_status(self):
        route = "/api/v1/status"
        r = self._make_request("GET", route)
        return Alert.from_dict(r.json())

    def get_receivers(self):
        route = "/api/v1/receivers"
        r = self._make_request("GET", route)
        return Alert.from_dict(r.json())

    def get_alert_groups(self):
        route = "/api/v1/groups"
        r = self._make_request("GET", route)
        return Alert.from_dict(r.json())

    def get_silence(self, id=None):
        route = "/api/v1/silences"
        if id:
            route = urljoin(route, id)
        r = self._make_request("GET", route)
        return Alert.from_dict(r.json())

    def post_silence(self):
        # http://10.255.238.146:9093/api/v1/silences
        pass

    def delete_silence(self, id):
        route = "/api/v1/silence/{0}".format(id)
        r = self._make_request("DELETE", route)
        return r.json()


class Alert(object):

    def __init__(self, dict_data=None):

        # __data_dict is the private dict that powers _raw getters and setters
        self.__data_dict = {}
        self._raw = dict_data

        if not self._validate():
            logging.warning("This Alert object doesn't validate, feel free to "
                            "adjust but you will be blocked on POSTing")

    @property
    def _raw(self):
        return self.__data_dict

    @_raw.setter
    def _raw(self, dict_data):
        __local_data_dict = copy.deepcopy(self.__data_dict)
        __local_data_dict.update(dict_data)
        if not self._validate(__local_data_dict):
            logging.warning("This Alert object doesn't validate, feel free to "
                            "adjust but you will be blocked on POSTing")
        else:
            self.__data_dict.update(dict_data)
            for key in self.alert_attributes:
                setattr(self, key, self._raw[key])

    @property
    def alert_attributes(self):
        return self._raw.keys()

    @classmethod
    def from_dict(cls, data):
        try:
            data = json.loads(data)
        except:
            pass

        return cls(dict_data=data)

    def _validate(self, data=None):
        # logic to check if the dictionary is good
        # If data none, rely on self._raw, if data is there validate that data

        if self._raw == "invalid":
            return False

        return True

    def jsonify(self, force=False):
        # Standardize how we convert this to Postable data... exception on
        # validation, but allow overrides just in case
        if not self._validate() and not force:
            raise ValueError('Data dict is invalid')

        return json.dumps(self._raw)


if __name__ == '__main__':
    test_data = {
        "labels": {
            "alertname": "TylerCTest2",
            "dev": "test",
            "instance": "its fake2",
            "severity": "warning"
        },
        "annotations": {
            "description": "Please don't break monitor wide this time",
            "info": "Tyler coil did this",
            "summary": "Please just ignore this alert"
        },
        "startsAt": "2018-04-18T11:22:44.44444444-05:00",
        "endsAt": "2018-04-18T11:22:44.44444444-05:00",
        "generatorURL": "",
        "status": {
            "state": "unprocessed",
            "silencedBy": [],
            "inhibitedBy": []
        },
        "receivers": [
            "slack-bottesting"
        ],
        "fingerprint": "a88192ddf88700bd"
    }
    test = Alert.from_dict(test_data)

    print(test)

    print(dir(test))

    print(test.endsAt)

    # I don't like that this is the functionality to update an existing
    # alert... i have some ideas, but i wanna make you know i don't like it
    test._raw = {'endsAt': 'I changed'}

    print(test.endsAt)
