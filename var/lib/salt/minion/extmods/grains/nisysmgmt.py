# -*- coding: utf-8 -*-
'''
National Instruments Systems Management grains.
'''

# Import python libs
from __future__ import absolute_import
import os
import os.path
import logging
import subprocess
import sys
import time
from datetime import datetime

# Import salt libs
# pylint: disable=import-error,3rd-party-module-not-gated
import salt.utils.files
import salt.utils.platform

# Solve the Chicken and egg problem where grains need to run before any
# of the modules are loaded and are generally available for any usage.
import salt.modules.cmdmod
# pylint: enable=import-error,3rd-party-module-not-gated

__salt__ = {
    'cmd.run_all': salt.modules.cmdmod._run_all_quiet,  # pylint: disable=protected-access
}

log = logging.getLogger(__name__)
__virtualname__ = 'nisysmgmt'

# Placeholder for '_nisysmgmt_utils' module that will be loaded
# in __virtual__ (when '__opts__' are available).
_nisysmgmt_utils = None  # pylint: disable=invalid-name
# Placeholder for '_nisysmgmt_grains' module that will be loaded
# in __virtual__ (when '__opts__' are available).
_nisysmgmt_grains = None  # pylint: disable=invalid-name

HAS_WMI = False
WMI_FAILURE_LOGGED = False
if salt.utils.platform.is_windows():
    import uptime  # pylint: disable=import-error,3rd-party-local-module-not-gated
    # attempt to import the python wmi module
    # the Windows minion uses WMI for some of its grains
    try:
        import wmi  # pylint: disable=import-error
        import salt.utils.winapi  # pylint: disable=ungrouped-imports
        HAS_WMI = True
    except ImportError:
        log.exception(
            'Unable to import Python wmi module, some National Instruments '
            'Systems Management grains will be missing'
        )
    import salt.modules.win_system  # pylint: disable=import-error,no-name-in-module,3rd-party-local-module-not-gated,ungrouped-imports
    __salt__['system.get_computer_desc'] = salt.modules.win_system.get_computer_desc  # pylint: disable=no-member
elif salt.utils.platform.is_linux():
    import salt.modules.system  # pylint: disable=import-error,no-name-in-module,3rd-party-local-module-not-gated,ungrouped-imports
    import salt.modules.shadow  # pylint: disable=import-error,no-name-in-module,3rd-party-local-module-not-gated,ungrouped-imports
    # get_computer_desc may use __salt__['cmd.run']
    salt.modules.system.__salt__ = {'cmd.run': salt.modules.cmdmod.run}  # pylint: disable=no-member
    __salt__['system.get_computer_desc'] = salt.modules.system.get_computer_desc  # pylint: disable=no-member
    __salt__['shadow.info'] = salt.modules.shadow.info  # pylint: disable=no-member


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


def _windows_platform_data():
    '''
    Use the platform module for as much as we can.
    '''
    # Provides:
    #    productcode
    #    deviceclass
    #    boottime
    #    nisysapi_enabled

    grains = {}
    productcode = ''
    deviceclass = 'Desktop'
    boottime = ''
    nisysapi_enabled = False

    if HAS_WMI:
        try:
            with salt.utils.winapi.Com():
                wmi_c = wmi.WMI()
                # 'productcode' and 'deviceclass'
                # http://msdn.microsoft.com/en-us/library/windows/desktop/aa394102%28v=vs.85%29.aspx
                systeminfo = wmi_c.Win32_ComputerSystem()[0]
                if hasattr(systeminfo, 'OEMStringArray'):
                    oem_strings = systeminfo.OEMStringArray
                    if oem_strings is not None:
                        for item in oem_strings:
                            colon = item.find(':')
                            if colon != -1:
                                key = item[:colon]
                                value = item[colon+1:]
                                if key == 'TargetID':
                                    productcode = value
                                elif key == 'DeviceClass':
                                    deviceclass = value
                # 'nisysapi_enabled'
                matched_services = wmi_c.Win32_Service(name='niminionagent')
                if matched_services and matched_services[0].State == 'Running':
                    nisysapi_enabled = True
        except Exception as exc:  # pylint: disable=broad-except
            global WMI_FAILURE_LOGGED  # pylint: disable=global-statement
            if not WMI_FAILURE_LOGGED:
                WMI_FAILURE_LOGGED = True
                log.error(
                    'Exception occurred when using WMI: %s',
                    exc, exc_info=True
                )

    localboottime = uptime.boottime()
    boottime = datetime.utcfromtimestamp(localboottime.timestamp()).isoformat() + 'Z'

    grains.update({
        'productcode': productcode,
        'deviceclass': deviceclass,
        'boottime': boottime,
        'nisysapi_enabled': nisysapi_enabled
    })
    return grains


