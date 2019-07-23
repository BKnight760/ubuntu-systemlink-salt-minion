# -*- coding: utf-8 -*-
'''
    A module for startup settings
'''

from __future__ import absolute_import

import logging
import os.path
import sys

from requests.structures import CaseInsensitiveDict  # pylint: disable=import-error,3rd-party-local-module-not-gated

# Import local libs
# This file may be loaded out of __pycache__, so the
# directory of its .py may not be in the search path.
IMPORT_PATH = os.path.dirname(__file__)
if IMPORT_PATH.endswith('__pycache__'):
    IMPORT_PATH = os.path.dirname(IMPORT_PATH)
sys.path.append(IMPORT_PATH)
try:
    import _nisysmgmt_grains  # pylint: disable=import-error,3rd-party-local-module-not-gated
finally:
    # Remove the extra search path that we added to sys.path
    sys.path.remove(IMPORT_PATH)

log = logging.getLogger(__name__)

try:
    import salt.modules.cmdmod as cmd
    import salt.serializers.json as json
    import salt.ext.six.moves.configparser as configparser
except ImportError:
    log.critical("Salt is not available")

# Define the module's virtual name
__virtualname__ = 'startup'

NIRTINI_PATH = '/etc/natinst/share/ni-rt.ini'
NIRTCFG_PATH = '/usr/local/natinst/bin/nirtcfg'
FWSETENV_PATH = '/sbin/fw_setenv'


def __virtual__():
    '''
        Only load this module if the nirtcfg command exist and is older NILinuxRT
        :return: True if environment is set up and False otherwise
    '''
    if 'NILinuxRT' in __grains__['os_family'] and 'nilrt' == __grains__['lsb_distrib_id']:
        return True
    return False, 'The startup_settings module cannot be loaded.'


def get_all(json_format=False):
    '''
        .. note::
            Get all of these settings:
                - NoFPGAApp
                - NoApp
                - ConsoleOut
                - EmbeddedUI
                - LabVIEWAccess
        :param json_format: If true, returns the result in JSON format
        :return: Returns settings
        CLI Example:

        .. code-block:: bash
        salt '*' startup.get_all
        salt '*' startup.get_all True
    '''
    settings = {'NoFPGAApp': get('nofpgaapp'),
                'NoApp': get('noapp'),
                'ConsoleOut': get('consoleout'),
                'LabVIEWAccess': get('labviewaccess')}
    cpuarch = __grains__.get('cpuarch')
    if cpuarch == 'x86_64':
        settings['EmbeddedUI'] = get('embeddedui')
    if not json_format:
        return settings
    return json.serialize(settings)


def get(setting):
    '''
        .. note::
            Get one of these settings:
                - NoFPGAApp
                - NoApp
                - ConsoleOut
                - EmbeddedUI
                - LabVIEWAccess
        :param setting: Name of setting.
        :return: Returns value of that setting or -1 if error.
        CLI Example:

        .. code-block:: bash
        salt '*' startup.get noapp
    '''
    setting = setting.strip().lower()
    system_settings = {'nofpgaapp': 'NoFPGAApp.enabled',
                       'noapp': 'NoApp.enabled',
                       'consoleout': 'ConsoleOut.enabled',
                       'embeddedui': 'ui.enabled'}
    lvrt_settings = {'labviewaccess': 'RTTarget.RTProtocolAllowed'}
    config = configparser.RawConfigParser(dict_type=CaseInsensitiveDict)
    config.read(NIRTINI_PATH)
    if setting in system_settings:
        return config.get('systemsettings', system_settings[setting]).strip('\"')
    elif setting in lvrt_settings:
        return config.get('lvrt', lvrt_settings[setting]).strip('\"')
    return -1


def enable_console_out(enable=True):
    '''
        .. note::
            Enable or disable ConsoleOut
        :param enable: If true enable ConsoleOut else disable ConsoleOut. Default is True.
        CLI Example:

        .. code-block:: bash
        salt '*' startup.enable_console_out
    '''
    cmd.run('{0} --set section=systemsettings,token={1},value={2}'.format(NIRTCFG_PATH, 'ConsoleOut.enabled', enable))
    cmd.run('{0} consoleoutenable={1}'.format(FWSETENV_PATH, enable))
    system_settings = _nisysmgmt_grains.get_last_known_startup_settings(__grains__)
    system_settings['ConsoleOut'] = str(enable)
    __salt__['event.fire']({'force_refresh': True}, 'grains_refresh')
    return True


def enable_no_fpga_app(enable=True):
    '''
        .. note::
            Enable or disable NoFPGAApp
        :param enable: If true enable NoFPGAApp else disable NoFPGAApp. Default is True.
        CLI Example:

        .. code-block:: bash
        salt '*' startup.enable_no_fpga_app
    '''
    cmd.run('{0} --set section=systemsettings,token={1},value={2}'.format(NIRTCFG_PATH, 'NoFPGAApp.enabled', enable))
    system_settings = _nisysmgmt_grains.get_last_known_startup_settings(__grains__)
    system_settings['NoFPGAApp'] = str(enable)
    __salt__['event.fire']({'force_refresh': True}, 'grains_refresh')
    return True


def enable_no_app(enable=True):
    '''
        .. note::
            Enable or disable NoApp
        :param enable: If true enable NoApp else disable NoApp. Default is True.
        CLI Example:

        .. code-block:: bash
        salt '*' startup.enable_no_app
    '''
    cmd.run('{0} --set section=systemsettings,token={1},value={2}'.format(NIRTCFG_PATH, 'NoApp.enabled', enable))
    system_settings = _nisysmgmt_grains.get_last_known_startup_settings(__grains__)
    system_settings['NoApp'] = str(enable)
    __salt__['event.fire']({'force_refresh': True}, 'grains_refresh')
    return True


def enable_embedded_ui(enable=True):
    '''
        .. note::
            Enable or disable Embedded UI
        :param enable: If true enable Embedded UI else disable Embedded UI. Default is True.
        CLI Example:

        .. code-block:: bash
        salt '*' startup.enable_embedded_ui
    '''
    cmd.run('{0} --set section=systemsettings,token={1},value={2}'.format(NIRTCFG_PATH, 'ui.enabled', enable))
    system_settings = _nisysmgmt_grains.get_last_known_startup_settings(__grains__)
    system_settings['EmbeddedUI'] = str(enable)
    __salt__['event.fire']({'force_refresh': True}, 'grains_refresh')
    return True


def enable_labview_access(enable=True):
    '''
        .. note::
            Enable or disable LabVIEW Project Access
        :param enable: If true enable LabVIEW Project Access else disable LabVIEW Project Access. Default is True.
        CLI Example:

        .. code-block:: bash
        salt '*' startup.enable_labview_access
    '''
    cmd.run('{0} --set section=lvrt,token={1},value={2}'.format(NIRTCFG_PATH, 'RTTarget.RTProtocolAllowed', enable))
    system_settings = _nisysmgmt_grains.get_last_known_startup_settings(__grains__)
    system_settings['LabVIEWAccess'] = str(enable)
    __salt__['event.fire']({'force_refresh': True}, 'grains_refresh')
    return True
