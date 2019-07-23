# -*- coding: utf-8 -*-
'''
A module for running nisysmgmt based actions.
'''
# Import python libs
from __future__ import absolute_import
import copy
import datetime
import logging
import os
import os.path
import sys
import time

# Import salt libs
# pylint: disable=import-error,3rd-party-module-not-gated
import salt.crypt
import salt.loader
import salt.transport
import salt.utils
import salt.utils.data
import salt.utils.event
import salt.utils.files
import salt.utils.platform
from salt.defaults import DEFAULT_TARGET_DELIM
from salt.exceptions import CommandExecutionError

# Import local libs
# This file may be loaded out of __pycache__, so the
# directory of its .py may not be in the search path.
IMPORT_PATH = os.path.dirname(__file__)
if IMPORT_PATH.endswith('__pycache__'):
    IMPORT_PATH = os.path.dirname(IMPORT_PATH)
sys.path.append(IMPORT_PATH)
try:
    import _nisysmgmt_config
    import _nisysmgmt_utils
    import _change_password
    import _nisysmgmt_grains
finally:
    # Remove the extra search path that we added to sys.path
    sys.path.remove(IMPORT_PATH)
# pylint: disable=import-error,3rd-party-module-not-gated

# Define the module's virtual name
__virtualname__ = 'nisysmgmt'

# Define unregister handler name
NISMS_JOB_FUNC_UNREGISTER = 'unregister'

# Used status codes
NISMS_STATUS_FAILED_GENERIC = -2147467259
NISMS_STATUS_SERVICE_NOT_FOUND = -2147220557
NISMS_STATUS_OPERATION_TIMED_OUT = -2147220448
NISMS_STATUS_INTERNAL_ERROR = -2147418113

# Used to keep track of when the Minion Info was last updated.
# This will only work if we reuse the same process for each job
# and not reload this module. Hence this will not work when
# 'multiprocessing' is True or when using salt-call. In those
# cases, the last updated timestamp will always be the current
# timestamp.
NISMS_MINION_INFO = None
NISMS_MINION_INFO_LASTUPDATED_TS = None

# Set up logging
log = logging.getLogger(__name__)


def __virtual__():
    '''
    Overwriting the cmd python module makes debugging modules
    with pdb a bit harder so lets do it this way instead.
    '''
    return __virtualname__


def _refresh_grains():
    '''
    Refresh the grains. '__grains__' will contain the updated grains.
    '''
    grains = salt.loader.grains(__opts__, force_refresh=True)
    # Make sure the '__grains__' reference doesn't change, so that other
    # loaded modules in this process will be automatically updated since
    # they already use the same reference.
    __grains__.clear()
    __grains__.update(grains)
    # salt.load.grains() always sets __opts__['grains'] to {}.
    # Make sure it is set correctly.
    __opts__['grains'] = __grains__


def _fire_master(data, tag):
    '''
    Fire an event to the Salt Master asynchronously.
    '''
    return salt.utils.event.MinionEvent(__opts__).fire_event(
        {'data': data, 'tag': tag, 'events': None, 'pretag': None},
        'fire_master'
    )


def _fire_master_sync(data, tag):
    '''
    Fire an event to the Salt Master synchronously.
    '''
    if (__opts__.get('local', None) or
            (__opts__.get('file_client', None) == 'local' and
                not __opts__.get('use_master_when_local', False)) or
            __opts__.get('master_type') == 'disable'):
        # We can't send an event if we're in masterless mode
        # Continue as if no error occurred.
        return False

    auth = salt.crypt.SAuth(__opts__)
    load = {'id': __opts__['id'],
            'tag': tag,
            'data': data,
            'tok': auth.gen_token('salt'),
            'cmd': '_minion_event'}
    channel = salt.transport.Channel.factory(__opts__)

    # 'channel.send' could throw an exception. If it does, let it leak out.
    channel.send(load, timeout=60)
    return True


def _reboot_windows():
    '''
    Reboot the system (for Windows)
    '''
    import win32api
    import win32security
    import pywintypes

    # Get the process token.
    flags = win32security.TOKEN_ADJUST_PRIVILEGES | win32security.TOKEN_QUERY
    htoken = win32security.OpenProcessToken(win32api.GetCurrentProcess(), flags)

    # Get the ID for the system shutdown privilege.
    privilege_id = win32security.LookupPrivilegeValue(
        None, win32security.SE_SHUTDOWN_NAME
    )

    # Create a list of the privileges to be added.
    new_privileges = [(privilege_id, win32security.SE_PRIVILEGE_ENABLED)]

    # Make the adjustment.
    win32security.AdjustTokenPrivileges(htoken, 0, new_privileges)

    message = 'NI SystemLink system restart'
    try:
        win32api.InitiateSystemShutdown(
            None, message, 5, True, True)
        return True
    except pywintypes.error as exc:
        (number, context, message) = exc
        msg = ('Failed to reboot the system. '
               'nbr: {0} ctx: {1} msg: {2}'.format(number, context, message))
        raise CommandExecutionError(msg)


