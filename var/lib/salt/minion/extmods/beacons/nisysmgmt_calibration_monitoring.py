# -*- coding: utf-8 -*-
'''
National Instruments SystemLink Calibration Monitoring Beacon
'''
from __future__ import absolute_import, print_function, unicode_literals

# Import Python libs
import atexit
import logging
import os
import os.path
import sys

# Import local libs
# pylint: disable=import-error,3rd-party-module-not-gated
try:
    import systemlink.messagebus.paths as paths
    from systemlink.messagebus.amqp_connection_manager import AmqpConnectionManager
    from systemlink.messagebus.amqp_configuration_manager import AmqpConfigurationManager
    from systemlink.messagebus.amqp_configuration import SKYLINE_MASTER_CONFIGURATION_ID
    from systemlink.messagebus.exceptions import SystemLinkException
    from systemlink.messagebus.message_service import MessageService
    from systemlink.messagebus.message_service_builder import MessageServiceBuilder
    HAS_NISKYLINE = True
except ImportError:
    HAS_NISKYLINE = False

# Import salt libs
import salt.utils.event
# pylint: enable=import-error,3rd-party-module-not-gated

# Import local libs
# Placeholder for '_apm_messages' module that will be loaded
# in __virtual__ (when '__opts__' are available).
_apm_messages = None  # pylint: disable=invalid-name

# Placeholder for '_nisysapi_ipc' module that will be loaded
# in __virtual__ (when '__opts__' are available).
_nisysapi_ipc = None  # pylint: disable=invalid-name

__virtualname__ = 'nisysmgmt_calibration_monitoring'

# Set up logging
log = logging.getLogger(__name__)

ATEXIT_REGISTERED = False
BEACON_INITIALIZED = False
BEACON_INTERVAL_DISCONNECTED = 15
BEACON_INTERVAL_CONNECTED = 300
BEACON_INTERVAL_CURRENT = None
CONNECTION_MANAGER = None
MESSAGE_SERVICE = None
# For firing local events
EVENT = None

# Version indicating the version of AssetPerformanceManagement Broadcast Message.
MESSAGE_VERSION = 1

'''
Dictionary containing fast "tag - tag name" data
'''
FAST_TAGS = {
    # SIMULATED VIRTUAL
    16814080: 'simulatedVirtual',
    # MODEL NUMBER
    16797696: 'modelNumber',
    # SERIAL NUMBER
    16805888: 'serialNumber',
    # VENDOR NUMBER
    16789504: 'vendorNumber',
    # PROVIDES BUS TYPE
    16932864: 'providesBusType',
    # IS PRESENT STATUS
    16924672: 'isPresentStatus'
}

'''
Dictionary containing calibration "tag - tag name" data
'''
CALIBRATION_TAGS = {
    # EXTERNAL CALIBRATION CHECKSUM
    17432576: 'calExtCheksum',
    # EXTERNAL CALIBRATION LAST LIMITED
    17428480: 'calExtLimited',
    # EXTERNAL CALIBRATION LAST TEMPERATURE
    16867328: 'calExtLastTempC',
    # EXTERNAL CALIBRATION LAST DATE
    16863232: 'calExtLastDate',
    # EXTERNAL CALIBRATION NEXT DATE
    16871424: 'calExtNextDate',
    # EXTERNAL CALIBRATION RECOMMENDED INTERVAL
    17207296: 'calExtRecommendedInterval',
    # SUPPORTS EXTERNAL CALIBRATION
    16859136: 'calExtSupport',
    # SUPPORTS LIMITED EXTERNAL CALIBRATION
    17424384: 'calExtSupportsLimited',
    # SUPPORTS EXTERNAL CALIBRATION WRITE
    17215488: 'calExtSupportsWrite',
    # EXTERNAL CALIBRATION MISC COMMENTS
    16961536: 'calExtMiscComments',
    # INTERNAL CALIBRATION LAST LIMITED
    17420288: 'calIntLastLimited',
    # INTERNAL CALIBRATION TEMPERATURE COUNT
    302034944: 'calIntTempCount',
    # INTERNAL CALIBRATION TEMPERATURE NAME_0
    302039040: 'calIntTempName0',
    # INTERNAL CALIBRATION LAST TEMPERATURE
    16850944: 'calIntLastTempC',
    # INTERNAL CALIBRATION LAST DATE
    16846848: 'calIntLastDate',
    # SUPPORTS INTERNAL CALIBRATION
    16842752: 'calIntSupport',
    # SENSOR TEMPERATURE COUNT
    17186816: 'sensorTempCount',
    # SENSOR TEMPERATURE NAME_0
    17190912: 'sensorTempName0',
    # SENSOR TEMPERATURE READING_O
    16965632: 'sensorReading0'
}


