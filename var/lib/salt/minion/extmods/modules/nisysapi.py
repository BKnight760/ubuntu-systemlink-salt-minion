# -*- coding: utf-8 -*-
'''
A module for running nisysapi based actions.
'''
# Import python libs
from __future__ import absolute_import
import logging
import os
import os.path
import sys

# Import salt libs
# pylint: disable=import-error,3rd-party-module-not-gated
import salt.utils.platform
# pylint: enable=import-error,3rd-party-module-not-gated

# Import local libs
# This file may be loaded out of __pycache__, so the
# directory of its .py may not be in the search path.
IMPORT_PATH = os.path.dirname(__file__)
if IMPORT_PATH.endswith('__pycache__'):
    IMPORT_PATH = os.path.dirname(IMPORT_PATH)
sys.path.append(IMPORT_PATH)
try:
    from _nisysapi_ipc import query_minionagent  # pylint: disable=3rd-party-local-module-not-gated
    import _nisysmgmt_utils  # pylint: disable=3rd-party-local-module-not-gated
finally:
    # Remove the extra search path that we added to sys.path
    sys.path.remove(IMPORT_PATH)

# Define the module's virtual name
__virtualname__ = 'nisysapi'

# Used status codes
NISMS_STATUS_INTERNAL_ERROR = -2147418113

# Set up logging
log = logging.getLogger(__name__)


def __virtual__():
    '''
    Overwriting the cmd python module makes debugging modules
    with pdb a bit harder so lets do it this way instead.
    '''
    return __virtualname__


def _prepare_request_data(current_fun, args, kwargs, minion_id):
    '''
    Prepare the data that will be sent as a job request
    to the NI Minion Agent.
    '''
    fun = __virtualname__ + '.' + current_fun
    return {
        'fun': fun,
        'args': args,
        'kwargs': kwargs,
        'jid': kwargs['__pub_jid'],
        'id': minion_id
    }


def _generic_func_impl(current_fun, service_optional, args, kwargs):
    '''
    This is the generic function implementation
    that calls into the NI Minion Agent.

    Most top-level public APIs would call into this function.
    '''
    jid = kwargs['__pub_jid']
    minion_id = __grains__['id']
    log.info(
        '_generic_func_impl: minion_id = %s, '
        'jid = %s, fun = %s',
        minion_id, jid, kwargs['__pub_fun']
    )

    response = query_minionagent(
        _prepare_request_data(current_fun, args, kwargs, minion_id),
        service_optional
    )
    return response


def delete_resource(*args, **kwargs):
    '''
    Delete a given resource
    '''
    current_fun = sys._getframe().f_code.co_name  # pylint: disable=protected-access
    return _generic_func_impl(current_fun, False, args, kwargs)


def get_props(*args, **kwargs):
    '''
    Get System API properties
    '''
    current_fun = sys._getframe().f_code.co_name  # pylint: disable=protected-access
    return _generic_func_impl(current_fun, True, args, kwargs)


def populate_props(*args, **kwargs):
    '''
    Get specific System API properties
    '''
    current_fun = sys._getframe().f_code.co_name  # pylint: disable=protected-access
    return _generic_func_impl(current_fun, False, args, kwargs)


def set_props(*args, **kwargs):
    '''
    Set System API properties
    '''
    current_fun = sys._getframe().f_code.co_name  # pylint: disable=protected-access
    response = _generic_func_impl(current_fun, False, args, kwargs)

    should_restart_minion = False
    if 'networkSettingsChange' in response:
        should_restart_minion = response['networkSettingsChange']
        # Do not save 'networkSettingsChange' in the master.
        del response['networkSettingsChange']

    if should_restart_minion and not salt.utils.platform.is_windows():
        # The script that restarts the minion does not currently work on
        # Windows. SysApi doesn't typically support changing network settings
        # on Windows, but it is possible that an external expert might claim
        # that a property bag supports 'mxSysServiceType_LocalNetInterface' so
        # we keep the Windows check in place.
        result = _nisysmgmt_utils.restart_salt_minion(['--delay', '5'])
        if result is not None and result != 0:
            if response['status_code'] >= 0:
                response['status_code'] = NISMS_STATUS_INTERNAL_ERROR

    return response


def reset_device(*args, **kwargs):
    '''
    Reset a device
    '''
    current_fun = sys._getframe().f_code.co_name  # pylint: disable=protected-access
    return _generic_func_impl(current_fun, False, args, kwargs)


def self_cal(*args, **kwargs):
    '''
    Calibrate a device
    '''
    current_fun = sys._getframe().f_code.co_name  # pylint: disable=protected-access
    return _generic_func_impl(current_fun, False, args, kwargs)


def self_test(*args, **kwargs):
    '''
    Self-test a device
    '''
    current_fun = sys._getframe().f_code.co_name  # pylint: disable=protected-access
    return _generic_func_impl(current_fun, False, args, kwargs)