def _linux_get_resetsource_x64(search_dir):
    '''
    Return path to 'reset_source' virtual file helper for x64.

    :param str search_dir: directory to start the search in

    :rtype: str|None
    :return: path to 'reset_source' or None if not found
    '''
    for root, _, files in os.walk(search_dir):
        # x64 driver exposes description file
        if 'reset_source' in files and 'description' in files:
            with salt.utils.files.fopen(os.path.join(root, 'description')) as fp_:
                if 'National Instruments Real-Time Features' in fp_.read():
                    return os.path.join(root, 'reset_source')
    return None


def _linux_get_resetsource_arm(search_dir):
    '''
    Return path to 'reset_source' virtual file helper for ARM.

    :param str search_dir: directory to start the search in

    :rtype: str|None
    :return: path to 'reset_source' or None if not found
    '''
    for root, _, files in os.walk(search_dir):
        # ARM driver exposes name
        if 'reset_source' in files and 'name' in files:
            with salt.utils.files.fopen(os.path.join(root, 'name')) as fp_:
                if 'cpld' in fp_.read():
                    return os.path.join(root, 'reset_source')
    return None


def _linux_get_resetsource_path():
    '''
    Return path to 'reset_source' virtual file.

    :rtype: str|None
    :return: path to 'reset_source' or None if not found
    '''
    if not os.path.isdir('/sys/devices'):
        return None

    # Example correct paths:
    #   x64:  /sys/devices/LNXSYSTM:00/LNXSYBUS:00/PNP0A08:00/device:0b/NIC775D:00/reset_source
    #   ARM:  /sys/devices/soc0/amba@0/e0004000.i2c/i2c-0/0-0040/reset_source
    # Optimized for efficiency, hence the extensive nested pathname checking.
    # pylint: disable=too-many-nested-blocks
    for subdir_1 in os.listdir('/sys/devices'):
        if subdir_1.startswith('LNXSYSTM:'):
            dir_1 = os.path.join('/sys/devices', subdir_1)
            if not os.path.isdir(dir_1):
                continue
            for subdir_2 in os.listdir(dir_1):
                if subdir_2.startswith('LNXSYBUS:'):
                    dir_2 = os.path.join(dir_1, subdir_2)
                    if not os.path.isdir(dir_2):
                        continue
                    for subdir_3 in os.listdir(dir_2):
                        if subdir_3.startswith('PNP'):
                            dir_3 = os.path.join(dir_2, subdir_3)
                            if not os.path.isdir(dir_3):
                                continue
                            for subdir_4 in os.listdir(dir_3):
                                if subdir_4.startswith('device:'):
                                    dir_4 = os.path.join(dir_3, subdir_4)
                                    if not os.path.isdir(dir_4):
                                        continue
                                    ret = _linux_get_resetsource_x64(dir_4)
                                    if ret:
                                        return ret
        elif subdir_1.startswith('soc'):
            dir_1 = os.path.join('/sys/devices', subdir_1)
            if not os.path.isdir(dir_1):
                continue
            for subdir_2 in os.listdir(dir_1):
                if subdir_2.startswith('amba@'):
                    dir_2 = os.path.join(dir_1, subdir_2)
                    if not os.path.isdir(dir_2):
                        continue
                    for subdir_3 in os.listdir(dir_2):
                        if subdir_3.endswith('.i2c'):
                            dir_3 = os.path.join(dir_2, subdir_3)
                            if not os.path.isdir(dir_3):
                                continue
                            for subdir_4 in os.listdir(dir_3):
                                if subdir_4.startswith('i2c-'):
                                    dir_4 = os.path.join(dir_3, subdir_4)
                                    if not os.path.isdir(dir_4):
                                        continue
                                    ret = _linux_get_resetsource_arm(dir_4)
                                    if ret:
                                        return ret
    # pylint: enable=too-many-nested-blocks
    return None