def __virtual__():
    if not HAS_NISKYLINE:
        return False, 'This beacon requires NI Skyline Message Bus for Python'

    global _apm_messages  # pylint: disable=global-statement,invalid-name
    global _nisysapi_ipc  # pylint: disable=global-statement,invalid-name

    # Add extra search paths to load '_apm_messages' and '_nisysapi_ipc'
    paths_to_add = __opts__['module_dirs']
    extmods_module_dir = os.path.join(__opts__['extension_modules'], 'modules')
    if extmods_module_dir not in paths_to_add:
        paths_to_add.append(extmods_module_dir)
    sys.path.extend(paths_to_add)
    try:
        import _apm_messages  # pylint: disable=redefined-outer-name,import-error,3rd-party-local-module-not-gated
        import _nisysapi_ipc  # pylint: disable=redefined-outer-name,import-error,3rd-party-local-module-not-gated
    finally:
        # Remove the extra search paths that we added to
        # sys.path
        for path in paths_to_add:
            sys.path.remove(path)

    return __virtualname__


def _set_connected_beacon_interval():
    '''
    This is invoked once we successfully connected
    and want to ensure that the long term beacon
    interval is in effect.
    '''
    global BEACON_INTERVAL_CURRENT  # pylint: disable=global-statement

    if BEACON_INTERVAL_CURRENT != BEACON_INTERVAL_CONNECTED:
        _fire_local_event(
            {
                'func': 'modify',
                'name': __virtualname__,
                'beacon_data': [{
                    'interval': BEACON_INTERVAL_CONNECTED
                }]
            },
            'manage_beacons'
        )
        BEACON_INTERVAL_CURRENT = BEACON_INTERVAL_CONNECTED


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


def _set_disconnected_beacon_interval():  # pylint: disable=invalid-name
    '''
    This is invoked when we have not successfully connected
    or have been disconnected due to error and want to ensure
    that the short term beacon interval is in effect.
    '''
    global BEACON_INTERVAL_CURRENT  # pylint: disable=global-statement

    if BEACON_INTERVAL_CURRENT != BEACON_INTERVAL_DISCONNECTED:
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


def _init_beacon():
    '''
    Initialize the beacon

    :return: ``True`` if initialized successfully, ``False`` otherwise.
    :rtype: bool
    '''
    global ATEXIT_REGISTERED  # pylint: disable=global-statement
    global BEACON_INITIALIZED  # pylint: disable=global-statement

    if BEACON_INITIALIZED:
        return True

    if __opts__.get('master_type') == 'disable':
        _fire_local_event(
            {
                'func': 'disable_beacon',
                'name': __virtualname__
            },
            'manage_beacons'
        )
        return False

    file_path = paths.get_skyline_master_file()
    if not os.path.isfile(file_path):
        # The Skyline Master file is not available.
        # Can't set up the Message Service without it.
        _set_disconnected_beacon_interval()
        return False

    _setup_amqp_connection()

    if not ATEXIT_REGISTERED:
        atexit.register(_cleanup_beacon)
        ATEXIT_REGISTERED = True

    BEACON_INITIALIZED = True
    return True


def _setup_amqp_connection():
    '''
    Opens the AMQP connection and instantiates a message service
    '''
    try:
        global CONNECTION_MANAGER  # pylint: disable=global-statement
        global MESSAGE_SERVICE  # pylint: disable=global-statement

        if MESSAGE_SERVICE:
            MESSAGE_SERVICE.close()
            MESSAGE_SERVICE = None

        if CONNECTION_MANAGER:
            CONNECTION_MANAGER.close()
            CONNECTION_MANAGER = None

        master_config = AmqpConfigurationManager.get_configuration(
            id_=SKYLINE_MASTER_CONFIGURATION_ID,
            enable_fallbacks=False
        )
        service_name = 'SaltCalibrationMonitoring'
        connection_timeout = 50

        CONNECTION_MANAGER = AmqpConnectionManager(config=master_config)
        CONNECTION_MANAGER.connection_timeout = connection_timeout
        CONNECTION_MANAGER.auto_reconnect = False
        message_service_builder = MessageServiceBuilder(service_name)
        message_service_builder.connection_manager = CONNECTION_MANAGER

        MESSAGE_SERVICE = MessageService(message_service_builder)
    except Exception as exc:  # pylint: disable=broad-except
        log.error(
            'Unexpected exception in "nisysmgmt_calibration_monitoring._setup_amqp_connection": %s',
            exc, exc_info=True
        )
        _set_disconnected_beacon_interval()


