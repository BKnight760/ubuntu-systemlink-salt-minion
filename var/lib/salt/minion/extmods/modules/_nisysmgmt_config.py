# -*- coding: utf-8 -*-
'''
NI Systems Management configuration functions.
'''

# Import Python libs
from __future__ import absolute_import
import os.path
import yaml


def get_dynamic_conf_file_path(opts):
    '''
    Return path for the dynamic configuration file
    eg: '/etc/salt/minion.d/nisysmgmt_dynamic.conf'

    :param opts: Options dictionary used by Salt.
    :type opts: dict
    '''
    base_conf_dir = os.path.dirname(opts['conf_file'])
    if opts.get('__role') == 'master':
        subdir = 'master.d'
    else:
        subdir = 'minion.d'
    conf_file = os.path.join(base_conf_dir, subdir, 'nisysmgmt_dynamic.conf')
    return conf_file


def read_dynamic_config(opts):
    '''
    Reads the contents of the dynamic configuation.
    Returns {} if the file is empty or doesn't exist.

    :param opts: Options dictionary used by Salt.
    :type opts: dict
    :return: The contents of the dynamic configuration as a dictionary
        or {} if the file is empty or does not exit.
    :rtype: dict
    '''
    config_file = get_dynamic_conf_file_path(opts)
    if not os.path.isfile(config_file):
        return {}

    with open(config_file, 'r') as fp_:  # pylint: disable=resource-leakage
        config_data = yaml.load(fp_)

    if not config_data:
        return {}
    return config_data


def write_dynamic_config(opts, config_data):
    '''
    Writes configuration data to the dynamic configuation
    file.

    :param opts: Options dictionary used by Salt.
    :type opts: dict
    '''
    config_file = get_dynamic_conf_file_path(opts)

    with open(config_file, 'w') as fp_:  # pylint: disable=resource-leakage
        yaml.dump(config_data, fp_, default_flow_style=False)
