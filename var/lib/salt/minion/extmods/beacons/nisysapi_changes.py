# -*- coding: utf-8 -*-
'''
National Instruments System API Beacon to react to changes in nisysapi data
'''
from __future__ import absolute_import

# Import Python libs
import logging
import os.path
import sys

# Import salt libs
# pylint: disable=import-error,3rd-party-module-not-gated
import salt.utils.event
# pylint: enable=import-error,3rd-party-module-not-gated

log = logging.getLogger(__name__)

__virtualname__ = 'nisysapi_changes'

# Placeholder for '_nisysapi_ipc' module that will be loaded
# in __virtual__ (when '__opts__' are available).
_nisysapi_ipc = None  # pylint: disable=invalid-name
EVENT = None


def __virtual__():
    global _nisysapi_ipc  # pylint: disable=global-statement,invalid-name

    # Add extra search paths to load '_nisysapi_ipc'
    paths_to_add = __opts__['module_dirs']
    extmods_module_dir = os.path.join(__opts__['extension_modules'], 'modules')
    if extmods_module_dir not in paths_to_add:
        paths_to_add.append(extmods_module_dir)
    sys.path.extend(paths_to_add)
    try:
        import _nisysapi_ipc  # pylint: disable=redefined-outer-name,import-error,3rd-party-local-module-not-gated
    finally:
        # Remove the extra search paths that we added to
        # sys.path
        for path in paths_to_add:
            sys.path.remove(path)

    return __virtualname__


def validate(config):
    '''
    Validate the beacon configuration
    '''
    if not isinstance(config, list):
        return False, ('Configuration for nisysapi_changes '
                       'beacon must be a list.')
    return True, 'Valid beacon configuration'


def beacon(config):  # pylint: disable=unused-argument
    '''
    Check to see if any data managed by the NI System API has changed.

    If any such changes are detected, notify the master by sending the
    updated data in an event.

    Example Config

    .. code-block:: yaml

       beacons:
         nisysapi_changed:
           - interval: 15
    '''
    global EVENT  # pylint: disable=global-statement

    try:
        refresh_cache = False

        minion_id = __grains__['id']

        request = {
            'fun': 'nisysapi.props_changed',
            'args': [],
            'kwargs': {},
            'jid': '0',
            'id': minion_id
        }

        response = _nisysapi_ipc.query_minionagent(request, False, connect_timeout=1)
        if (isinstance(response, dict) and
                response.get('status_code', -1) >= 0 and
                response.get('props_changed', False) is True):
            refresh_cache = True

        if refresh_cache is True:
            request = {
                'fun': 'nisysapi.get_props',
                'args': [],
                'kwargs': {},
                'jid': '0',
                'id': minion_id
            }

            response = _nisysapi_ipc.query_minionagent(request, False)
            if (isinstance(response, dict) and
                    response.get('status_code', -1) >= 0 and
                    'resources' in response and
                    isinstance(response['resources'], list)):
                tag = 'nisysmgmt/sysapi/update/' + minion_id
                event_data = {
                    'id': minion_id,
                    'data': response['resources']
                }

                if not EVENT:
                    EVENT = salt.utils.event.get_event(
                        'minion', opts=__opts__, listen=False
                    )

                EVENT.fire_master(event_data, tag)
    except Exception as exc:  # pylint: disable=broad-except
        log.error(
            'Unexpected exception in the "nisysapi_changes" beacon: %s',
            exc, exc_info=True
        )

    # Always return an empty list so that nothing is sent to the master.
    return []