def _cleanup_beacon():
    '''
    Clean up the beacon. Set BEACON_INITIALIZED to False
    '''
    global BEACON_INITIALIZED  # pylint: disable=global-statement
    global CONNECTION_MANAGER  # pylint: disable=global-statement
    global MESSAGE_SERVICE  # pylint: disable=global-statement

    if MESSAGE_SERVICE:
        MESSAGE_SERVICE.close()
        MESSAGE_SERVICE = None

    if CONNECTION_MANAGER:
        CONNECTION_MANAGER.close()
        CONNECTION_MANAGER = None

    BEACON_INITIALIZED = False


def validate(config):
    '''
    Validate the beacon configuration
    '''
    if not isinstance(config, list):
        return False, ('Configuration for nisysmgmt_calibration_monitoring '
                       'beacon must be a list.')
    return True, 'Valid beacon configuration'


def beacon(config):  # pylint: disable=unused-argument
    '''
    National Instruments SystemLink Calibration Monitoring Beacon
    '''
    global BEACON_INITIALIZED  # pylint: disable=global-statement
    global CONNECTION_MANAGER  # pylint: disable=global-statement
    global MESSAGE_SERVICE  # pylint: disable=global-statement

    try:
        if not BEACON_INITIALIZED:
            success = _init_beacon()
            if not success:
                return []

            _set_connected_beacon_interval()

        minion_id = __grains__['id']

        get_props_response = _get_props(minion_id)
        if 'resources' not in get_props_response:
            return []

        is_present_status_tag = next((key for key, value in FAST_TAGS.items() if value == 'isPresentStatus'), None)

        resource_uris = [resource['resource_uri']
                         for resource in get_props_response['resources']
                         for prop in resource['properties']
                         if prop['tag'] == is_present_status_tag and prop['value'] == 1]

        if not resource_uris:
            return []

        populate_props_response = _populate_calibration_props(
            minion_id, resource_uris)
        _publish_calibration_data(
            minion_id, get_props_response, populate_props_response)
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
        if MESSAGE_SERVICE:
            MESSAGE_SERVICE.close()
            MESSAGE_SERVICE = None
        if CONNECTION_MANAGER:
            CONNECTION_MANAGER.close()
            CONNECTION_MANAGER = None
        _set_disconnected_beacon_interval()
    except Exception as exc:  # pylint: disable=broad-except
        log.error(
            'Unexpected exception in "nisysmgmt_calibration_monitoring beacon": %s',
            exc, exc_info=True
        )
        _set_disconnected_beacon_interval()

    return []


def _get_props(minion_id):
    '''
    Call a 'get_props' function to get a list of the resource uris in the minion
    '''
    get_props_request = {
        'fun': 'nisysapi.get_props',
        'args': [],
        'kwargs': {},
        'jid': '0',
        'id': minion_id
    }
    response = _nisysapi_ipc.query_minionagent(get_props_request, False)
    return response


def _populate_calibration_props(minion_id, resource_uris):
    '''
    Do a 'populate_props' job to get calibration slow properties
    '''
    resource_tags = [{'tags': list(CALIBRATION_TAGS.keys()), 'resource_uri': resource_uri} for
                     resource_uri in resource_uris]

    populate_props_request = {
        'fun': 'nisysapi.populate_props',
        'args': [],
        'kwargs': {
            'resource_tags': resource_tags
        },
        'jid': '0',
        'id': minion_id
    }

    response = _nisysapi_ipc.query_minionagent(populate_props_request, False)
    return response


def _publish_calibration_data(minion_id, get_props_response, populate_props_response):
    '''
    Create a 'calibratable assets' broadcast message which only contains information about
    the assets that are calibratable (SUPPORT_EXTERNAL_CAL or SUPPORT_INTERNAL_CAL)
    '''
    populated_assets = []
    for resource in populate_props_response['resources']:
        resource_uri = resource.get('resource_uri')
        fast_properties = dict((prop['tag'], prop['value']) for
                               prop in _extract_fast_props_for_resource(get_props_response, resource_uri))
        calibration_properties = dict((prop['tag'], prop['value']) for
                                      prop in resource['properties'])
        if (not _is_simulated(fast_properties)) and _supports_any_calibration(calibration_properties):
            asset = {CALIBRATION_TAGS[item]: calibration_properties[item] for
                     item in calibration_properties if item in CALIBRATION_TAGS}
            asset_extra = {FAST_TAGS[item]: fast_properties[item] for
                           item in fast_properties if item in FAST_TAGS}

            asset.update(asset_extra)
            asset['resource_uri'] = resource_uri
            populated_assets.append(asset)

    # The broadcast message must contain an array of APM_Message asset data
    asset_list = []
    for asset in populated_assets:
        self_calibration_data = _create_self_calibration_data(asset)
        external_calibration_data = _create_external_calibration_data(asset)
        asset_data = _create_asset_data(
            asset, external_calibration_data, self_calibration_data)
        asset_list.append(asset_data)

    _publish_results(minion_id, asset_list)