def _reboot_linux():
    '''
    Reboot the system (for Linux)
    '''
    cmd = ['shutdown', '-r', 'now']
    ret = __salt__['cmd.run_all'](cmd, python_shell=False)
    if ret['retcode'] != 0:
        msg = 'Reboot failed. Exit code: {0}. Reason: {1}'.format(
            ret['retcode'], ret['stderr']
        )
        raise CommandExecutionError(msg)

    return True


def clear_superuser_password(**kwargs):  # pylint: disable=unused-argument
    '''
    Clearing the password of the superuser.
    '''
    delete_strategy = _change_password.DeletePasswordStrategy()
    _change_password.__salt__ = __salt__
    ret = _change_password.change_password(delete_strategy, __grains__)
    __salt__['event.fire']({'force_refresh': True}, 'grains_refresh')
    return ret


def grains_items(**kwargs):  # pylint: disable=unused-argument
    '''
    Return all of the minion's grains

    CLI Example:

    .. code-block:: bash

        salt '*' grains.items
    '''
    _refresh_grains()
    return __grains__


def grains_item(*args, **kwargs):
    '''
    Return one or more grains

    CLI Example:

    .. code-block:: bash

        salt '*' grains.item os
        salt '*' grains.item os osrelease oscodename
    '''
    ret = {}
    default = kwargs.get('default', '')
    delimiter = kwargs.get('delimiter', DEFAULT_TARGET_DELIM)
    _refresh_grains()

    try:
        for arg in args:
            ret[arg] = salt.utils.data.traverse_dict_and_list(
                __grains__,
                arg,
                default,
                delimiter
            )
    except KeyError:
        pass
    return ret


def get_info(*args, **kwargs):  # pylint: disable=unused-argument
    '''
    Get system information
    '''
    global NISMS_MINION_INFO  # pylint: disable=global-statement
    global NISMS_MINION_INFO_LASTUPDATED_TS  # pylint: disable=global-statement

    salt_call = bool(__opts__.get('__cli') == 'salt-call')
    if not salt_call:
        # salt-call already refreshes grains on entry.
        # No need to do it again.
        _refresh_grains()

    minion_info = {
        'comments': _nisysmgmt_grains.get_grain_as_str(__grains__, 'computer_desc'),
        'cpu_arch': _nisysmgmt_grains.get_grain_as_str(__grains__, 'cpuarch'),
        'device_class': _nisysmgmt_grains.get_grain_as_str(__grains__, 'deviceclass'),
        'hostname': _nisysmgmt_grains.get_grain_as_str(__grains__, 'host'),
        'ip_address': _nisysmgmt_grains.get_grain_as_str(__grains__, 'ipv4'),
        'master': _nisysmgmt_grains.get_grain_as_str(__grains__, 'master'),
        'minion_id': _nisysmgmt_grains.get_grain_as_str(__grains__, 'id'),
        'model_number': _nisysmgmt_grains.get_grain_as_str(__grains__, 'productcode'),
        'model_name': _nisysmgmt_grains.get_grain_as_str(__grains__, 'productname'),
        'os_family': _nisysmgmt_grains.get_grain_as_str(__grains__, 'os_family'),
        'os_release': _nisysmgmt_grains.get_grain_as_str(__grains__, 'osrelease'),
        'serial_number': _nisysmgmt_grains.get_grain_as_str(__grains__, 'serialnumber'),
        'vendor_name': _nisysmgmt_grains.get_grain_as_str(__grains__, 'manufacturer'),
        'version': _nisysmgmt_grains.get_grain_as_str(__grains__, 'saltversion')
    }

    if salt_call:
        minion_info['last_updated_timestamp'] = datetime.datetime.utcnow().isoformat() + 'Z'
    else:
        if minion_info != NISMS_MINION_INFO:
            NISMS_MINION_INFO = copy.deepcopy(minion_info)
            NISMS_MINION_INFO_LASTUPDATED_TS = datetime.datetime.utcnow().isoformat() + 'Z'
        minion_info['last_updated_timestamp'] = NISMS_MINION_INFO_LASTUPDATED_TS

    ret = {
        'info': minion_info,
        'status_code': 0
    }
    return ret


def restart(*args, **kwargs):  # pylint: disable=unused-argument
    '''
    Restart the system (reboot)
    '''
    # Perform the reboot
    if salt.utils.platform.is_windows():
        _reboot_windows()
    else:
        _reboot_linux()

    # Wait for the reboot to happen, since it's async
    time.sleep(120)

    # If we get here, then something went wrong
    return {'status_code': NISMS_STATUS_FAILED_GENERIC}


