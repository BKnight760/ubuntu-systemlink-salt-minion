# -*- coding: utf-8 -*-

'''
Utility functions for use by NI Systems Management
related Salt modules and Python scripts.
'''
from __future__ import absolute_import

# Import python libs
import os.path
import logging
import sys

# Import salt libs
import salt.modules.cmdmod  # pylint: disable=import-error,3rd-party-module-not-gated
import salt.utils.stringutils  # pylint: disable=import-error,3rd-party-module-not-gated

log = logging.getLogger(__name__)

LAST_KNOWN_MINION_BLACKOUT_STATE = None
LAST_KNOWN_STARTUP_SETTINGS = None
LAST_KNOWN_IS_SUPERUSER_PASSWORD_SET = None
LAST_KNOWN_NETWORK_GRAINS_STATE = None

NIHASPASSWORD_PATH = '/usr/bin/nihaspassword'


def is_windows():
    '''
    Return True if the system platform is Windows. Return False otherwise.
    '''
    return sys.platform.startswith('win')


def is_linux():
    '''
    Return True if the system platform is Linux. Return False otherwise.
    '''
    return sys.platform.startswith('linux')

if is_windows():
    # pylint: disable=import-error,3rd-party-local-module-not-gated,wrong-import-position
    import winreg
    # pylint: enable=import-error,3rd-party-local-module-not-gated,wrong-import-position

    NI_INSTALLERS_REG_PATH = 'SOFTWARE\\National Instruments\\Common\\Installer'
    NI_INSTALLERS_REG_KEY_APP_DATA = 'NIPUBAPPDATADIR'

try:
    import startup_settings
    HAS_STARTUP_SETTINGS = True
except ImportError:
    HAS_STARTUP_SETTINGS = False

if is_windows():
    def _get_ni_common_appdata_dir():
        '''
        Return the National Instruments Common Application Data Directory.
        This looks like: 'C:\\ProgramData\\National Instruments'

        :return: The National Instruments Common Application Data Directory.
        :rtype: str
        '''
        with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                NI_INSTALLERS_REG_PATH,
                0,
                winreg.KEY_READ) as hkey:
            (appdata_dir, _) = winreg.QueryValueEx(hkey, NI_INSTALLERS_REG_KEY_APP_DATA)
            return appdata_dir


def minion_blackout_grains(opts):
    '''
    Fill the data about the locking-state of the minion, along with a
    potential list of commands that are allowed to be executed even
    while locked.
    '''
    # Provides:
    #    minion_blackout
    #    minion_blackout_whitelist
    grains = {}
    grains['minion_blackout_whitelist'] = opts.get('minion_blackout_whitelist', [])
    lock_file_path = get_blackout_file_path()
    grains['minion_blackout'] = os.path.isfile(lock_file_path)

    return grains


def set_last_known_minion_blackout(is_locked):
    '''
    This will persist the last_known_minion_blackout state
    to synchronize the beacon with set_blackout/unset_blackout
    functions in the module - to avoid race-condition on the master.
    '''
    global LAST_KNOWN_MINION_BLACKOUT_STATE  # pylint: disable=global-statement
    LAST_KNOWN_MINION_BLACKOUT_STATE = is_locked


def get_last_known_minion_blackout():
    '''
    Return the persisted last_known_minion_blackout state
    of the minion.
    '''
    return LAST_KNOWN_MINION_BLACKOUT_STATE


def get_blackout_file_path():
    '''
    Return path for the minion blackout lock file.
    eg: '/var/lib/salt/minion/minion_blackout.lock'
    '''
    if is_windows():
        # Use the <Program Data>\National Instruments\salt\var\cache\salt\minion folder, typically:
        # 'C:\ProgramData\National Instruments\salt\var\cache\salt\minion'
        lock_file = _get_ni_common_appdata_dir()
        lock_file = os.path.join(
            lock_file, 'salt',
            'var', 'cache', 'salt', 'minion'
        )
    elif is_linux():
        lock_file = '/var/lib/salt/minion/blackout'
    else:
        raise RuntimeError('Unsupported platform')
    lock_file = os.path.join(lock_file, 'minion_blackout.lock')
    return lock_file


def startup_settings_grains(grains):
    '''
    Fill the data about the startup settings of the minion.
    '''
    if not HAS_STARTUP_SETTINGS:
        return {}
    # inject __grains__ since startup_settings is a salt module
    # and assumes __grains__ are populated
    startup_settings.__grains__ = grains
    settings = startup_settings.get_all(False)
    return {'startup_settings': settings}


