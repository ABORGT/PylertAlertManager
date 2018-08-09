from requests.compat import urljoin
from requests import HTTPError
import collections
import requests
import logging
import json
import copy
import maya
from box import Box, BoxKeyError


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

        r = self.request_session.request(method, route, kwargs)
        return r

    def get_alerts(self, **kwargs):
        route = "/api/v1/alerts"
        self._validate_get_alert_kwargs(**kwargs)
        if kwargs['filter']:
            kwargs['filter'] = self._handle_filters(kwargs['filter'])
        r = self._make_request("GET", route, **kwargs)
        if self._check_response(r):
            return Alert.from_dict(r.json())

    def _validate_get_alert_kwargs(self, **kwargs):
        valid_keys = ['filter', 'silenced', 'inhibited']
        for key in kwargs.keys():
            if key not in valid_keys:
                raise KeyError('invalid get parameter {}'.format(key))

    def _handle_filters(self, filter_dict):
        if not isinstance(filter_dict, dict):
            raise TypeError('get_alerts() filter must be dict')
        filter_list = list()
        starter_string = '{}="{}"'
        for key, value in filter_dict.items():
            string = starter_string.format(key, value)
            filter_list.append(string)
        final_filter_string = ','.join(filter_list)
        return '{{{}}}'.format(final_filter_string)

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

    def post_silence(self, alert):
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


class Alert(Box):

    def __init__(self, *args, **kwargs):
        # This allows us to create keys that don't exist yet
        # Alert().this.key.hasnt.been.made.yet = False
        kwargs.update(default_box=True)

        super().__init__(*args, **kwargs)

    @classmethod
    def from_dict(cls, data):
        try:
            data = json.loads(data)
        except:
            pass

        return cls(data)

    @property
    def attributes(self):
        return self.keys()

    def _validate(self):
        # TODO: we need to offer a quick sanity check to our consumers
        if True:
            return True
        else:
            logging.warning('Does not validate')
            return False

    def add_label(self, key, value):
        self.labels[key] = value

    def add_annotation(self, key, value):
        self.annotations[key] = value

    def set_endtime(self, endtime):
        # Returns an RFC3339 timestamp of the UTC variety
        # AlertManager expects rfc3339 timestamps
        # https://prometheus.io/docs/alerting/clients/
        # RFC3339 works best with UTC, so no override currently
        self.endsAt = maya.when(endtime).rfc3339()


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
