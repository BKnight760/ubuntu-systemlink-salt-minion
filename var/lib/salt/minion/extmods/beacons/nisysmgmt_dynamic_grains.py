# -*- coding: utf-8 -*-
'''
National Instruments Systems Management Beacon to react to dynamic
grain changes
'''
from __future__ import absolute_import

# Import Python libs
import logging
import os.path
import sys

# Import salt libs
# pylint: disable=import-error,3rd-party-module-not-gated
import salt.utils.event
import salt.utils.platform
import salt.ext.six as six
# pylint: enable=import-error,3rd-party-module-not-gated

# pylint: disable=import-error,3rd-party-local-module-not-gated
if salt.utils.platform.is_windows():
    import salt.utils.winapi  # pylint: disable=ungrouped-imports
else:
    import salt.modules.cmdmod  # pylint: disable=ungrouped-imports
# pylint: enable=import-error,3rd-party-local-module-not-gated

log = logging.getLogger(__name__)

# Placeholder for 'modules/_nisysmgmt_utils.py' module that will be loaded
# in __virtual__ (when '__opts__' are available).
_nisysmgmt_utils = None  # pylint: disable=invalid-name
# Placeholder for 'modules/_nisysmgmt_grains.py' module that will be loaded
# in __virtual__ (when '__opts__' are available).
_nisysmgmt_grains = None  # pylint: disable=invalid-name

__virtualname__ = 'nisysmgmt_dynamic_grains'

EVENT = None
FIRST_RUN = True
LAST_MASTER = None
LAST_COMPUTER_DESC = None
LAST_HOST = None
LAST_IPV4 = None
LAST_IPV6 = None
LAST_HEALTH_MONITORING_OPTIONS = {
    'health_monitoring_enabled': None,
    'health_monitoring_interval': None,
    'health_monitoring_retention_type': None,
    'health_monitoring_retention_duration_days': None,
    'health_monitoring_retention_max_history_count': None
}

KEY_MDNS = ['master', 'host', 'ipv4', 'ipv6', 'computer_desc']
KEY_REFRESH_MASTER = [
    'minion_blackout',
    'network_settings',
    'startup_settings',
    'computer_desc'
]
KEY_REFRESH_MASTER.extend(list(LAST_HEALTH_MONITORING_OPTIONS.keys()))

if salt.utils.platform.is_windows():
    MDNS_BEACON = 'bonjour_announce'
else:
    MDNS_BEACON = 'avahi_announce'


def __virtual__():
    global _nisysmgmt_utils  # pylint: disable=global-statement,invalid-name
    global _nisysmgmt_grains  # pylint: disable=global-statement,invalid-name
    # Add extra search paths to load '_nisysapi_ipc'
    paths_to_add = __opts__['module_dirs']
    extmods_module_dir = os.path.join(__opts__['extension_modules'], 'modules')
    if extmods_module_dir not in paths_to_add:
        paths_to_add.append(extmods_module_dir)
    sys.path.extend(paths_to_add)
    try:
        import _nisysmgmt_utils  # pylint: disable=redefined-outer-name,import-error,3rd-party-local-module-not-gated
        import _nisysmgmt_grains  # pylint: disable=redefined-outer-name,import-error,3rd-party-local-module-not-gated
    finally:
        # Remove the extra search paths that we added to
        # sys.path
        for path in paths_to_add:
            sys.path.remove(path)

    return __virtualname__


def _init_event():
    '''
    Initialize the event object if needed.
    '''
    global EVENT  # pylint: disable=global-statement

    if not EVENT:
        EVENT = salt.utils.event.get_event(
            'minion', opts=__opts__, listen=False
        )


def _master_grain(changes):
    '''
    Check if the ``master`` grain has changed.

    :param changes: Dictionary with key of which grain has changed and
        value of the new value of the changed grain. This will be modified
        when any grains have changed.
    :type changes: dict
    :return: ``True`` if any grains were changed. ``False`` otherwise.
    :rtype: bool
    '''
    global LAST_MASTER  # pylint: disable=global-statement

    master = __grains__.get('master', None)  # pylint: disable=undefined-variable
    if LAST_MASTER != master:
        changes['master'] = master
        LAST_MASTER = master
        return True
    return False


