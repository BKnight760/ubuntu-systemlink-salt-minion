#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
This script is used to register a minion to a master
'''
from __future__ import absolute_import

# Import python libs
import argparse  # pylint: disable=minimum-python-version
import os.path
import sys

# Import local libs
import _nisysmgmt_mutex  # pylint: disable=import-error,3rd-party-module-not-gated
import _nisysmgmt_utils

MUTEX_NAME = 'salt.modules.nisysmgmt'


class MasterListArgumentAction(argparse.Action):  # pylint: disable=too-few-public-methods
    '''
    Class that defines an action to take for the Master List
    from within 'argparse.ArgumentParser'.
    '''
    def __call__(self, parser, namespace, values, option_string=None):
        if isinstance(values, str):
            values = values.split(',')
        if 'master_list' in namespace:
            namespace.master_list.extend(values)
        else:
            setattr(namespace, 'master_list', values)


def parse_args():
    '''
    This will parse the command-line arguments passed in.
    Returns a dictionary of the parsed command-line arguments.

    The master and master-list arguments are stored in the same list to
    preserve order.
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--master',
        action='append',
        dest='master_list',
        default=[],
        help='An address of the salt-master to connect to. May also'
             'specify a master finger.'
    )
    parser.add_argument(
        '--master-list',
        action=MasterListArgumentAction,
        dest='master_list',
        default=[],
        help='A comma separated list of addresses of the salt-master to '
             'connect to. May also specify a master finger.'
    )
    parser.add_argument(
        '--master-finger',
        dest='master_finger',
        default='',
        type=str,
        help='Fingerprint of the master public key used to validate the '
             'identity of the Salt master before the initial key '
             'exchange. Must also specify a master or master list.'
    )
    args = parser.parse_args()

    new_master = _nisysmgmt_utils.uniquify_list(args.master_list)
    new_master_len = len(new_master)

    if new_master_len == 0:
        parser.print_help()
        sys.exit(1)

    return args


def main():
    '''
    This is the main entry point for this script.
    '''
    if not _nisysmgmt_utils.is_windows() and not _nisysmgmt_utils.is_linux():
        sys.stderr.write(
            '{0}: Unsupported platform. Only Windows and Linux are '
            'supported.'.format(
                os.path.basename(__file__)
            )
        )
        sys.exit(1)

    args = parse_args()

    mutex = _nisysmgmt_mutex.NamedMutex(MUTEX_NAME)
    with mutex:
        _nisysmgmt_utils.set_salt_minion_master_config(
            unregister=False,
            master_list=args.master_list,
            master_finger=args.master_finger
        )
        _nisysmgmt_utils.stop_minion_if_running()
        _nisysmgmt_utils.clear_pki_minion_master_cache()
        _nisysmgmt_utils.remove_skyline_master_file()
        _nisysmgmt_utils.remove_http_master_file()
        _nisysmgmt_utils.start_minion_if_not_running()

        sys.exit(0)


if __name__ == '__main__':
    main()
