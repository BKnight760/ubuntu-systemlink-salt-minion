# -*- coding: utf-8 -*-
'''
A module for generating an nisysmgmt based ID.
'''
from __future__ import absolute_import

# Import python libs
import logging
import os
import re
import sys
import uuid

# Import salt libs
# pylint: disable=import-error,3rd-party-module-not-gated
import salt.utils.platform
import salt.utils.stringutils
import salt.ext.six as six

# Import local libs
# This file may be loaded out of __pycache__, so the
# directory of its .py may not be in the search path.
IMPORT_PATH = os.path.dirname(__file__)
if IMPORT_PATH.endswith('__pycache__'):
    IMPORT_PATH = os.path.dirname(IMPORT_PATH)
sys.path.append(IMPORT_PATH)
try:
    import _nisysmgmt_grains
finally:
    # Remove the extra search path that we added to sys.path
    sys.path.remove(IMPORT_PATH)
# pylint: enable=import-error,3rd-party-module-not-gated

# Define the module's virtual name
__virtualname__ = 'nisysmgmt_id'

# Set up logging
log = logging.getLogger(__name__)


def __virtual__():
    return __virtualname__


def _get_mac_address_windows():
    '''
    Determine the MAC address of the non-virtual adapter with the lowest index.
    Windows version.

    :return: MAC address of the non-virtual adapter with the lowest index, or
        ``None`` if no non-virtual adapters exist.
    :rtype: str or None
    '''
    # Do not use salt.utils.network.interfaces() for Windows because there is
    # no easy way to filter out virtual adapters.
    # pylint: disable=import-error,3rd-party-local-module-not-gated
    import wmi
    from salt.utils.winapi import Com
    # pylint: enable=import-error,3rd-party-local-module-not-gated

    try:
        interfaces = {}

        with Com():
            wmi_obj = wmi.WMI()
            # Query with 'PhysicalAdapter=True' to filter out logical adapters
            for interface in wmi_obj.Win32_NetworkAdapter(PhysicalAdapter=True):
                if (interface.PNPDeviceID and interface.MACAddress and
                        interface.Index is not None):
                    interfaces[interface.Index] = {
                        'pnp_device_id': interface.PNPDeviceID,
                        'mac_address': interface.MACAddress
                    }
        for iface_address in sorted(interfaces.items(), key=lambda i: i[0]):
            if iface_address[1]['pnp_device_id'][:5] != 'ROOT\\':
                # Win32_NetworkAdapter.PNPDeviceID will have the prefix 'ROOT\'
                # for virtual adapters
                return iface_address[1]['mac_address']
    except Exception:  # pylint: disable=broad-except
        pass
    return None


def _get_mac_address_linux():
    '''
    Determine the MAC address of the system. ``eth0`` has preference if
    it exists, otherwise the first valid MAC address in the adapter list
    is returned.
    Linux version.

    :return: MAC address of the system or ``None`` if a valid MAC address is
        not found.
    :rtype: str or None
    '''
    import salt.utils.network as network  # pylint: disable=import-error,3rd-party-local-module-not-gated

    try:
        interfaces = network.interfaces()
        # 'eth0' has preference if it exists and has a valid MAC address.
        if 'eth0' in interfaces:
            hw_addr = interfaces['eth0'].get('hwaddr')
            if hw_addr and hw_addr != '00:00:00:00:00:00':
                return hw_addr.upper()
        # When 'eth0' doesn't exist, pick the first interface that has a valid
        # MAC address.
        for val in six.itervalues(interfaces):
            hw_addr = val.get('hwaddr')
            if hw_addr and hw_addr != '00:00:00:00:00:00':
                return hw_addr.upper()
    except Exception:  # pylint: disable=broad-except
        pass
    return None


def _get_mac_address():
    '''
    Determine the MAC address of the non-virtual adapter with the lowest index.

    :return: MAC address of the non-virtual adapter with the lowest index, or
        ``None`` if no non-virtual adapters exist.
    :rtype: str or None
    '''
    if salt.utils.platform.is_windows():
        return _get_mac_address_windows()
    elif salt.utils.platform.is_linux():
        return _get_mac_address_linux()
    else:
        raise RuntimeError('Unsupported platform')


def generate_id():
    '''
    Generate the ID.

    :return: The generated ID.
    :rtype: str
    '''
    # '__grains__' is defined by the framework
    # pylint: disable=undefined-variable
    product_name = _nisysmgmt_grains.get_grain_as_str(__grains__, 'productname').strip()
    if product_name == '':
        unique_id = str(uuid.uuid4())
        log.warning('Failed to format unique ID. Product name is not '
                    'available. As a fallback, assigning UUID "%s" as '
                    'unique ID.', unique_id)
        return unique_id

    serial_number = _nisysmgmt_grains.get_grain_as_str(__grains__, 'serialnumber').strip()
    mac_address = _get_mac_address()

    unique_id = product_name
    if serial_number != '':
        unique_id += '--SN-' + serial_number
    if mac_address is not None:
        unique_id += '--MAC-' + mac_address
    elif serial_number == '':
        unique_id += '--UUID-' + str(uuid.uuid4())
        log.warning('Serial number and MAC address are not available when '
                    'formatting unique ID. As a fallback, assigning "%s" as '
                    'unique ID.', unique_id)

    unique_id = unique_id.replace(' ', '_')
    unique_id = unique_id.replace('.', '_')
    unique_id = re.sub(
        r'([^0-9A-Za-z\-_])+',
        '-',
        unique_id
    )
    return unique_id