def _mdns_grains(changes):
    '''
    Check if the mdns related network grains have changed.

    :param changes: Dictionary with key of which grain has changed and
        value of the new value of the changed grain. This will be modified
        when any grains have changed.
    :type changes: dict
    :return: ``True`` if any grains were changed. ``False`` otherwise.
    :rtype: bool
    '''
    global LAST_HOST  # pylint: disable=global-statement
    global LAST_IPV4  # pylint: disable=global-statement
    global LAST_IPV6  # pylint: disable=global-statement

    changed = False
    host = __grains__.get('host', '')  # pylint: disable=undefined-variable
    if LAST_HOST != host:
        changes['host'] = host
        LAST_HOST = host
        changed = True

    ipv4 = __grains__.get('ipv4', [])  # pylint: disable=undefined-variable
    if LAST_IPV4 != ipv4:
        changes['ipv4'] = ipv4
        LAST_IPV4 = ipv4
        changed = True

    ipv6 = __grains__.get('ipv6', [])  # pylint: disable=undefined-variable
    if LAST_IPV6 != ipv6:
        changes['ipv6'] = ipv6
        LAST_IPV6 = ipv6
        changed = True

    return changed


def _computer_desc_grain(changes):
    '''
    Check if the ``computer_desc`` grain has changed.

    :param changes: Dictionary with key of which grain has changed and
        value of the new value of the changed grain. This will be modified
        when any grains have changed.
    :type changes: dict
    :return: ``True`` if any grains were changed. ``False`` otherwise.
    :rtype: bool
    '''
    global LAST_COMPUTER_DESC  # pylint: disable=global-statement

    computer_desc = _nisysmgmt_utils.get_computer_desc_grains(__salt__).get('computer_desc', '')
    if LAST_COMPUTER_DESC != computer_desc:
        changes['computer_desc'] = computer_desc
        LAST_COMPUTER_DESC = computer_desc
        __grains__['computer_desc'] = computer_desc  # pylint: disable=undefined-variable
        return True
    return False


def _network_grains(changes):
    '''
    Check if the ``network_grains`` have changed.

    :param changes: Dictionary with key of which grain has changed and
        value of the new value of the changed grain. This will be modified
        when any grains have changed.
    :type changes: dict
    :return: ``True`` if any grains were changed. ``False`` otherwise.
    :rtype: bool
    '''
    network_grains = _nisysmgmt_grains.get_network_grains(__grains__)
    last_known_network_grains = _nisysmgmt_grains.get_last_known_network_grains()
    if last_known_network_grains != network_grains:
        changes['network_settings'] = network_grains
        _nisysmgmt_grains.set_last_known_network_grains(network_grains)
        __grains__.update(network_grains)  # pylint: disable=undefined-variable
        return True
    return False


def _minion_blackout_grain(changes):
    '''
    Check if the ``minion_blackout`` grain has changed.

    :param changes: Dictionary with key of which grain has changed and
        value of the new value of the changed grain. This will be modified
        when any grains have changed.
    :type changes: dict
    :return: ``True`` if any grains were changed. ``False`` otherwise.
    :rtype: bool
    '''
    minion_blackout = _nisysmgmt_grains.minion_blackout_grains(__opts__).get('minion_blackout', False)
    last_known_minion_blackout = _nisysmgmt_grains.get_last_known_minion_blackout()
    if (last_known_minion_blackout != minion_blackout or
            minion_blackout != __grains__['minion_blackout']):
        changes['minion_blackout'] = minion_blackout
        _nisysmgmt_grains.set_last_known_minion_blackout(minion_blackout)
        __grains__['minion_blackout'] = minion_blackout  # pylint: disable=undefined-variable
        return True
    return False


def _health_monitoring_grains(changes):
    '''
    Check if the Health Monitoring grains have changed.

    :param changes: Dictionary with key of which grain has changed and
        value of the new value of the changed grain. This will be modified
        when any grains have changed.
    :type changes: dict
    :return: ``True`` if any grains were changed. ``False`` otherwise.
    :rtype: bool
    '''
    changed = False
    hm_grains = _nisysmgmt_utils.health_monitoring_grains(__opts__)
    for key, val in six.iteritems(LAST_HEALTH_MONITORING_OPTIONS):
        if val != hm_grains[key]:
            changes[key] = hm_grains[key]
            LAST_HEALTH_MONITORING_OPTIONS[key] = hm_grains[key]
            if __grains__[key] != hm_grains[key]:  # pylint: disable=undefined-variable
                # Changed outside of the execution module
                __grains__[key] = hm_grains[key]
                if key == 'health_monitoring_enabled':
                    if hm_grains[key]:
                        func = 'enable_beacon'
                    else:
                        func = 'disable_beacon'
                    _init_event()
                    EVENT.fire_event(
                        {'func': func, 'name': 'nisysmgmt_monitoring'},
                        'manage_beacons'
                    )
                elif key == 'health_monitoring_interval':
                    _init_event()
                    # Use an interval of 1 to have the beacon execute on the next beacon
                    # loop. It will reset this value itself.
                    EVENT.fire_event(
                        {
                            'func': 'modify',
                            'name': 'nisysmgmt_monitoring',
                            'beacon_data': [{'interval': 1}]
                        },
                        'manage_beacons'
                    )
            changed = True
    return changed