def _extract_fast_props_for_resource(get_props_response, resource_uri):  # pylint: disable=invalid-name
    '''
    Returns the properties of a resource from the get_props response
    '''
    for resource in get_props_response['resources']:
        if resource.get('resource_uri') == resource_uri:
            return resource['properties']
    return []


def _is_simulated(fast_properties):
    '''
    Checks if the given list contains properties which
    define if an asset is simulated
    '''
    simulated_virtual_fast_tag = list(FAST_TAGS.keys())[list(
        FAST_TAGS.values()).index('simulatedVirtual')]

    return fast_properties.get(simulated_virtual_fast_tag, False)


def _supports_any_calibration(calibration_properties):
    '''
    Checks if the given list contains properties which
    define if an asset supports internal or external calibration
    '''
    supports_internal_cal_tag = list(CALIBRATION_TAGS.keys())[list(
        CALIBRATION_TAGS.values()).index('calIntSupport')]
    supports_external_cal_tag = list(CALIBRATION_TAGS.keys())[list(
        CALIBRATION_TAGS.values()).index('calExtSupport')]

    return (calibration_properties.get(supports_external_cal_tag, False) or
            calibration_properties.get(supports_internal_cal_tag, False))


def _create_self_calibration_data(asset):
    '''
    Creates and returns a "SelfCalibrationData" message
    '''
    temperature_data = _create_multiple_sensor_temperature_data(
        asset,
        'calIntTempCount',
        'calIntTempName0',
        'calIntLastTempC'
    )
    self_calibration_data = _apm_messages.SelfCalibrationData(
        asset.get('calIntLastDate', '0 0 0 0'),
        asset.get('calIntLastLimited', False),
        temperature_data
    )

    return self_calibration_data


def _create_multiple_sensor_temperature_data(asset, count_tag, name_tag, reading_tag):  # pylint: disable=invalid-name
    '''
    Creates and returns a list of "TemperatureData" messages for multiple sensors
    '''
    count = asset.get(count_tag)
    if count and count > 1:
        return [_apm_messages.TemperatureData(t[0], t[1]) for
                t in zip(asset.get(name_tag, []), asset.get(reading_tag, []))]
    return _create_single_sensor_temperature_data(asset, name_tag, reading_tag)


def _create_single_sensor_temperature_data(asset, name_tag, reading_tag):  # pylint: disable=invalid-name
    '''
    Creates and returns a list with one "TemperatureData" message for a single sensor
    '''
    reading = asset.get(reading_tag)
    if reading:
        return [_apm_messages.TemperatureData(
            asset.get(name_tag, ''),
            reading
        )]
    return []


def _create_external_calibration_data(asset):  # pylint: disable=invalid-name
    '''
    Creates and returns an "ExternalCalibrationData" message
    '''
    temperature_data = _create_single_sensor_temperature_data(
        asset,
        '',
        'calExtLastTempC'
    )
    external_calibration_data = _apm_messages.ExternalCalibrationData(
        asset.get('calExtLastDate', '0 0 0 0'),
        asset.get('calExtNextDate', '0 0 0 0'),
        asset.get('calExtRecommendedInterval', -1),
        asset.get('calExtLimited', False),
        asset.get('calExtSupportsLimited', False),
        asset.get('calExtSupportsWrite', False),
        temperature_data,
        asset.get('calExtCheksum', ''),
        asset.get('calExtMiscComments', '')
    )

    return external_calibration_data


def _create_asset_data(asset, external_calibration_data, self_calibration_data):
    '''
    Creates and returns an "AssetData" message
    '''
    temperature_data = _create_multiple_sensor_temperature_data(
        asset,
        'sensorTempCount',
        'sensorTempName0',
        'sensorReading0'
    )
    asset_data = _apm_messages.AssetData(  # pylint: disable=too-many-function-args
        asset.get('resource_uri'),
        asset.get('serialNumber'),
        asset.get('vendorNumber'),
        asset.get('modelNumber'),
        asset.get('providesBusType', 0),
        asset.get('calIntSupport', False),
        self_calibration_data,
        asset.get('calExtSupport', False),
        external_calibration_data,
        temperature_data
    )

    return asset_data


def _publish_results(minion_id, assets):
    '''
    Publishes the given assets on the message bus as a broadcast message
    '''

    broadcast = _apm_messages.AssetPerformanceManagementMinionCalibrationUpdatedBroadcast(
        minion_id,
        assets,
        MESSAGE_VERSION
    )

    if MESSAGE_SERVICE:
        MESSAGE_SERVICE.publish_broadcast(broadcast)
