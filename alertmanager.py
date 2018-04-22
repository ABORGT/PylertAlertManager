from requests.compat import urljoin
from requests import HTTPError
import collections
import requests
import logging
import json
import copy


class AlertManager(object):

    SUCCESS_STATUSES = ['success']
    ERROR_STATUSES = ['error']

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

    def _check_response(self, req):
        """Helper to check that responses are what we expect."""
        if (req.status_code == requests.codes.ok
                and req.json()['status'] in self.SUCCESS_STATUSES):
            return True
        elif (req.status_code == requests.codes.ok
                and req.json()['status'] in self.ERROR_STATUSES):
            raise ValueError('{} ==> {}'.format(req.json()['errorType'],
                             req.json()['error']))
        else:
            raise HTTPError('{} ==> {}'.format(req.status_code, req.text))

    def _make_request(self, method="GET", route="/", **kwargs):
        _host = "{}:{}".format(self.hostname, self.port)
        route = urljoin(_host, route)

        # We want to make use of requests built in json, it just makese sense
        # But, they currently are not willing to allow you to provide a custom
        # json encoder, and we don't want to use all **kwargs[data] are json
        # So lets make some pyfu
        # https://github.com/requests/requests/issues/2755
        # https://github.com/python/cpython/blob/master/Lib/json/encoder.py#L413-L438
        if kwargs.get('json'):
            kw_json = kwargs['json']
            if isinstance(kw_json, collections.Iterable):
                kw_json = [dict(i) for i in kw_json]
            elif isinstance(kw_json, object):
                kw_json = dict(kw_json)

            kwargs['json'] = kw_json

        r = self.request_session.request(method, route, **kwargs)
        return r

    def get_alerts(self):
        route = "/api/v1/alerts"
        r = self._make_request("GET", route)
        if self._check_response(r):
            return Alert.from_dict(r.json())

    def post_alerts(self, *alert):
        # http://10.255.238.146:9093/api/v1/alerts
        route = "/api/v1/alerts"
        r = self._make_request("POST", route, json=alert)
        if self._check_response(r):
            return Alert.from_dict(r.json())

    def get_status(self):
        route = "/api/v1/status"
        r = self._make_request("GET", route)
        if self._check_response(r):
            return Alert.from_dict(r.json())

    def get_receivers(self):
        route = "/api/v1/receivers"
        r = self._make_request("GET", route)
        if self._check_response(r):
            return Alert.from_dict(r.json())

    def get_alert_groups(self):
        route = "/api/v1/groups"
        r = self._make_request("GET", route)
        if self._check_response(r):
            return Alert.from_dict(r.json())

    def get_silence(self, id=None):
        route = "/api/v1/silences"
        if id:
            route = urljoin(route, id)
        r = self._make_request("GET", route)
        if self._check_response(r):
            return Alert.from_dict(r.json())

    def post_silence(self, *alert):
        route = "/api/v1/silences"
        r = self._make_request("POST", route, json=alert)
        if self._check_response(r):
            return Alert.from_dict(r.json())

    def delete_silence(self, silence_id):
        route = "/api/v1/silence/"
        route = urljoin(route, silence_id)
        r = self._make_request("DELETE", route)
        if self._check_response(r):
            return Alert.from_dict(r.json())


class Alert(collections.UserDict):

    def __init__(self, dict_data=None):

        # __data_dict is the private dict that powers data getters and setters
        self.__data_dict = {}
        self.data = dict_data

        if not self._validate():
            logging.warning("This Alert object doesn't validate, feel free to "
                            "adjust but you will be blocked on POSTing")

    @property
    def data(self):
        return self.__data_dict

    @data.setter
    def data(self, dict_data):
        if not dict_data:
            return

        __local_data_dict = copy.deepcopy(self.__data_dict)
        __local_data_dict.update(dict_data)
        if not self._validate(__local_data_dict):
            logging.warning("This Alert object doesn't validate, feel free to "
                            "adjust but you will be blocked on POSTing")
        else:
            self.__data_dict.update(dict_data)
            for key in self.alert_attributes:
                setattr(self, key, self.data[key])

    @property
    def alert_attributes(self):
        return self.data.keys()

    @classmethod
    def from_dict(cls, data):
        try:
            data = json.loads(data)
        except:
            pass

        return cls(dict_data=data)

    def _validate(self, data=None):
        # logic to check if the dictionary is good
        # If data none, rely on self.data, if data is there validate that data

        if self.data == "invalid":
            return False

        return True

    def __setattr__(self, key, value, presynced=False):
        super().__setattr__(key, value)
        # This probably isn't efficient. But we're dealing with small amounts
        # of data, maybe if we see large scale alert creation we may need to
        # re-eval
        # Userdict don't expect the dict to be managed by attributes, that
        # is why we must implement this. Offer presynced because sometimes
        # we may wanna bypass the extra OP
        if not key.startswith('_') and key != 'data' and not presynced:
            self.data[key] = value

    def __setitem__(self, key, value):
        # This probably isn't efficient. But we're dealing with small amounts
        # of data, maybe if we see large scale alert creation we may need to
        # re-eval
        try:
            getattr(self, key)
            # Send presynced, because this call already accurately updates
            # the underlying dict because UserDict
            self.__setattr__(key, value, presynced=True)
        except AttributeError:
            # not an Alert Attribute
            pass

        super().__setitem__(key, value)



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
    test.data = {'endsAt': 'I changed'}

    print(test.endsAt)