def _startup_settings_grain(changes):
    '''
    Check if the ``startup_settings`` grain has changed.

    :param changes: Dictionary with key of which grain has changed and
        value of the new value of the changed grain. This will be modified
        when any grains have changed.
    :type changes: dict
    :return: ``True`` if any grains were changed. ``False`` otherwise.
    :rtype: bool
    '''
    if 'NILinuxRT' in __grains__['os_family'] and 'nilrt' == __grains__['lsb_distrib_id']:
        startup_settings = _nisysmgmt_grains.startup_settings_grains(__grains__).get('startup_settings')
        last_known_startup_settings = _nisysmgmt_grains.get_last_known_startup_settings(__grains__)
        if (last_known_startup_settings != startup_settings or
                startup_settings != __grains__['startup_settings']):
            changes['startup_settings'] = startup_settings
            _nisysmgmt_grains.set_last_known_startup_settings(startup_settings)
            __grains__['startup_settings'] = startup_settings  # pylint: disable=undefined-variable
            return True
    return False


def _enable_mdns_beacon_if_needed(changes):
    '''
    Enable mdns beacon if the mdns grains have changed.

    :param changes: Dictionary with key of which grain has changed and
        value of the new value of the changed grain. This will be modified
        when any grains have changed.
    :type changes: dict
    '''
    if any([key in KEY_MDNS for key in changes]) and MDNS_BEACON in __opts__['beacons']:
        _init_event()
        EVENT.fire_event(
            {'func': 'enable_beacon', 'name': MDNS_BEACON},
            'manage_beacons'
        )


def _update_grains_if_needed(changes):
    '''
    Enable refresh grains on master if grains changed.

    :param changes: Dictionary with key of which grain has changed and
        value of the new value of the changed grain. This will be modified
        when any grains have changed.
    :type changes: dict
    '''
    if any([key in KEY_REFRESH_MASTER for key in changes]):
        _init_event()
        tag = 'nisysmgmt/grains/update/{0}'.format(__grains__['id'])  # pylint: disable=undefined-variable
        data = {'data': __grains__}  # pylint: disable=undefined-variable
        EVENT.fire_master(data, tag)


def validate(config):
    '''
    Validate the beacon configuration
    '''
    if not isinstance(config, list):
        return False, ('Configuration for nisysmgmt_dynamic_grains '
                       'beacon must be a list.')
    return True, 'Valid beacon configuration'


def beacon(config):  # pylint: disable=unused-argument
    '''
    Check to see if a dynamic grain that is used for mDNS announcements
    changes.

    If changes, update the __grains__ (if applicable) and enable
    the appropriate mDNS announcement beacon.

    It is assumed that the mDNS announcement beacon that is used is
    set to `run_once: True` so that it will disable itself after a
    single run until it is re-enabled by this beacon.

    Example Config

    .. code-block:: yaml

       beacons:
         nisysmgmt_dynamic_grains:
           - interval: 15
    '''
    global FIRST_RUN  # pylint: disable=global-statement

    try:
        changes = {}

        _master_grain(changes)
        _mdns_grains(changes)
        _computer_desc_grain(changes)
        _minion_blackout_grain(changes)
        _health_monitoring_grains(changes)
        _startup_settings_grain(changes)

        # The network grains are undefined when system starts,
        # they updates with new value in first run
        # and update grains doesn't trigger
        force_update = _network_grains(changes)

        if (not FIRST_RUN or force_update) and changes:
            _enable_mdns_beacon_if_needed(changes)
            _update_grains_if_needed(changes)

        if FIRST_RUN:
            # Since the first run sets up the initial values,
            # no point in announcing changes until we have
            # a valid baseline.
            FIRST_RUN = False

    except Exception as exc:  # pylint: disable=broad-except
        log.error(
            'Unexpected exception in the "nisysmgmt_dynamic_grains" beacon: %s',
            exc, exc_info=True
        )

    # Always return an empty list so that nothing is sent to the master.
    return []
