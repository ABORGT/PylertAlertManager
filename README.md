# PylertAlertManager

PylertAlertManager aims to be an easy-to-use interface for interacting with the Alert Manager API.


### Getting Started

The latest stable release is available from PyPI:

```
pip install pylertalertmanager
```

Otherwise you can install from git:

```
pip install git+https://github.com/ABORGT/PylertAlertManager.git
```

### Usage
Here we cover some basic usage examples to get folks off and running. We are importing json here just to pretty print our objects. Additionally, we have an Alert Manager instance running in docker to target.
```python
>>> import json
>>> from alertmanager import AlertManager
>>> from alertmanager import Alert
>>>
>>> # Provide some test data to be converted into an Alert object.
>>> test_data = {
...     "labels": {
...         "alertname": "TestAlert",
...         "instance": "TestInstance",
...         "severity": "critical"
...     },
...     "annotations": {
...         "description": "This is a test alert",
...         "info": "Test Alert",
...         "summary": "A simple Test alert"
...     }
... }
>>># Run the from_dict method on our test_data.
>>> test_alert = Alert.from_dict(test_data)
>>> type(test_alert)
<class 'alertmanager.alertmanager.Alert'>
>>>
>>> # Add an annotation with the add_annotation method.
>>> test_alert.add_annotation('test_annotation', 'this is a test annotation')
>>> print(json.dumps(test_alert, indent=4))
{
    "labels": {
        "alertname": "TestAlert",
        "instance": "TestInstance",
        "severity": "critical"
    },
    "annotations": {
        "description": "This is a test alert",
        "info": "Test Alert",
        "summary": "A simple Test alert",
        "test_annotation": "this is a test annotation"
    }
}
>>> # Add a label with the add_label method.
>>> test_alert.add_label('test_label', 'this is a test label')
>>> print(json.dumps(test_alert, indent=4))
{
    "labels": {
        "alertname": "TestAlert",
        "instance": "TestInstance",
        "severity": "critical",
        "test_label": "this is a test label"
    },
    "annotations": {
        "description": "This is a test alert",
        "info": "Test Alert",
        "summary": "A simple Test alert",
        "test_annotation": "this is a test annotation"
    }
}
>>> # Specify an Alert Manager host to connect to.
>>> host = 'http://127.0.0.1'
>>> a_manager = AlertManager(host=host)
>>>
>>> # Post an alert to our Alert Manager.
>>> a_manager.post_alerts(test_alert)
<Box: {'status': 'success'}>
>>> # Return a list of alerts from our Alert Manager.
>>> alerts = a_manager.get_alerts()
>>> print(json.dumps(alerts, indent=4))
[
    {
        "labels": {
            "alertname": "TestAlert",
            "instance": "TestInstance",
            "severity": "critical",
            "test_label": "this is a test label"
        },
        "annotations": {
            "description": "This is a test alert",
            "info": "Test Alert",
            "summary": "A simple Test alert",
            "test_annotation": "this is a test annotation"
        },
        "startsAt": "2018-11-08T16:25:02.327027475Z",
        "endsAt": "2018-11-08T16:30:02.327027475Z",
        "generatorURL": "",
        "status": {
            "state": "unprocessed",
            "silencedBy": [],
            "inhibitedBy": []
        },
        "receivers": [
            "team-X-mails"
        ],
        "fingerprint": "e6b119b9ce57e0c4"
    }
]
```
## Running the tests

TODO: Add tests

## Contributing
1. Fork it.
2. Create a branch describing either the issue or feature you're working.
3. Making changes, committing along the way.
4. Follow PEP8, except where ridiculous.
5. Include tests for any functionality changes.
6. Push the changes and create a pull request :D.

## Built With

* [Python3](https://www.python.org/downloads/) - Beautiful language.

## Authors

* **Tyler Coil** - [Other Projects](https://github.com/kamori)
* **Justin Palmer** - [Other Projects](https://github.com/jpavlav)

## Acknowledgments

* Kenneth Reitz -> [setup](https://github.com/kennethreitz/setup.py) - Thanks!
