# -*- coding: utf-8 -*-
'''
National Instruments Systems Management Beacon to run
initialization code during minion startup.
'''
from __future__ import absolute_import

# Import Python libs
import logging
import os
import os.path
import socket
import time
import sys

# Import salt libs
# pylint: disable=import-error,3rd-party-module-not-gated
import salt.utils.platform
# pylint: enable=import-error,3rd-party-module-not-gated

if salt.utils.platform.is_windows():
    # This file may be loaded out of __pycache__, so the
    # directory of its .py may not be in the search path.
    IMPORT_PATH = os.path.dirname(__file__)
    if IMPORT_PATH.endswith('__pycache__'):
        IMPORT_PATH = os.path.dirname(IMPORT_PATH)
    sys.path.append(IMPORT_PATH)
    try:
        import _nisysmgmt_local_master
    finally:
        # Remove the extra search path that we added to sys.path
        sys.path.remove(IMPORT_PATH)

# Set up logging
log = logging.getLogger(__name__)

__virtualname__ = 'nisysmgmt_startup'


def __virtual__():
    return __virtualname__


def _wait_for_network():
    '''
    Pause until the network is up or 10 seconds has elapsed,
    whichever happens first.
    '''
    attempts = 0
    initial_time = time.time()

    while True:
        try:
            local_ip = socket.gethostbyname(socket.gethostname())
        except Exception as exc:  # pylint: disable=broad-except
            log.warning(
                'Exception occurred when trying to detect network: %s', exc
            )
            local_ip = '127.0.0.1'

        if local_ip != '127.0.0.1':
            break
        attempts += 1
        if (attempts == 10) or (time.time() - initial_time > 10):
            log.warning('Network not detected after 10 seconds. Continuing.')
            break
        log.debug('Attempt #%d did not detect network', attempts)
        time.sleep(1)


def validate(config):
    '''
    Validate the beacon configuration
    '''
    if not isinstance(config, list):
        return False, ('Configuration for nisysmgmt_startup '
                       'beacon must be a list.')
    return True, 'Valid beacon configuration'


def beacon(config):
    '''
    Run initialization code during minion startup.

    Example Config

    .. code-block:: yaml

       beacons:
         nisysmgmt_startup:
           - run_once: true
    '''
    try:
        if salt.utils.platform.is_linux():
            _wait_for_network()
            os.environ['PATH'] += os.pathsep + '/usr/local/bin'
        elif salt.utils.platform.is_windows():
            _nisysmgmt_local_master.setup_local_salt_master(__opts__, __grains__)
    except Exception as exc:  # pylint: disable=broad-except
        log.error(
            'Unexpected exception in the "nisysmgmt_startup" beacon: %s',
            exc, exc_info=True
        )

    # Always return an empty list so that nothing is sent to the master.
    return []