def set_network_address(request_mode, interface_name, address, netmask, gateway, nameservers):
    '''
    Set network address
    '''
    interfaces = __salt__['ip.get_interfaces_details']()
    # there was a bug before SystemLink 19.0 where we couldn't set an empty DNS list and we want to keep things backwards compatible
    if nameservers == ',' or nameservers == []:
        nameservers = None
    for interface in interfaces.get('interfaces'):
        if interface.get('connectionid') == interface_name:
            ipv4_info = interface.get('ipv4')
            if ipv4_info.get('requestmode') != request_mode:
                break
            if (ipv4_info.get('address') == address and
                    ipv4_info.get('gateway') == gateway and
                    ipv4_info.get('netmask') == netmask and
                    ipv4_info.get('dns') is not None and
                    ((ipv4_info.get('dns') == [] and nameservers == None) or
                    ' '.join(ipv4_info.get('dns')) == nameservers)):
                return True

    if request_mode == "dhcp_linklocal":
        result = __salt__['ip.set_dhcp_linklocal_all'](interface_name)
    else:
        result = __salt__['ip.set_static_all'](interface_name, address, netmask, gateway, nameservers)

    if result is False:
        return result

    # If the reboot required witnessed is set to True, we will do a system
    # reboot so the salt minion will also restart.
    if __salt__['system.get_reboot_required_witnessed']() is False:
        _nisysmgmt_utils.restart_salt_minion()

        # Wait for the restart to happen, since it's async
        time.sleep(120)
    return result


def set_blackout(*args, **kwargs):  # pylint: disable=unused-argument
    '''
    Set minion to blackout
    '''
    path = _nisysmgmt_grains.get_blackout_file_path()
    with salt.utils.files.fopen(path, 'a') as _:
        os.chmod(path, 0o777)
    __salt__['event.fire']({'force_refresh': True}, 'grains_refresh')
    _nisysmgmt_grains.set_last_known_minion_blackout(True)
    return True


def set_superuser_password(passwd, **kwargs):  # pylint: disable=unused-argument
    '''
    Setting the password of the superuser.
    '''
    set_strategy = _change_password.SetPasswordStrategy(passwd)
    _change_password.__salt__ = __salt__
    ret = _change_password.change_password(set_strategy, __grains__)
    __salt__['event.fire']({'force_refresh': True}, 'grains_refresh')
    return ret


def state_apply(**kwargs):  # pylint: disable=unused-argument
    '''
    Apply the sysmgmt state. This is needed because we don't want to
    put state.apply in the whitelist. We put only this in whitelist
    and call it from refresh_all.
    '''
    return __salt__['state.apply']('nisysmgmt')


def unregister(*args, **kwargs):  # pylint: disable=unused-argument
    '''
    Unregister the minion
    '''
    return _nisysmgmt_utils.restart_salt_minion(['--clear-master', '--clear-pki-cache'])


def unset_blackout(*args, **kwargs):  # pylint: disable=unused-argument
    '''
    Unset minion from blackout
    '''
    path = _nisysmgmt_grains.get_blackout_file_path()
    try:
        os.remove(path)
        __salt__['event.fire']({'force_refresh': True}, 'grains_refresh')
        _nisysmgmt_grains.set_last_known_minion_blackout(False)
        return True

    except OSError:
        return True


def get_health_monitoring_enabled(**kwargs):  # pylint: disable=unused-argument
    '''
    Return whether or not Health Monitoring is enabled.

    :return: Whether or not Health Monitoring is enabled.
    :rtype: bool
    '''
    hm_grains = _nisysmgmt_utils.health_monitoring_grains(__opts__)
    return hm_grains['health_monitoring_enabled']


def get_health_monitoring_interval(**kwargs):  # pylint: disable=unused-argument
    '''
    Return the Health Monitoring interval.

    :return: The Health Monitoring interval in seconds.
    :rtype: int
    '''
    hm_grains = _nisysmgmt_utils.health_monitoring_grains(__opts__)
    return hm_grains['health_monitoring_interval']


def get_health_monitoring_retention_type(**kwargs):  # pylint: disable=invalid-name,unused-argument
    '''
    Return the Health Monitoring retention type.

    :return: The Health Monitoring retention type. Will be one of
        ``none``, ``duration``, ``count``, or ``permanent``.
    :rtype: str
    '''
    hm_grains = _nisysmgmt_utils.health_monitoring_grains(__opts__)
    return hm_grains['health_monitoring_retention_type']


def get_health_monitoring_retention_duration_days(**kwargs):  # pylint: disable=invalid-name,unused-argument
    '''
    Return the Health Monitoring retention duration in days.

    :return: The Health Monitoring retention duration in days.
    :rtype: int
    '''
    hm_grains = _nisysmgmt_utils.health_monitoring_grains(__opts__)
    return hm_grains['health_monitoring_retention_duration_days']


