# -*- coding: utf-8 -*-
'''
National Instruments SystemLink Health Monitoring Beacon
'''

# Import Python libs
from __future__ import absolute_import
import atexit
import logging
import os
import os.path
import sys

# Import third party libs
# pylint: disable=import-error,3rd-party-module-not-gated,wrong-import-order
import tornado.gen
import tornado.ioloop
import tornado.stack_context
# pylint: enable=import-error,3rd-party-module-not-gated,wrong-import-order

# Import National Instruments libs
# pylint: disable=import-error,3rd-party-module-not-gated
try:
    import systemlink.messagebus.paths as paths
    from systemlink.messagebus.amqp_configuration import SKYLINE_MASTER_CONFIGURATION_ID
    from systemlink.messagebus.amqp_configuration_manager import AmqpConfigurationManager
    from systemlink.messagebus.exceptions import SystemLinkException
    from systemlink.tagclient import TagClient
    HAS_NISKYLINE = True
except ImportError:
    HAS_NISKYLINE = False

# pylint: enable=import-error,3rd-party-module-not-gated

# Import salt libs
# pylint: disable=import-error,3rd-party-module-not-gated
import salt.utils.event
import salt.ext.six as six
# pylint: enable=import-error,3rd-party-module-not-gated

# Import local libs
# This file may be loaded out of __pycache__, so the
# directory of its .py may not be in the search path.
IMPORT_PATH = os.path.dirname(__file__)
if IMPORT_PATH.endswith('__pycache__'):
    IMPORT_PATH = os.path.dirname(IMPORT_PATH)
sys.path.append(IMPORT_PATH)
try:
    import _nisysmgmt_health
finally:
    # Remove the extra search path that we added to sys.path
    sys.path.remove(IMPORT_PATH)

# Set up logging
log = logging.getLogger(__name__)

# For firing local events
EVENT = None

# The tornado IO Loop for asynchronous actions
IO_LOOP = None

__virtualname__ = 'nisysmgmt_monitoring'

# Beacon initialization flag
ATEXIT_REGISTERED = False
BEACON_INITIALIZED = False
BEACON_INTERVAL_DISCONNECTED = 15
BEACON_INTERVAL_CURRENT = None

LAST_HEALTH_MONITORING_INTERVAL = None
LAST_HEALTH_MONITORING_RETENTION_TYPE = None
LAST_HEALTH_MONITORING_RETENTION_DURATION_DAYS = None
LAST_HEALTH_MONITORING_RETENTION_MAX_HISTORY_COUNT = None

# Tag Client Object
TAG_CLIENT = None
TAG_INFO = {}


def __virtual__():
    if not HAS_NISKYLINE:
        return False, 'This beacon requires NI Skyline Message Bus and Tag Client for Python'
    if not _nisysmgmt_health.HAS_PSUTIL:
        return False, 'This beacon requires psutil'

    return __virtualname__


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


def _retention_tag_properties():
    '''
    Return tag properties associated with retention.

    :return: Tag properties associated with retention.
    :rtype: dict(str, str)
    '''
    tag_properties = {
        'nitagRetention': __grains__['health_monitoring_retention_type'].upper(),
        'nitagHistoryTTLDays': str(__grains__['health_monitoring_retention_duration_days']),
        'nitagMaxHistoryCount': str(__grains__['health_monitoring_retention_max_history_count'])
    }
    return tag_properties


def _retention_changed():
    '''
    Return ``True`` if one of the retention related grains changed.
    ``False`` otherwise.

    :return: ``True`` if one of the retention related grains changed.
        ``False`` otherwise.
    :rtype: bool
    '''
    if (LAST_HEALTH_MONITORING_RETENTION_TYPE !=
            __grains__['health_monitoring_retention_type'] or
        LAST_HEALTH_MONITORING_RETENTION_DURATION_DAYS !=
            __grains__['health_monitoring_retention_duration_days'] or
        LAST_HEALTH_MONITORING_RETENTION_MAX_HISTORY_COUNT !=
            __grains__['health_monitoring_retention_max_history_count']):
        return True
    return False


def _update_tag_properties():
    '''
    Update the properties of all the tags managed by this beacon.
    Currently, we only update retention-related properties.
    Will invoke the Tag Client to do so.
    '''
    global LAST_HEALTH_MONITORING_RETENTION_TYPE  # pylint: disable=global-statement
    global LAST_HEALTH_MONITORING_RETENTION_DURATION_DAYS  # pylint: disable=global-statement
    global LAST_HEALTH_MONITORING_RETENTION_MAX_HISTORY_COUNT  # pylint: disable=global-statement

    tag_properties = _retention_tag_properties()
    for tag in six.itervalues(TAG_INFO):
        TAG_CLIENT.update_tag_metadata(tag['path'], tag_properties=tag_properties)
    LAST_HEALTH_MONITORING_RETENTION_TYPE = __grains__['health_monitoring_retention_type']
    LAST_HEALTH_MONITORING_RETENTION_DURATION_DAYS = __grains__['health_monitoring_retention_duration_days']
    LAST_HEALTH_MONITORING_RETENTION_MAX_HISTORY_COUNT = __grains__['health_monitoring_retention_max_history_count']


