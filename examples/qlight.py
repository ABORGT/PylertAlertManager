from alertmanager import AlertManager, Alert
from copy import copy
from time import sleep

# https://github.com/KennethWilke/qlight_userspace
QLIGHT_PATH = "/opt/personal/qlight/qlight"
LIGHT_STATUS = {'red': 'off',
                'yellow': 'off',
                'blue': 'off',
                'green': 'on',
                'sound': 'off'}

ALL_GOOD_LIGHT_STATUS = copy(LIGHT_STATUS)

def set_red(status):
    if status.lower() not in ['on', 'off', 'blink']:
        raise Exception('Invalid Status')
    LIGHT_STATUS['red'] = status

def set_yellow(status):
    if status.lower() not in ['on', 'off', 'blink']:
        raise Exception('Invalid Status')
    LIGHT_STATUS['yellow'] = status

def set_green(status):
    if status.lower() not in ['on', 'off', 'blink']:
        raise Exception('Invalid Status')
    LIGHT_STATUS['green'] = status

def set_blue(status):
    if status.lower() not in ['on', 'off', 'blink']:
        raise Exception('Invalid Status')
    LIGHT_STATUS['blue'] = status

def set_sound(soundid):
    if type(soundid) != int and not soundid.isdigit():
        raise Exception('Invalid Soundid')
    LIGHT_STATUS['sound'] = soundid

def set_qlight_from_dict(alertstatus):
    _any_errors = 0
    for k, v in alertstatus.items():
        if v in ['on', 'blink'] or type(v) == int:
            _any_errors = 1
            _key = 'set_{}'.format(k)
            globals()[_key](v)
    if _any_errors:
        set_green('off')


def set_all_clear():
    global LIGHT_STATUS
    LIGHT_STATUS = copy(ALL_GOOD_LIGHT_STATUS)

def send_qlight_signal():
    _cmd = "{qlight} -r {red} -g {green} -b {blue} -y {yellow} -s {sound}"
    _r_cmd = _cmd.format(qlight=QLIGHT_PATH,
                         red=LIGHT_STATUS['red'],
                         green=LIGHT_STATUS['green'],
                         blue=LIGHT_STATUS['blue'],
                         yellow=LIGHT_STATUS['yellow'],
                         sound=LIGHT_STATUS['sound'])
    import os
    os.system('{}'.format(_r_cmd))
    if LIGHT_STATUS['sound'] and LIGHT_STATUS['sound'] != 'off':
        sleep(0.8)
        LIGHT_STATUS['sound'] = 'off'
        send_qlight_signal()

def get_qlight_labels(alert):
    light_status = {
        "red": alert.labels.qlight_red,
        "blue": alert.labels.qlight_blue,
        "green": alert.labels.qlight_green,
        "yellow": alert.labels.qlight_yellow,
        "sound": alert.labels.qlight_sound,
    }
    return light_status

# def infrastructure_maas_down(alert):
#     if (alert.labels.severity == 'critical' 
#             and 'maas' in alert.labels.monitor.lower()):
#         return True
    
#     return False

# def persite_maas_down(alert):
#     if (alert.labels.severity == 'critical' 
#             and ('maas' in alert.labels.monitor.lower() or alert.labels )):
#         return True

    
#     return False

# def infrastructure_down(alert):
#     return False

# def maintanence_window(alert):
#     return False


if __name__ == "__main__":

    # TODO: Make sure we don't beep too often in a row

    v2AlM = AlertManager('http://prometheus.example.com')
    v3AlM = AlertManager('http://api.kube.example.com')
    alerts = []

    alerts = list(v2AlM.get_alerts() + v3AlM.get_alerts())

    _CONFIRMATION = {}

    for alert in alerts:
        print(alert)

        # Get the qlight_* labels from each alert manager.
        # Apply it at the end.
        # Off is ignored on any labels, so one alert can not turn off a red for
        # someone else's alert.
        set_qlight_from_dict(get_qlight_labels(alert))
        continue

        # if persite_maas_down(alert) and not _CONFIRMATION.get('maas'):
        #     # A website is down, don't present green
        #     set_yellow('on')
        #     set_green('off')
        #     _CONFIRMATION['maas'] = True
        #     print("set and confirmed a customer site is down")

        # if ((infrastructure_down(alert) or infrastructure_maas_down(alert)) 
        #     and not _CONFIRMATION.get('infra')):
        #     # Infrastructure is down, don't present green
        #     set_red('blink')
        #     set_green('off')
        #     # set_sound(5)
        #     _CONFIRMATION['infra'] = True
        #     print("set and confirmed infrastructure downtime")

        # if maintanence_window(alert) and not _CONFIRMATION.get('maint'):
        #     # Set blue for maintanence, but let green be decided by other
        #     # checks
        #     set_blue('on')
        #     _CONFIRMATION['maint'] = True
        #     print("set and confirmed an active maint window")
    

    # After we know what state we got from alertmanager
    send_qlight_signal()
