# -*- coding: utf-8 -*-
'''
National Instruments SystemLink Assets Monitoring Beacon
'''
from __future__ import absolute_import, print_function, unicode_literals

# Import Python libs
import logging

# Import salt libs
# pylint: disable=import-error,3rd-party-module-not-gated
import salt.utils.event
# pylint: enable=import-error,3rd-party-module-not-gated

__virtualname__ = 'nisysmgmt_assets_monitoring'

# Set up logging
log = logging.getLogger(__name__)

BEACON_INITIALIZED = False
BEACON_EXCEPTION_INTERVAL = 15
BEACON_NORMAL_INTERVAL = 300
BEACON_CURRENT_INTERVAL = None
# For firing local events
EVENT = None


def __virtual__():
    return __virtualname__


def validate(config):
    '''
    Validate the beacon configuration
    '''
    if not isinstance(config, list):
        return False, ('Configuration for nisysmgmt_assets_monitoring '
                       'beacon must be a list.')
    return True, 'Valid beacon configuration'


def beacon(config):  # pylint: disable=unused-argument
    '''
    National Instruments SystemLink Assets Monitoring Beacon
    '''
    global BEACON_INITIALIZED  # pylint: disable=global-statement

    beacon_interval = BEACON_NORMAL_INTERVAL

    try:
        if not BEACON_INITIALIZED:
            success = _init_beacon()
            if not success:
                return []

        __salt__['nisysmgmt_assets.publish_user_defined_assets']()
    except Exception as exc:  # pylint: disable=broad-except
        log.error(
            'Unexpected exception in "nisysmgmt_assets_monitoring beacon": %s',
            exc, exc_info=True
        )
        beacon_interval = BEACON_EXCEPTION_INTERVAL

    _set_beacon_interval(beacon_interval)

    return []


def _init_beacon():
    '''
    Initialize the beacon

    :return: ``True`` if initialized successfully, ``False`` otherwise.
    :rtype: bool
    '''
    global BEACON_INITIALIZED  # pylint: disable=global-statement

    if __opts__.get('master_type') == 'disable':
        _fire_local_event(
            {
                'func': 'disable_beacon',
                'name': __virtualname__
            },
            'manage_beacons'
        )
        return False

    BEACON_INITIALIZED = True
    return True


def _fire_local_event(event_data, event_tag):
    '''
    Fire an event to the local event bus.

    :param event_data: The data associated with the event.
    :type event_data: dict
    :param event_tag: The identifier of the event.
    :type event_tag: str
    '''
    global EVENT  # pylint: disable=global-statement

    if not EVENT:
        EVENT = salt.utils.event.get_event(
            'minion', opts=__opts__, listen=False
        )
    EVENT.fire_event(event_data, event_tag)


def _set_beacon_interval(interval):
    '''
    This is invoked once we successfully connected
    and want to ensure that the long term beacon
    interval is in effect.
    '''
    global BEACON_CURRENT_INTERVAL  # pylint: disable=global-statement

    if BEACON_CURRENT_INTERVAL != interval:
        _fire_local_event(
            {
                'func': 'modify',
                'name': __virtualname__,
                'beacon_data': [{
                    'interval': interval
                }]
            },
            'manage_beacons'
        )
        BEACON_CURRENT_INTERVAL = interval
