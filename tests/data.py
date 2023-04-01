from datetime import datetime
import time

def am_fmt(ts):
    """ format time to AM format """
    return datetime.utcfromtimestamp(ts).strftime('%Y-%m-%dT%H:%M:%S.%fZ')

TEST_ADD_MATCHER_DATA = {
    'matchers': [{'name': 'alertname', 'value': 'alert1', 'isRegex': False}],
    'endsAt': 'some_date_string'
}

TEST_SILENCE_VALIDATE_DATA_1 = {
    'this': 'that'
}

TEST_SILENCE_VALIDATE_DATA_2 = {
    'matchers': []
}

TEST_SILENCE_VALIDATE_DATA_3 = {
    'matchers': [{}]
}

TEST_ADD_LABEL_DATA = {
    'labels': {'alertname': 'alert1'}
}

TEST_ADD_ANNOTATION_DATA = {
    'annotations': {'alert_source': 'maas'}
}

TEST_ALERT_VALIDATE_DATA_1 = {
    'this': 'that'
}

TEST_ALERT_VALIDATE_DATA_2 = {
    'labels': {}
}

TEST_ALERT_POST_DATA = {
    'labels': {
        'alertname': 'alert1'
    },
    'annotations': {
        'alert_source': 'alert_source1'
    }
}

TEST_SILENCE_POST_DATA = {
    "matchers": [{'name': 'alertname', 'value': 'alert1', 'isRegex': False}],
    "startsAt": am_fmt(int(time.time())),
    "endsAt": am_fmt(int(time.time()) + (60 * 60)),
    "createdBy": "pytest",
    "comment": "pytest"
}