def _create_tags():
    '''
    Create Tags. Will invoke the Tag Client to do so.
    '''
    global LAST_HEALTH_MONITORING_RETENTION_TYPE  # pylint: disable=global-statement
    global LAST_HEALTH_MONITORING_RETENTION_DURATION_DAYS  # pylint: disable=global-statement
    global LAST_HEALTH_MONITORING_RETENTION_MAX_HISTORY_COUNT  # pylint: disable=global-statement

    tag_properties = _retention_tag_properties()
    tag_properties['minionId'] = __grains__['id']
    for tag in six.itervalues(TAG_INFO):
        TAG_CLIENT.create_tag(tag['path'], tag['type'], tag_properties=tag_properties)
    LAST_HEALTH_MONITORING_RETENTION_TYPE = __grains__['health_monitoring_retention_type']
    LAST_HEALTH_MONITORING_RETENTION_DURATION_DAYS = __grains__['health_monitoring_retention_duration_days']
    LAST_HEALTH_MONITORING_RETENTION_MAX_HISTORY_COUNT = __grains__['health_monitoring_retention_max_history_count']


def _update_tags():
    '''
    Update tags. Will invoke the Tag Client to do so.
    '''
    tag_info = []
    for tag in six.itervalues(TAG_INFO):
        tag_info.append(tag)

    TAG_CLIENT.update_tags(tag_info)


def _connected_beacon_interval():
    '''
    This is invoked once we successfully connected
    and want to ensure that the long term beacon
    interval is in effect.
    '''
    global BEACON_INTERVAL_CURRENT  # pylint: disable=global-statement
    global LAST_HEALTH_MONITORING_INTERVAL  # pylint: disable=global-statement

    interval_changed = False
    interval = __grains__['health_monitoring_interval']
    if interval != LAST_HEALTH_MONITORING_INTERVAL:
        LAST_HEALTH_MONITORING_INTERVAL = interval
        # When the grains interval changes, it means that the
        # beacon interval could have also been externally changed.
        interval_changed = True

    if BEACON_INTERVAL_CURRENT != interval or interval_changed:
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
        BEACON_INTERVAL_CURRENT = interval


def _disconnected_beacon_interval():
    '''
    This is invoked when we have not successfully connected
    or have been disconnected due to error and want to ensure
    that the short term beacon interval is in effect.
    '''
    global BEACON_INTERVAL_CURRENT  # pylint: disable=global-statement
    global LAST_HEALTH_MONITORING_INTERVAL  # pylint: disable=global-statement

    try:
        interval_changed = False
        interval = __grains__['health_monitoring_interval']
        if interval != LAST_HEALTH_MONITORING_INTERVAL:
            LAST_HEALTH_MONITORING_INTERVAL = interval
            # When the grains interval changes, it means that the
            # beacon interval could have also been externally changed.
            interval_changed = True

        if BEACON_INTERVAL_CURRENT != BEACON_INTERVAL_DISCONNECTED or interval_changed:
            _fire_local_event(
                {
                    'func': 'modify',
                    'name': __virtualname__,
                    'beacon_data': [{
                        'interval': BEACON_INTERVAL_DISCONNECTED
                    }]
                },
                'manage_beacons'
            )
            BEACON_INTERVAL_CURRENT = BEACON_INTERVAL_DISCONNECTED
    except Exception as exc:  # pylint: disable=broad-except
        log.error(
            'Unexpected exception in "nisysmgmt_monitoring._disconnected_beacon_interval": %s',
            exc, exc_info=True
        )


def _init_beacon():
    '''
    Initialize the beacon.

    :return: ``True`` if initialized successfully, ``False`` otherwise.
    :rtype: bool
    '''
    global ATEXIT_REGISTERED  # pylint: disable=global-statement
    global BEACON_INITIALIZED  # pylint: disable=global-statement
    global BEACON_INTERVAL_CURRENT  # pylint: disable=global-statement
    global IO_LOOP  # pylint: disable=global-statement
    global LAST_HEALTH_MONITORING_INTERVAL  # pylint: disable=global-statement
    global TAG_CLIENT  # pylint: disable=global-statement

    if BEACON_INITIALIZED:
        return True

    if not BEACON_INTERVAL_CURRENT:
        BEACON_INTERVAL_CURRENT = __opts__['beacons'][__virtualname__][0].get('interval', 15)

    LAST_HEALTH_MONITORING_INTERVAL = __grains__['health_monitoring_interval']

    if __opts__.get('master_type') == 'disable' or not __grains__['health_monitoring_enabled']:
        # Disable the beacon
        _fire_local_event(
            {'func': 'disable_beacon', 'name': __virtualname__},
            'manage_beacons'
        )
        return False

    file_path = paths.get_skyline_master_file()
    if not os.path.isfile(file_path):
        # The Skyline Master file is not available.
        # Can't set up the Tag Client without it.
        _disconnected_beacon_interval()
        return False

    if not IO_LOOP:
        IO_LOOP = tornado.ioloop.IOLoop.current()

    if TAG_CLIENT:
        # Always re-initialize the TAG_CLIENT in case the credentials or
        # certificate have changed.
        TAG_CLIENT.close()
        TAG_CLIENT = None

    config = AmqpConfigurationManager.get_configuration(
        id_=SKYLINE_MASTER_CONFIGURATION_ID,
        enable_fallbacks=False
    )
    TAG_CLIENT = TagClient(
        service_name='SaltMonitoringTagClient',
        config=config,
        auto_reconnect=False
    )

    if not ATEXIT_REGISTERED:
        atexit.register(_cleanup_beacon)
        ATEXIT_REGISTERED = True

    minion_id = __grains__['id']
    _nisysmgmt_health.setup_tags(TAG_INFO, minion_id)
    _create_tags()

    BEACON_INITIALIZED = True
    return True


