import maya
from box import Box, BoxKeyError
import json


class AlertObject(Box):
    """
    Base class for alerts/silences.

    This class abstracts some commonalities between alerts and silences.
    """

    def __init__(self, *args, **kwargs):
        """
        Init method.

        Parameters
        ----------
        args : list
            Arbitrary positional arguments.

        kwargs: dict
            Arbitrary keyword arguments.

        """
        kwargs.update(default_box=True)

        super().__init__(*args, **kwargs)

    @classmethod
    def from_dict(cls, data):
        """
        Convert a dictionary into an AlertObject.

        This class method takes a dictionary as an argument, loads it as json
        and then constructs an AlertObject with that data.

        Parameters
        ----------
        data : dict
            A dictionary representing the alert object we would like returned.


        Returns
        -------
        Alert
            Return an AlertObject created from our data parameter.

        """
        try:
            data = json.loads(data)
        except:
            pass

        return cls(data)

    @property
    def attributes(self):
        """
        Alert attributes.

        This property is a simple way to set the attributes of our Alert
        object.

        Returns
        -------
        dict_keys
            Return a dict_keys view to populate the objects attributes.


        """
        return self.keys()

    def set_endtime(self, endtime):
        """
        Set an endtime for the alert.

        Alert Manager has a default configuration for the amount of time an
        Alert will persist beyond it's firing. This method allows us to
        specify the endsAt key with a datetime string in order to specify how
        long our alerts should persist beyond their first firing.

        Parameters
        ----------
        endtime : str
            A string representation of time. EX: 'in 2 minutes'


        Returns
        -------
        Alert
            Return our Alert object back to us with a specified endsAt.

        """
        # Returns an RFC3339 timestamp of the UTC variety
        # AlertManager expects rfc3339 timestamps
        # https://prometheus.io/docs/alerting/clients/
        # RFC3339 works best with UTC, so no override currently
        self.endsAt = maya.when(endtime).rfc3339()

    def validate_and_dump(self):
        """
        Validate the object meets minimum structural requirements.

        Validate and dump calls the overriden method validate in order to
        ensure our Alert/Silences have the structure necessary for Alert
        Manager not to throw an exception on post. If validation succeeds,
        we return the object as a json string. Otherwise, we raise a ValueError
        indicating to the user that the construction of their Alert/Silence
        doesn't pass muster.

        Returns
        -------
        self : str
            Return a jsonified string.


        Raises
        ------
        ValueError
            Raise a ValueError if our Alert/Silence doesn't pass muster.

        """
        if self._validate():
            return self.to_dict()
        else:
            raise ValueError('Object does not validate ==> {}'.format(self))

    def _validate(self):
        raise NotImplementedError


class Alert(AlertObject):
    """
    Class represents an Alert Manager alert.

    An alert object, minimally a dictionary that contains a 'labels' key with a
    value of a non-empty dictionary of labels with their corresponding values.

    """

    def add_label(self, key, value):
        """
        Add a label to our Alert object.

        Alert Manager alerts typically have a 'labels' key. The keys/values
        contained within the 'labels' data structure are used by Alert Manager
        for grouping/deduplication etc. This method allows us to easily specify
        a new label by passing in a key, value pair.

        Parameters
        ----------
        key: str
            The new label's key.

        value: str
            The new label's value.

        Returns
        -------
        Alert
            Return our Alert back to us with the newly added label.

        """
        if 'labels' not in self:
            self['labels'] = dict()
        self.labels[key] = value

    def add_annotation(self, key, value):
        """
        Add an annotation to our Alert object.

        Alert Manager alerts also typically have an annotations key. The
        keys/values specified here can be used for matching or simply
        providing more information about the alert itself.

        Parameters
        ----------
        key: str
            The new annotation's key.

        value: str
            The new annotation's value.

        Returns
        -------
        Alert
            Return our Alert back to us with the newly added annotation.

        """
        if 'annotations' not in self:
            self['annotations'] = dict()
        self.annotations[key] = value

    def _validate(self):
        """
        Validate that our Alert meets minimum structural requirements.

        Here we check our alert to see if it has at least the 'labels' key and
        that the 'labels' value is a non-empty dict.
        """
        valid = False
        if 'labels' in self:
            if self['labels']:
                valid = True
            else:
                pass
        else:
            pass
        return valid


class Silence(AlertObject):
    """
    Alert Manager silence.

    An Alert Manager silence object. Minimally a dict containing the keys,
    'matchers' and 'endsAt'. Silences suppress Alert Manager alerts.

    """

    def add_matcher(self, name, value, isRegex=False):
        """
        Add a matcher to the silence.

        Silences have a concept of matchers which are used to do just that.
        The keys/values specified in a matcher will be used to identify the
        alert we want to silence. This method is an easy way to add matchers
        and ensure they have the correct structure.

        Parameters
        ----------
        name: str
            This is the key name we want to match on e.g. 'alertname'.

        value: str
            This is the value of the key we expect. If 'alertname' is the key
            then we might expect the value to be 'high_memory' or something
            along those lines.

        isRegex: Bool
            (Default value=False)
            This determines whether or not we are matching on regex or exact.
            We default this value to False, but it can be overridden.

        """
        if 'matchers' not in self:
            self['matchers'] = list()
        self['matchers'].append({'name': name, 'value': value,
                                 'isRegex': isRegex})

    def _validate(self):
        """
        Validate that our Silence meets the minimum structural requirement.

        Ensure the silence object has both the 'matchers' and 'endsAt' keys.
        Additionally, validate that the 'matchers' value is a non-empty list.

        """
        valid = True
        if 'matchers' in self and 'endsAt' in self:
            if self['matchers'] and isinstance(self['matchers'], list):
                for matcher in self['matchers']:
                    if not matcher:
                        valid = False
                        break
            else:
                valid = False
        else:
            valid = False
        return valid