def set_last_known_startup_settings(settings):
    '''
    This will persist the last_known_startup_settings state
    to synchronize the beacon with enable functions in the
    startup_settings module - to avoid race-condition on the master.
    '''
    global LAST_KNOWN_STARTUP_SETTINGS  # pylint: disable=global-statement
    LAST_KNOWN_STARTUP_SETTINGS = settings


def get_last_known_startup_settings(grains):
    '''
    Return the persisted last_known_startup_settings state
    of the minion.
    '''
    global LAST_KNOWN_STARTUP_SETTINGS  # pylint: disable=global-statement
    if LAST_KNOWN_STARTUP_SETTINGS is None:
        if HAS_STARTUP_SETTINGS:
            # inject __grains__ since startup_settings is a salt module
            # and assumes __grains__ are populated
            startup_settings.__grains__ = grains
            LAST_KNOWN_STARTUP_SETTINGS = startup_settings.get_all(False)
        else:
            LAST_KNOWN_STARTUP_SETTINGS = {}
    return LAST_KNOWN_STARTUP_SETTINGS


def is_superuser_password_set_grains(salt_module_funcs, grains):  # pylint: disable=invalid-name
    '''
    Fill the data about whether the superuser password is set or not
    '''
    nigrains = {}
    if is_windows():
        return nigrains
    elif 'NILinuxRT' in grains['os_family'] and 'nilrt' == grains['lsb_distrib_id']:
        if os.path.exists(NIHASPASSWORD_PATH):
            result = salt.modules.cmdmod.retcode('{0} admin'.format(NIHASPASSWORD_PATH), output_loglevel='quiet')
            nigrains['is_superuser_password_set'] = bool(result)
    else:
        info = salt_module_funcs['shadow.info']('root')
        nigrains['is_superuser_password_set'] = bool(info.get('passwd'))
    return nigrains


def set_last_known_is_superuser_password_set(is_set):  # pylint: disable=invalid-name
    '''
    This will persist the last_known_is_superuser_password_set
    to synchronize the beacon with set_superuser_password
    function in the module - to avoid race-condition on the master.
    '''
    global LAST_KNOWN_IS_SUPERUSER_PASSWORD_SET  # pylint: disable=global-statement
    LAST_KNOWN_IS_SUPERUSER_PASSWORD_SET = is_set


def get_last_known_is_superuser_password_set():  # pylint: disable=invalid-name
    '''
    Return the persisted last_known_is_superuser_password_set state
    of the minion.
    '''
    return LAST_KNOWN_IS_SUPERUSER_PASSWORD_SET


def get_network_grains(grains):
    '''
    Get grains for network interfaces settings
    '''
    nigrains = {}
    if 'NILinuxRT' in grains['os_family']:
        try:
            import salt.modules.nilrt_ip as nilrt_ip  # pylint: disable=import-error,no-name-in-module,3rd-party-local-module-not-gated
            nilrt_ip.__grains__ = grains
            nilrt_ip.__salt__ = {
                'cmd.run': salt.modules.cmdmod.run,
                'cmd.shell': salt.modules.cmdmod.shell
            }  # pylint: disable=no-member
            nigrains.update({'network_settings': nilrt_ip.get_interfaces_details()})
        except ImportError:
            log.exception('Unable to import Python nilrt_ip module')
    return nigrains


def set_last_known_network_grains(network_grains):
    '''
    This will persist the last_known_network_grains state
    to synchronize the beacon - to avoid race-condition on the master.
    '''
    global LAST_KNOWN_NETWORK_GRAINS_STATE  # pylint: disable=global-statement
    LAST_KNOWN_NETWORK_GRAINS_STATE = network_grains


def get_last_known_network_grains():
    '''
    Return the persisted last_known_network_grains state
    of the minion.
    '''
    return LAST_KNOWN_NETWORK_GRAINS_STATE


def get_grain_as_str(grains, grain, default_value=''):
    '''
    Return the value of a grain as a string, or default_value if it's not found.
    '''
    value = grains.get(grain, default_value)
    try:
        return salt.utils.stringutils.to_str(value)
    except TypeError:
        if isinstance(value, int):
            return str(value)
        elif isinstance(value, list):
            return ','.join(value)
        return default_value