def _linux_platform_data():
    '''
    Use the platform module for as much as we can.
    '''
    # Provides:
    #    productcode
    #    deviceclass
    #    boottime
    #    resetsource
    #    nisysapi_enabled

    grains = {}
    productcode = ''
    deviceclass = 'Desktop'
    fw_printenv = '/sbin/fw_printenv'
    boottime = ''
    stat_path = '/proc/stat'
    ut_path = '/proc/uptime'
    niminionagent_daemon_path = '/etc/init.d/niminionagent'
    nisysapi_enabled = False

    resetsource_path = _linux_get_resetsource_path()
    if resetsource_path:
        with salt.utils.files.fopen(resetsource_path) as fp_:
            resetsource = fp_.read()
    else:
        resetsource = None

    if os.path.isfile(fw_printenv):
        ret = __salt__['cmd.run_all']('{0} -n DeviceCode'.format(fw_printenv))
        if ret['retcode'] == 0:
            productcode = ret['stdout']
        ret = __salt__['cmd.run_all']('{0} -n TargetClass'.format(fw_printenv))
        if ret['retcode'] == 0:
            deviceclass = ret['stdout']

    try:
        with salt.utils.files.fopen(stat_path, 'r') as fp_:
            for line in fp_:
                if line.startswith('btime'):
                    boottime = datetime.utcfromtimestamp(int(line.split()[1])).isoformat() + 'Z'
                    break
    except (IOError, IndexError):
        if os.path.isfile(ut_path):
            currenttime = time.time()
            with salt.utils.files.fopen(ut_path, 'r') as fp_:
                uptime_ = int(float(fp_.read().split()[0]))
            boottime = datetime.utcfromtimestamp(currenttime - uptime_).isoformat() + 'Z'

    if os.path.isfile(niminionagent_daemon_path):
        retcode = subprocess.call([niminionagent_daemon_path, 'status'])
        if retcode == 0:
            nisysapi_enabled = True

    grains.update({
        'productcode': productcode,
        'deviceclass': deviceclass,
        'boottime': boottime,
        'resetsource': resetsource,
        'nisysapi_enabled': nisysapi_enabled
    })
    return grains


def nisysmgmt_data(grains):
    '''
    Return grains used by National Instruments Systems Management
    '''
    nigrains = {}
    nigrains.update({'nisystemlink_version': '19.0.0'})
    nigrains.update(_nisysmgmt_utils.get_computer_desc_grains(__salt__))
    if salt.utils.platform.is_windows():
        nigrains.update(_windows_platform_data())
    elif salt.utils.platform.is_linux():
        nigrains.update(_linux_platform_data())
    nigrains.update(_nisysmgmt_grains.minion_blackout_grains(__opts__))
    nigrains.update(_nisysmgmt_utils.health_monitoring_grains(__opts__))
    if 'NILinuxRT' in grains['os_family'] and 'nilrt' == grains['lsb_distrib_id']:
        nigrains.update(_nisysmgmt_grains.startup_settings_grains(grains))
    nigrains.update(_nisysmgmt_grains.is_superuser_password_set_grains(__salt__, grains))
    nigrains.update(_nisysmgmt_grains.get_network_grains(grains))
    return nigrains