def get_health_monitoring_retention_max_history_count(**kwargs):  # pylint: disable=invalid-name,unused-argument
    '''
    Return the Health Monitoring retention history count.

    :return: Tthe Health Monitoring retention history count.
    :rtype: int
    '''
    hm_grains = _nisysmgmt_utils.health_monitoring_grains(__opts__)
    return hm_grains['health_monitoring_retention_max_history_count']


def _set_health_monitoring_option(key, value):
    '''
    For a Health Monitoring option 'key', set value 'value'.

    :param key: The key name of the Health Monitoring option.
    :type key: str
    :param value: The value of the Health Monitoring option.
    :type value: str or int or float
    :return: ``True`` if the value was changed, ``False`` otherwise.
    :rtype: bool
    '''
    changed = True
    config_data = _nisysmgmt_config.read_dynamic_config(__opts__)
    if 'health_monitoring' not in config_data:
        config_data['health_monitoring'] = {}
    hm_config = config_data['health_monitoring']
    if key in hm_config and hm_config[key] == value:
        changed = False
    else:
        hm_config[key] = value

    if not changed:
        return False

    _nisysmgmt_config.write_dynamic_config(__opts__, config_data)
    __salt__['event.fire']({'force_refresh': True}, 'grains_refresh')
    return True


def set_health_monitoring_enabled(enabled, **kwargs):  # pylint: disable=unused-argument
    '''
    Set whether or not Health Monitoring is enabled.

    :param enabled: Whether or not Health Monitoring is enabled.
    :type enabled: bool
    :return: ``True``.
    :rtype: bool
    '''
    enabled = salt.utils.is_true(enabled)
    changed = _set_health_monitoring_option('enabled', enabled)
    if changed:
        if enabled:
            func = 'enable_beacon'
        else:
            func = 'disable_beacon'
        __salt__['event.fire'](
            {'func': func, 'name': 'nisysmgmt_monitoring'},
            'manage_beacons'
        )
    return True


def set_health_monitoring_interval(interval, **kwargs):  # pylint: disable=unused-argument
    '''
    Set the Health Monitoring interval.

    :param interval: The Health Monitoring interval.
    :type interval: int
    :return: ``True``.
    :rtype: bool
    '''
    interval = int(interval)
    changed = _set_health_monitoring_option('interval', interval)
    if changed:
        # Use an interval of 1 to have the beacon execute on the next beacon
        # loop. It will reset this value itself.
        __salt__['event.fire'](
            {
                'func': 'modify',
                'name': 'nisysmgmt_monitoring',
                'beacon_data': [{'interval': 1}]
            },
            'manage_beacons'
        )
    return True


def set_health_monitoring_retention_type(retention_type, **kwargs):  # pylint: disable=invalid-name,unused-argument
    '''
    Set the Health Monitoring retention type.

    :param retention_type: The Health Monitoring retention type. Must be one of
        ``none``, ``duration``, ``count``, or ``permanent``.
    :type retention_type: str
    :return: ``True``.
    :rtype: bool
    '''
    retention_type = retention_type.lower()
    if retention_type not in _nisysmgmt_utils.HEALTH_MONITORING_RETENTION_TYPES:
        msg = 'Invalid retention type: \'{0}\'. Valid choices: {1}'.format(
            retention_type,
            _nisysmgmt_utils.HEALTH_MONITORING_RETENTION_TYPES
        )
        raise CommandExecutionError(msg)

    _set_health_monitoring_option('retention_type', retention_type)
    return True


def set_health_monitoring_retention_duration_days(duration_days, **kwargs):  # pylint: disable=invalid-name,unused-argument
    '''
    Set the Health Monitoring retention duration (in days).
    This value is only used when ``retention_type`` is set to ``duration``.

    :param duration_days: The Health Monitoring retention duration (in days).
    :type duration_days: int
    :return: ``True``.
    :rtype: bool
    '''
    duration_days = int(duration_days)
    _set_health_monitoring_option('retention_duration_days', duration_days)
    return True


def set_health_monitoring_retention_max_history_count(max_history_count, **kwargs):  # pylint: disable=invalid-name,unused-argument
    '''
    Set the Health Monitoring retention history count.
    This value is only used when ``retention_type`` is set to ``count``.

    :param max_history_count: The Health Monitoring retention history count.
    :type max_history_count: int
    :return: ``True``.
    :rtype: bool
    '''
    max_history_count = int(max_history_count)
    _set_health_monitoring_option('retention_max_history_count', max_history_count)
    return True


def restart_if_required(*args, **kwargs):  # pylint: disable=unused-argument
    '''
    Restart the system if the reboot required witnessed is true
    '''
    if __salt__['system.get_reboot_required_witnessed']():
        restart()
