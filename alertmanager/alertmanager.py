from requests.compat import urljoin
from requests import HTTPError
import requests
import logging
import json
import maya
from box import Box, BoxKeyError
from .alert_objects import Alert, Silence


class AlertManager(object):
    """
    Implements and interface to the Alert Manager API.

    Alert Manager comes packaged with Prometheus and is used for alert
    management. This class aims to create an interface that simplifies
    interactions with the Alert Manager API. It also provides a simple means of
    introducing alerts into Alert Manager that do not originate from
    Prometheus.


    """

    SUCCESS_STATUSES = ['success']
    ERROR_STATUSES = ['error']

    def __init__(self, host, port=9093, req_obj=None):
        """
        Init method.

        Parameters
        ----------
        host : str
            This is the Alert Manager instance we wish to connect to.
        port : int
            (Default value = 9093)
            This is the port we wish to use to connect to our
            Alert Manager instance.
        req_obj : request object
            (Default value = None)
            The req object would typically be a requests.Session() object.

        """
        self.hostname = host
        self.port = port
        self._req_obj = req_obj

    @property
    def request_session(self):
        """
        Return a requests object used to affect HTTP requests.

        This property is intended to be called by the _make_request method
        so we are always working with request.Sessions, allowing good
        customization for end users

        Returns
        -------
        _req_obj : requests.Session()
            This is our default requests.Session() object. Can be overridden
            during instantiation by specifying the req_obj parameter.

        """
        if not self._req_obj:
            self._req_obj = requests.Session()

        return self._req_obj

    def _check_response(self, req):
        """
        Raise an error if our responses are not what we expect.

        This is a protected method that should only be used by methods making
        API calls. The intention is to check out responses for a successful
        HTTP status code along with a successful return from the Alert Manager
        API.

        Parameters
        ----------
        req : requests.Response
            This is the response object we want to verify.


        Returns
        -------
        boolean
            Return True if response check is successful.


        Raises
        ------
        ValueError
            Raise a value error if the 'status' key of our response is in
            our list of error statuses from Alert Manager.
        HTTPError
            Raise an http error if our response objects status_code attribute
            is not in requests.codes.ok (basically not a 200).

        """
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
        """
        Make our HTTP request and return a requests.Response object.

        This is a protected method to affect simple utilization of the
        requests.request method. Here we can override the HTTP verb we utilize
        and ensure any keyword arguments are passed as well. Ultimately this
        method returns a requests.Response object.

        Parameters
        ----------
        method : str
            (Default value = "GET")
            This is our HTTP verb.
        route : str
            (Default value = "/")
            This is the url we are making our request to.
        **kwargs : dict
            Arbitrary keyword arguments.


        Returns
        -------
        r : requests.Response
            Return the response from our API call.

        """
        _host = "{}:{}".format(self.hostname, self.port)
        route = urljoin(_host, route)

        r = self.request_session.request(method, route, **kwargs)
        return r

    def get_alerts(self, **kwargs):
        """
        Get a list of all alerts currently in Alert Manager.

        This method returns a list of all firing alerts from our Alert Manager
        instance.

        Parameters
        ----------
        **kwargs : dict
            Arbitrary keyword arguments. These kwargs can be used to specify
            filters to limit the return of our list of alerts to alerts that
            match our filter.


        Returns
        -------
        list
            Return a list of Alert objects from our Alert Manager instance.

        """
        route = "/api/v1/alerts"
        self._validate_get_alert_kwargs(**kwargs)
        if kwargs.get('filter'):
            kwargs['filter'] = self._handle_filters(kwargs['filter'])
        r = self._make_request("GET", route, params=kwargs)
        if self._check_response(r):
            return [Alert(alert) for alert in r.json()['data']]

    def _validate_get_alert_kwargs(self, **kwargs):
        """
        Check kwargs for validity.

        This is a protected method and should not be used outside of the
        get_alerts method. Here we verify that the kwargs we pass to filter our
        returned alerts is sane and contains keys Alert Manager knows about.

        Parameters
        ----------
        **kwargs : dict
            Arbitrary keyword arguments. These kwargs are used to specify
            filters to limit the return of our list of alerts to alerts that
            match our filter.


        Raises
        ------
        KeyError
            If a key in our kwargs doesn't match our list of valid_keys,
            we raise a key error. We prevent filter keys that Alert Manager
            doesn't understand from being passed in a request.

        """
        valid_keys = ['filter', 'silenced', 'inhibited']
        for key in kwargs.keys():
            if key not in valid_keys:
                raise KeyError('invalid get parameter {}'.format(key))

    def _handle_filters(self, filter_dict):
        """
        Construct and return a filter.

        This is a protected method and should not be used outside of the public
        get_alerts method. This method works to ensure the structure of our
        filter string is something that Alert Manager can understand.

        Parameters
        ----------
        filter_dict : dict
            A dict where the keys represent the label on which we wish to
            filter and the value that key should have.


        Returns
        -------
        str
            Returns a filter string to be passed along with our get_alerts
            method call.

        """
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
        """
        Post alerts to Alert Manager.

        This method is straightforward and it's name describes what it does.
        We use this method to post alerts to Alert Manager.

        Parameters
        ----------
        *alert : list of alerts or single alert
            This is either a list of Alert objects, dictionaries or a single
            Alert object or dictionary to be posted as an alert to
            Alert Manager.


        Returns
        -------
        Alert
            Return the response from Alert Manager as an Alert object.

        """
        payload = list()
        for obj in alert:
            if isinstance(obj, Alert):
                payload.append(obj.validate_and_dump())
            else:
                converted = Alert.from_dict(obj)
                payload.append(converted.validate_and_dump())
        route = "/api/v1/alerts"
        r = self._make_request("POST", route, json=payload)
        if self._check_response(r):
            return Alert.from_dict(r.json())

    def get_status(self):
        """
        Return the status of our Alert Manager instance.

        This method returns a great deal of valuable information about our
        Alert Manager's current configuration.

        Returns
        -------
        Alert
            Return the response from Alert Manager as an Alert object.

        """
        route = "/api/v1/status"
        r = self._make_request("GET", route)
        if self._check_response(r):
            return Alert.from_dict(r.json())

    def get_receivers(self):
        """
        Return a list of available receivers from our Alert Manager instance.

        Receivers from an alert manager perspective are notification
        integrations. Notifications can be sent from Alert Manager to any of
        The listed receivers. Per Alert Manager documentation, no new
        receivers are going to be added, so further integrations should be
        managed via the webhook receiver:
        https://prometheus.io/docs/alerting/configuration/

        Returns
        -------
        Alert
            Return the response from Alert Manager as an Alert object.

        """
        route = "/api/v1/receivers"
        r = self._make_request("GET", route)
        if self._check_response(r):
            return Alert.from_dict(r.json())

    def get_alert_groups(self):
        """
        Return alerts grouped by label keys.

        Another method to return our alerts.

        Return
        ------
        Alert
            Return the response from Alert Manager as an Alert object.

        """
        route = "/api/v1/alerts/groups"
        r = self._make_request("GET", route)
        if self._check_response(r):
            return Alert.from_dict(r.json())

    def get_silence(self, id=None):
        """
        Return a list of alert silences.

        Alert Manager allows alerts to be silenced. This call will return a
        list of all silences that have been created on our Alert Manager
        instance.

        Parameters
        ----------
        id : str
             (Default value = None)
             This is the ID of the silence we want returned.

        Returns
        -------
        Alert
            Return the response from Alert Manager as an Alert object. In this
            case a list of silences.

        """
        route = "/api/v1/silences"
        if id:
            route = urljoin(route, id)
        r = self._make_request("GET", route)
        if self._check_response(r):
            return Alert.from_dict(r.json())

    def post_silence(self, silence):
        """
        Create a silence.

        This method can be utilized to silence alerts based on a matches found
        by alert manager specified in the matchers parameter. Minimum structure
        for a matcher is as follows:
        {'matchers':
            [
                {
                    'name': 'label',
                    'value': 'label_value'
                }
            ],
            'endsAt': 'silence end_time'
        }

        Parameters
        ----------
        matcher : dict
            Our matcher is a dict containing keys/values to match an alert.


        Returns
        -------
        Alert
            Return the response from Alert Manager as an Alert object.

        """
        if isinstance(silence, Silence):
            silence = silence.validate_and_dump()
        else:
            silence = Silence.from_dict(silence)
            silence = silence.validate_and_dump()
        route = "/api/v1/silences"
        r = self._make_request("POST", route, json=silence)
        if self._check_response(r):
            return Alert.from_dict(r.json())

    def delete_silence(self, silence_id):
        """
        Delete a silence.

        This method allows us to specify a silence_id and delete it from
        Alert Manager.

        Parameters
        ----------
        silence_id : str
            This is the ID of the silence returned by Alert Manager.


        Returns
        -------
        Alert
            Return the response from Alert Manager as an Alert object.

        """
        route = "/api/v1/silence/"
        route = urljoin(route, silence_id)
        r = self._make_request("DELETE", route)
        if self._check_response(r):
            return Alert.from_dict(r.json())