def _cleanup_beacon():
    '''
    Clean up the beacon.
    For use with atexit.register
    '''
    global BEACON_INITIALIZED  # pylint: disable=global-statement
    global TAG_CLIENT  # pylint: disable=global-statement

    if TAG_CLIENT:
        # Disable logging when closing the Tag Client. _cleanup_beacon() is
        # called due to 'atexit.register', and this call can occur after the
        # logging process has exited. If the logging process has exited, and
        # it tries to log to the logging queue, the logging queue will block
        # waiting for send to flush (which will never happen since the
        # receiving process has exited), which will in turn hang this process
        # as it is trying to exit.
        logging.disable(logging.CRITICAL)
        TAG_CLIENT.close()
        logging.disable(logging.NOTSET)
        TAG_CLIENT = None
    TAG_INFO.clear()
    BEACON_INITIALIZED = False


@tornado.gen.coroutine
def _calc_and_publish_results():
    '''
    This will finish the calculations and publish the results.
    There is a delay in order to properly capture CPU usage.
    '''
    global BEACON_INITIALIZED  # pylint: disable=global-statement
    global TAG_CLIENT  # pylint: disable=global-statement

    try:
        _nisysmgmt_health.calc_cpu(TAG_INFO)
        _nisysmgmt_health.calc_disk(TAG_INFO)
        _nisysmgmt_health.calc_mem(TAG_INFO)

        try:
            if _retention_changed():
                _update_tag_properties()
            _update_tags()
            _connected_beacon_interval()
        except SystemLinkException as exc:
            if exc.error.name == 'Skyline.AMQPErrorFailedToLogIn':
                # Since the 'beacons_before_connect' configuration option is set
                # to True, the salt-master may have changed credentials after
                # the salt-minion connects to the salt-master through Salt. When
                # this occurs, allow the beacon to re-initialize itself in order
                # to use the new credentials.
                log.warning(
                    'AMQP Authentication error. Credentials may have changed: %s',
                    exc
                )
            else:
                # All other AMQP exceptions. Allow the beacon to re-initialize
                # itself.
                log.error(
                    'An AMQP error has occurred: %s',
                    exc, exc_info=True
                )
            BEACON_INITIALIZED = False
            # Close the TAG_CLIENT now so its doesn't try to reconnect while
            # we are waiting for the beacon to be re-initialized.
            # We use a nested try/except block in case this operation throws.
            TAG_CLIENT.close()
            TAG_CLIENT = None
            _disconnected_beacon_interval()
    except Exception as exc:  # pylint: disable=broad-except
        log.error(
            'Unexpected exception in "nisysmgmt_monitoring._calc_and_publish_results": %s',
            exc, exc_info=True
        )
        _disconnected_beacon_interval()


def validate(config):
    '''
    Validate the beacon configuration
    '''
    if not isinstance(config, list):
        return False, ('Configuration for nisysmgmt_monitoring '
                       'beacon must be a list.')
    return True, 'Valid beacon configuration'


def beacon(config):  # pylint: disable=unused-argument
    '''
    Every interval period, send Health Monitoring
    data back to the master via the NI Skyline Tag Client.

    Example Config

    .. code-block:: yaml

       beacons:
         nisysmgmt_monitoring:
           - interval: 300
    '''
    try:
        if not BEACON_INITIALIZED:
            success = _init_beacon()
            if not success:
                return []

            # Initially set the beacon interval to connected.
            # _calc_and_publish_results() will adjust the interval on
            # communication errors with the master.
            _connected_beacon_interval()

        _nisysmgmt_health.cpu_usage_snapshot()

        # Don't associate the callback with its caller's stack_context, similar
        # to spawn_callback() behavior.
        with tornado.stack_context.NullContext():
            IO_LOOP.call_later(_nisysmgmt_health.CPU_USAGE_INTERVAL, _calc_and_publish_results)
    except Exception as exc:  # pylint: disable=broad-except
        log.error(
            'Unexpected exception in the "nisysmgmt_monitoring" beacon: %s',
            exc, exc_info=True
        )
        _disconnected_beacon_interval()

    # Always return an empty list so that nothing is sent to the master
    # via Salt mechanisms.
    return []
