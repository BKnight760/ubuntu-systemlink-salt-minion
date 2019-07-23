# -*- coding: utf-8 -*-
# DO NOT EDIT! This file is auto-generated.
"""
Classes for SystemLink Message Bus usage.
"""
from __future__ import absolute_import

# Import python libs
import json
import sys
from datetime import datetime  # pylint: disable=unused-import

# Import local libs
# pylint: disable=import-error
from systemlink.messagebus.broadcast_message import BroadcastMessage  # pylint: disable=unused-import
from systemlink.messagebus.datetime import from_datetime, to_datetime  # pylint: disable=unused-import
from systemlink.messagebus.message_header import (  # pylint: disable=unused-import
    MessageHeader, JSON_MESSAGE_CONTENT_TYPE, BINARY_MESSAGE_CONTENT_TYPE)
from systemlink.messagebus.message_base import MessageBase
from systemlink.messagebus.request_message import RequestMessage  # pylint: disable=unused-import
from systemlink.messagebus.response_message import ResponseMessage  # pylint: disable=unused-import
from systemlink.messagebus.routed_message import RoutedMessage  # pylint: disable=unused-import
# pylint: enable=import-error

if sys.version_info[0] >= 3:
    long = int  # pylint: disable=redefined-builtin,invalid-name


_PASS_THROUGH_TYPES = {
    'bool',
    'bytearray',
    'float',
    'int',
    'long',
    'object',
    'str'
}

_PRIMITIVE_TYPES = {
    'bool': bool,
    'bytearray': bytearray,
    'datetime': datetime,
    'dict': dict,
    'float': float,
    'int': int,
    'list': list,
    'long': long,
    'object': object,
    'str': str
}


def _str_to_type(type_name):
    """
    Convert a type name to a type.

    :param type_name: The name of the type.
    :type type_name: str
    :return: The corresponding type.
    :rtype: type
    """
    type_ = _PRIMITIVE_TYPES.get(type_name)
    if type_ is not None:
        return type_
    return getattr(sys.modules[__name__], type_name)


def _deserialize(value, type_name):  # pylint: disable=too-many-return-statements,too-many-branches
    """
    Deserialize a value from a Python native type.

    :param value: The value to deserialize.
    :type value: object
    :param type_name: The name of the type of `value``.
    :type type_name: str
    :return: The deserialized object.
    :rtype: object
    """
    if value is None:
        return None
    if not type_name:
        return value
    if type_name.endswith(')'):
        sep_index = type_name.find('(')
        sub_type_name = type_name[sep_index+1:-1]
        type_name = type_name[:sep_index]
        if type_name == 'list':
            if sub_type_name in _PASS_THROUGH_TYPES:
                return value
            return [_deserialize(item, sub_type_name) for item in value]
        assert type_name == 'dict'
        sep_index = sub_type_name.find(',')
        key_type_name = sub_type_name[:sep_index]
        value_type_name = sub_type_name[sep_index+1:].strip()
        if key_type_name in _PASS_THROUGH_TYPES and value_type_name in _PASS_THROUGH_TYPES:
            return value
        new_dict = {}
        for dict_key, dict_value in value.items():
            new_dict[_deserialize(dict_key, key_type_name)] = _deserialize(
                dict_value, value_type_name
            )
        return new_dict
    if type_name in _PASS_THROUGH_TYPES:
        return value
    type_ = _str_to_type(type_name)
    if type_ == datetime:
        if not isinstance(value, datetime):
            return to_datetime(value)
        return value
    if hasattr(type_, 'from_dict'):
        return type_.from_dict(value)
    if hasattr(type_, 'from_string'):
        if isinstance(value, int):
            return type_(value)
        return type_.from_string(value)
    if hasattr(type_, 'from_list'):
        if isinstance(value, int):
            return type_(value)
        return type_.from_list(value)
    return value


def _serialize(value):  # pylint: disable=too-many-return-statements
    """
    Serialize a value to a Python native type.

    :param value: The value to serialize.
    :type value: object
    :return: The serialized object.
    :rtype: object
    """
    if value is None:
        return None
    if isinstance(value, list):
        return [_serialize(item) for item in value]
    if isinstance(value, dict):
        new_dict = {}
        for dict_key, dict_value in value.items():
            new_dict[_serialize(dict_key)] = _serialize(dict_value)
        return new_dict
    if isinstance(value, datetime):
        return from_datetime(value)
    if hasattr(value, 'to_dict'):
        return value.to_dict()
    if hasattr(value, 'to_string'):
        return value.to_string()
    if hasattr(value, 'to_list'):
        return value.to_list()
    return value


# pylint: disable=line-too-long,too-many-lines,too-many-instance-attributes,too-many-arguments,too-many-locals,useless-object-inheritance


#
# AssetPerformanceManagementMessageObjects namespace
#


class BusType(object):  # pylint: disable=too-few-public-methods
    """
    BusType normal enum.
    """
    BUILT_IN_SYSTEM = 0
    PCI_PXI = 1
    USB = 2
    GPIB = 3
    VXI = 4
    SERIAL = 5
    TCP_IP = 6
    CRIO = 7
    SCXI = 8
    CDAQ = 9
    SWITCH_BLOCK = 10
    SCC = 11
    FIRE_WIRE = 12
    ACCESSORY = 13
    CAN = 14
    SWITCH_BLOCK_DEVICE = 15
    _INT_TO_STRING = {
        0: 'BUILT_IN_SYSTEM',
        1: 'PCI_PXI',
        2: 'USB',
        3: 'GPIB',
        4: 'VXI',
        5: 'SERIAL',
        6: 'TCP_IP',
        7: 'CRIO',
        8: 'SCXI',
        9: 'CDAQ',
        10: 'SWITCH_BLOCK',
        11: 'SCC',
        12: 'FIRE_WIRE',
        13: 'ACCESSORY',
        14: 'CAN',
        15: 'SWITCH_BLOCK_DEVICE'
    }
    _STRING_TO_INT = {
        'BUILT_IN_SYSTEM': 0,
        'PCI_PXI': 1,
        'USB': 2,
        'GPIB': 3,
        'VXI': 4,
        'SERIAL': 5,
        'TCP_IP': 6,
        'CRIO': 7,
        'SCXI': 8,
        'CDAQ': 9,
        'SWITCH_BLOCK': 10,
        'SCC': 11,
        'FIRE_WIRE': 12,
        'ACCESSORY': 13,
        'CAN': 14,
        'SWITCH_BLOCK_DEVICE': 15
    }

    def __init__(self, value):
        """
        :param value: The integer value of the enum.
        :type value: int
        """
        self._value = value

    @property
    def value(self):
        """
        Get integer value of the enum.

        :return: The integer value of the enum.
        :rtype: int
        """
        return self._value

    @value.setter
    def value(self, value):
        """
        Set integer value of the enum.

        :param value: The integer value of the enum.
        :type value: int
        """
        self._value = value

    @classmethod
    def from_string(cls, value_string):
        """
        Create a new instance of :class:`BusType` using a string.

        :param value_string: The string value of the enum.
        :type value_string: str
        :return: A new instance of :class:`BusType`.
        :rtype: BusType
        """
        if value_string is None:
            return None
        value = cls._STRING_TO_INT[value_string]
        return cls(value)

    def to_string(self):
        """
        Returns a string representing the enum.

        :return: A string representing the enum.
        :rtype: str
        """
        return self._INT_TO_STRING[self._value]

    def __str__(self):
        """
        Returns a string representing the enum.

        :return: A string representing the enum.
        :rtype: str
        """
        return self.to_string()


class SystemConnectionState(object):  # pylint: disable=too-few-public-methods
    """
    SystemConnectionState normal enum.
    """
    APPROVED = 0
    DISCONNECTED = 1
    CONNECTED_UPDATE_PENDING = 2
    CONNECTED_UPDATE_SUCCESSFUL = 3
    CONNECTED_UPDATE_FAILED = 4
    UNSUPPORTED = 5
    ACTIVATED = 6
    _INT_TO_STRING = {
        0: 'APPROVED',
        1: 'DISCONNECTED',
        2: 'CONNECTED_UPDATE_PENDING',
        3: 'CONNECTED_UPDATE_SUCCESSFUL',
        4: 'CONNECTED_UPDATE_FAILED',
        5: 'UNSUPPORTED',
        6: 'ACTIVATED'
    }
    _STRING_TO_INT = {
        'APPROVED': 0,
        'DISCONNECTED': 1,
        'CONNECTED_UPDATE_PENDING': 2,
        'CONNECTED_UPDATE_SUCCESSFUL': 3,
        'CONNECTED_UPDATE_FAILED': 4,
        'UNSUPPORTED': 5,
        'ACTIVATED': 6
    }

    def __init__(self, value):
        """
        :param value: The integer value of the enum.
        :type value: int
        """
        self._value = value

    @property
    def value(self):
        """
        Get integer value of the enum.

        :return: The integer value of the enum.
        :rtype: int
        """
        return self._value

    @value.setter
    def value(self, value):
        """
        Set integer value of the enum.

        :param value: The integer value of the enum.
        :type value: int
        """
        self._value = value

    @classmethod
    def from_string(cls, value_string):
        """
        Create a new instance of :class:`SystemConnectionState` using a string.

        :param value_string: The string value of the enum.
        :type value_string: str
        :return: A new instance of :class:`SystemConnectionState`.
        :rtype: SystemConnectionState
        """
        if value_string is None:
            return None
        value = cls._STRING_TO_INT[value_string]
        return cls(value)

    def to_string(self):
        """
        Returns a string representing the enum.

        :return: A string representing the enum.
        :rtype: str
        """
        return self._INT_TO_STRING[self._value]

    def __str__(self):
        """
        Returns a string representing the enum.

        :return: A string representing the enum.
        :rtype: str
        """
        return self.to_string()


class AssetPresenceStatus(object):  # pylint: disable=too-few-public-methods
    """
    AssetPresenceStatus normal enum.
    """
    INITIALIZING = -2
    UNKNOWN = -1
    NOT_PRESENT = 0
    PRESENT = 1
    _INT_TO_STRING = {
        -2: 'INITIALIZING',
        -1: 'UNKNOWN',
        0: 'NOT_PRESENT',
        1: 'PRESENT'
    }
    _STRING_TO_INT = {
        'INITIALIZING': -2,
        'UNKNOWN': -1,
        'NOT_PRESENT': 0,
        'PRESENT': 1
    }

    def __init__(self, value):
        """
        :param value: The integer value of the enum.
        :type value: int
        """
        self._value = value

    @property
    def value(self):
        """
        Get integer value of the enum.

        :return: The integer value of the enum.
        :rtype: int
        """
        return self._value

    @value.setter
    def value(self, value):
        """
        Set integer value of the enum.

        :param value: The integer value of the enum.
        :type value: int
        """
        self._value = value

    @classmethod
    def from_string(cls, value_string):
        """
        Create a new instance of :class:`AssetPresenceStatus` using a string.

        :param value_string: The string value of the enum.
        :type value_string: str
        :return: A new instance of :class:`AssetPresenceStatus`.
        :rtype: AssetPresenceStatus
        """
        if value_string is None:
            return None
        value = cls._STRING_TO_INT[value_string]
        return cls(value)

    def to_string(self):
        """
        Returns a string representing the enum.

        :return: A string representing the enum.
        :rtype: str
        """
        return self._INT_TO_STRING[self._value]

    def __str__(self):
        """
        Returns a string representing the enum.

        :return: A string representing the enum.
        :rtype: str
        """
        return self.to_string()


class CalibrationMode(object):  # pylint: disable=too-few-public-methods
    """
    CalibrationMode normal enum.
    """
    AUTOMATIC = 0
    MANUAL = 1
    _INT_TO_STRING = {
        0: 'AUTOMATIC',
        1: 'MANUAL'
    }
    _STRING_TO_INT = {
        'AUTOMATIC': 0,
        'MANUAL': 1
    }

    def __init__(self, value):
        """
        :param value: The integer value of the enum.
        :type value: int
        """
        self._value = value

    @property
    def value(self):
        """
        Get integer value of the enum.

        :return: The integer value of the enum.
        :rtype: int
        """
        return self._value

    @value.setter
    def value(self, value):
        """
        Set integer value of the enum.

        :param value: The integer value of the enum.
        :type value: int
        """
        self._value = value

    @classmethod
    def from_string(cls, value_string):
        """
        Create a new instance of :class:`CalibrationMode` using a string.

        :param value_string: The string value of the enum.
        :type value_string: str
        :return: A new instance of :class:`CalibrationMode`.
        :rtype: CalibrationMode
        """
        if value_string is None:
            return None
        value = cls._STRING_TO_INT[value_string]
        return cls(value)

    def to_string(self):
        """
        Returns a string representing the enum.

        :return: A string representing the enum.
        :rtype: str
        """
        return self._INT_TO_STRING[self._value]

    def __str__(self):
        """
        Returns a string representing the enum.

        :return: A string representing the enum.
        :rtype: str
        """
        return self.to_string()


class CalibrationStatus(object):  # pylint: disable=too-few-public-methods
    """
    CalibrationStatus normal enum.
    """
    OK = 0
    APPROACHING_RECOMMENDED_DUE_DATE = 1
    PAST_RECOMMENDED_DUE_DATE = 2
    _INT_TO_STRING = {
        0: 'OK',
        1: 'APPROACHING_RECOMMENDED_DUE_DATE',
        2: 'PAST_RECOMMENDED_DUE_DATE'
    }
    _STRING_TO_INT = {
        'OK': 0,
        'APPROACHING_RECOMMENDED_DUE_DATE': 1,
        'PAST_RECOMMENDED_DUE_DATE': 2
    }

    def __init__(self, value):
        """
        :param value: The integer value of the enum.
        :type value: int
        """
        self._value = value

    @property
    def value(self):
        """
        Get integer value of the enum.

        :return: The integer value of the enum.
        :rtype: int
        """
        return self._value

    @value.setter
    def value(self, value):
        """
        Set integer value of the enum.

        :param value: The integer value of the enum.
        :type value: int
        """
        self._value = value

    @classmethod
    def from_string(cls, value_string):
        """
        Create a new instance of :class:`CalibrationStatus` using a string.

        :param value_string: The string value of the enum.
        :type value_string: str
        :return: A new instance of :class:`CalibrationStatus`.
        :rtype: CalibrationStatus
        """
        if value_string is None:
            return None
        value = cls._STRING_TO_INT[value_string]
        return cls(value)

    def to_string(self):
        """
        Returns a string representing the enum.

        :return: A string representing the enum.
        :rtype: str
        """
        return self._INT_TO_STRING[self._value]

    def __str__(self):
        """
        Returns a string representing the enum.

        :return: A string representing the enum.
        :rtype: str
        """
        return self.to_string()


class QueryOperator(object):  # pylint: disable=too-few-public-methods
    """
    QueryOperator normal enum.
    """
    CONTAINS = 0
    NOT_CONTAINS = 1
    EQUAL = 2
    NOT_EQUAL = 3
    LESS_THAN = 4
    GREATER_THAN = 5
    LESS_THAN_OR_EQUAL = 6
    GREATER_THAN_OR_EQUAL = 7
    _INT_TO_STRING = {
        0: 'CONTAINS',
        1: 'NOT_CONTAINS',
        2: 'EQUAL',
        3: 'NOT_EQUAL',
        4: 'LESS_THAN',
        5: 'GREATER_THAN',
        6: 'LESS_THAN_OR_EQUAL',
        7: 'GREATER_THAN_OR_EQUAL'
    }
    _STRING_TO_INT = {
        'CONTAINS': 0,
        'NOT_CONTAINS': 1,
        'EQUAL': 2,
        'NOT_EQUAL': 3,
        'LESS_THAN': 4,
        'GREATER_THAN': 5,
        'LESS_THAN_OR_EQUAL': 6,
        'GREATER_THAN_OR_EQUAL': 7
    }

    def __init__(self, value):
        """
        :param value: The integer value of the enum.
        :type value: int
        """
        self._value = value

    @property
    def value(self):
        """
        Get integer value of the enum.

        :return: The integer value of the enum.
        :rtype: int
        """
        return self._value

    @value.setter
    def value(self, value):
        """
        Set integer value of the enum.

        :param value: The integer value of the enum.
        :type value: int
        """
        self._value = value

    @classmethod
    def from_string(cls, value_string):
        """
        Create a new instance of :class:`QueryOperator` using a string.

        :param value_string: The string value of the enum.
        :type value_string: str
        :return: A new instance of :class:`QueryOperator`.
        :rtype: QueryOperator
        """
        if value_string is None:
            return None
        value = cls._STRING_TO_INT[value_string]
        return cls(value)

    def to_string(self):
        """
        Returns a string representing the enum.

        :return: A string representing the enum.
        :rtype: str
        """
        return self._INT_TO_STRING[self._value]

    def __str__(self):
        """
        Returns a string representing the enum.

        :return: A string representing the enum.
        :rtype: str
        """
        return self.to_string()


class AssetState(object):
    """
    AssetState custom data type.
    """
    def __init__(self,
                 system_connection_=None,
                 asset_presence_=None):
        """
        :param system_connection_: system_connection
        :type system_connection_: SystemConnectionState
        :param asset_presence_: asset_presence
        :type asset_presence_: AssetPresenceStatus
        """
        self.system_connection = system_connection_
        self.asset_presence = asset_presence_

    @classmethod
    def from_dict(cls, body_dict):
        """
        Create a new instance of :class:`AssetState` using a dictionary.

        :param body_dict: A dictionary representing the body.
        :type body_dict: dict
        :return: A new instance of :class:`AssetState`.
        :rtype: AssetState
        """
        system_connection_ = _deserialize(body_dict.get('systemConnection'), 'SystemConnectionState')
        asset_presence_ = _deserialize(body_dict.get('assetPresence'), 'AssetPresenceStatus')
        return cls(
            system_connection_=system_connection_,
            asset_presence_=asset_presence_
        )

    @classmethod
    def from_json(cls, body_json):
        """
        Create a new instance of :class:`AssetState` using a JSON string.

        :param body_json: A string in JSON format representing the body.
        :type body_json: str
        :return: A new instance of :class:`AssetState`.
        :rtype: AssetState
        """
        body_dict = json.loads(body_json)
        return cls.from_dict(body_dict)

    @classmethod
    def from_body_bytes(cls, body_bytes):
        """
        Create a new instance of :class:`AssetState` using a body
        of type :class:`bytes` or :class:`bytearray`.

        :param body_bytes: The body to use.
        :type body_bytes: bytes or bytearray
        :return: A new instance of :class:`AssetState`.
        :rtype: AssetState
        """
        body_json = str(body_bytes, 'utf-8')
        return cls.from_json(body_json)

    def to_dict(self):
        """
        Returns a dictionary representing the data in this object.

        :return: A dictionary representing the data in this object.
        :rtype: dict
        """
        system_connection_ = _serialize(self.system_connection)
        asset_presence_ = _serialize(self.asset_presence)
        return {
            'systemConnection': system_connection_,
            'assetPresence': asset_presence_
        }

    def to_json(self):
        """
        Returns a JSON string representing the data in this object.

        :return: A JSON string representing the data in this object.
        :rtype: str
        """
        body_dict = self.to_dict()
        return json.dumps(body_dict, separators=(',', ':'))

    def to_body_bytes(self):
        """
        Returns a :class:`bytearray` body representing the data in this object.

        :return: A :class:`bytearray` body representing the data in this object.
        :rtype: bytearray
        """
        body_json = self.to_json()
        return bytearray(body_json, 'utf-8')


class AssetLocation(object):
    """
    AssetLocation custom data type.
    """
    def __init__(self,
                 minion_id_=None,
                 parent_=None,
                 resource_uri_=None,
                 slot_number_=None,
                 system_name_=None,
                 state_=None):
        """
        :param minion_id_: minion_id
        :type minion_id_: str
        :param parent_: parent
        :type parent_: str
        :param resource_uri_: resource_uri
        :type resource_uri_: str
        :param slot_number_: slot_number
        :type slot_number_: int
        :param system_name_: system_name
        :type system_name_: str
        :param state_: state
        :type state_: AssetState
        """
        self.minion_id = minion_id_
        self.parent = parent_
        self.resource_uri = resource_uri_
        self.slot_number = slot_number_
        self.system_name = system_name_
        self.state = state_

    @classmethod
    def from_dict(cls, body_dict):
        """
        Create a new instance of :class:`AssetLocation` using a dictionary.

        :param body_dict: A dictionary representing the body.
        :type body_dict: dict
        :return: A new instance of :class:`AssetLocation`.
        :rtype: AssetLocation
        """
        minion_id_ = _deserialize(body_dict.get('minionId'), 'str')
        parent_ = _deserialize(body_dict.get('parent'), 'str')
        resource_uri_ = _deserialize(body_dict.get('resourceUri'), 'str')
        slot_number_ = _deserialize(body_dict.get('slotNumber'), 'int')
        system_name_ = _deserialize(body_dict.get('systemName'), 'str')
        state_ = _deserialize(body_dict.get('state'), 'AssetState')
        return cls(
            minion_id_=minion_id_,
            parent_=parent_,
            resource_uri_=resource_uri_,
            slot_number_=slot_number_,
            system_name_=system_name_,
            state_=state_
        )

    @classmethod
    def from_json(cls, body_json):
        """
        Create a new instance of :class:`AssetLocation` using a JSON string.

        :param body_json: A string in JSON format representing the body.
        :type body_json: str
        :return: A new instance of :class:`AssetLocation`.
        :rtype: AssetLocation
        """
        body_dict = json.loads(body_json)
        return cls.from_dict(body_dict)

    @classmethod
    def from_body_bytes(cls, body_bytes):
        """
        Create a new instance of :class:`AssetLocation` using a body
        of type :class:`bytes` or :class:`bytearray`.

        :param body_bytes: The body to use.
        :type body_bytes: bytes or bytearray
        :return: A new instance of :class:`AssetLocation`.
        :rtype: AssetLocation
        """
        body_json = str(body_bytes, 'utf-8')
        return cls.from_json(body_json)

    def to_dict(self):
        """
        Returns a dictionary representing the data in this object.

        :return: A dictionary representing the data in this object.
        :rtype: dict
        """
        minion_id_ = _serialize(self.minion_id)
        parent_ = _serialize(self.parent)
        resource_uri_ = _serialize(self.resource_uri)
        slot_number_ = _serialize(self.slot_number)
        system_name_ = _serialize(self.system_name)
        state_ = _serialize(self.state)
        return {
            'minionId': minion_id_,
            'parent': parent_,
            'resourceUri': resource_uri_,
            'slotNumber': slot_number_,
            'systemName': system_name_,
            'state': state_
        }

    def to_json(self):
        """
        Returns a JSON string representing the data in this object.

        :return: A JSON string representing the data in this object.
        :rtype: str
        """
        body_dict = self.to_dict()
        return json.dumps(body_dict, separators=(',', ':'))

    def to_body_bytes(self):
        """
        Returns a :class:`bytearray` body representing the data in this object.

        :return: A :class:`bytearray` body representing the data in this object.
        :rtype: bytearray
        """
        body_json = self.to_json()
        return bytearray(body_json, 'utf-8')


class TemperatureSensor(object):
    """
    TemperatureSensor custom data type.
    """
    def __init__(self,
                 name_=None,
                 reading_=None):
        """
        :param name_: name
        :type name_: str
        :param reading_: reading
        :type reading_: float
        """
        self.name = name_
        self.reading = reading_

    @classmethod
    def from_dict(cls, body_dict):
        """
        Create a new instance of :class:`TemperatureSensor` using a dictionary.

        :param body_dict: A dictionary representing the body.
        :type body_dict: dict
        :return: A new instance of :class:`TemperatureSensor`.
        :rtype: TemperatureSensor
        """
        name_ = _deserialize(body_dict.get('name'), 'str')
        reading_ = _deserialize(body_dict.get('reading'), 'float')
        return cls(
            name_=name_,
            reading_=reading_
        )

    @classmethod
    def from_json(cls, body_json):
        """
        Create a new instance of :class:`TemperatureSensor` using a JSON string.

        :param body_json: A string in JSON format representing the body.
        :type body_json: str
        :return: A new instance of :class:`TemperatureSensor`.
        :rtype: TemperatureSensor
        """
        body_dict = json.loads(body_json)
        return cls.from_dict(body_dict)

    @classmethod
    def from_body_bytes(cls, body_bytes):
        """
        Create a new instance of :class:`TemperatureSensor` using a body
        of type :class:`bytes` or :class:`bytearray`.

        :param body_bytes: The body to use.
        :type body_bytes: bytes or bytearray
        :return: A new instance of :class:`TemperatureSensor`.
        :rtype: TemperatureSensor
        """
        body_json = str(body_bytes, 'utf-8')
        return cls.from_json(body_json)

    def to_dict(self):
        """
        Returns a dictionary representing the data in this object.

        :return: A dictionary representing the data in this object.
        :rtype: dict
        """
        name_ = _serialize(self.name)
        reading_ = _serialize(self.reading)
        return {
            'name': name_,
            'reading': reading_
        }

    def to_json(self):
        """
        Returns a JSON string representing the data in this object.

        :return: A JSON string representing the data in this object.
        :rtype: str
        """
        body_dict = self.to_dict()
        return json.dumps(body_dict, separators=(',', ':'))

    def to_body_bytes(self):
        """
        Returns a :class:`bytearray` body representing the data in this object.

        :return: A :class:`bytearray` body representing the data in this object.
        :rtype: bytearray
        """
        body_json = self.to_json()
        return bytearray(body_json, 'utf-8')


class SelfCalibrationModel(object):
    """
    SelfCalibrationModel custom data type.
    """
    def __init__(self,
                 temperature_sensors_=None,
                 is_limited_=None,
                 date_=None):
        """
        :param temperature_sensors_: temperature_sensors
        :type temperature_sensors_: list(TemperatureSensor)
        :param is_limited_: is_limited
        :type is_limited_: bool
        :param date_: date
        :type date_: datetime
        """
        self.temperature_sensors = temperature_sensors_
        self.is_limited = is_limited_
        self.date = date_

    @classmethod
    def from_dict(cls, body_dict):
        """
        Create a new instance of :class:`SelfCalibrationModel` using a dictionary.

        :param body_dict: A dictionary representing the body.
        :type body_dict: dict
        :return: A new instance of :class:`SelfCalibrationModel`.
        :rtype: SelfCalibrationModel
        """
        temperature_sensors_ = _deserialize(body_dict.get('temperatureSensors'), 'list(TemperatureSensor)')
        is_limited_ = _deserialize(body_dict.get('isLimited'), 'bool')
        date_ = _deserialize(body_dict.get('date'), 'datetime')
        return cls(
            temperature_sensors_=temperature_sensors_,
            is_limited_=is_limited_,
            date_=date_
        )

    @classmethod
    def from_json(cls, body_json):
        """
        Create a new instance of :class:`SelfCalibrationModel` using a JSON string.

        :param body_json: A string in JSON format representing the body.
        :type body_json: str
        :return: A new instance of :class:`SelfCalibrationModel`.
        :rtype: SelfCalibrationModel
        """
        body_dict = json.loads(body_json)
        return cls.from_dict(body_dict)

    @classmethod
    def from_body_bytes(cls, body_bytes):
        """
        Create a new instance of :class:`SelfCalibrationModel` using a body
        of type :class:`bytes` or :class:`bytearray`.

        :param body_bytes: The body to use.
        :type body_bytes: bytes or bytearray
        :return: A new instance of :class:`SelfCalibrationModel`.
        :rtype: SelfCalibrationModel
        """
        body_json = str(body_bytes, 'utf-8')
        return cls.from_json(body_json)

    def to_dict(self):
        """
        Returns a dictionary representing the data in this object.

        :return: A dictionary representing the data in this object.
        :rtype: dict
        """
        temperature_sensors_ = _serialize(self.temperature_sensors)
        is_limited_ = _serialize(self.is_limited)
        date_ = _serialize(self.date)
        return {
            'temperatureSensors': temperature_sensors_,
            'isLimited': is_limited_,
            'date': date_
        }

    def to_json(self):
        """
        Returns a JSON string representing the data in this object.

        :return: A JSON string representing the data in this object.
        :rtype: str
        """
        body_dict = self.to_dict()
        return json.dumps(body_dict, separators=(',', ':'))

    def to_body_bytes(self):
        """
        Returns a :class:`bytearray` body representing the data in this object.

        :return: A :class:`bytearray` body representing the data in this object.
        :rtype: bytearray
        """
        body_json = self.to_json()
        return bytearray(body_json, 'utf-8')


class CalibrationOperator(object):
    """
    CalibrationOperator custom data type.
    """
    def __init__(self,
                 display_name_=None,
                 user_id_=None):
        """
        :param display_name_: display_name
        :type display_name_: str
        :param user_id_: user_id
        :type user_id_: str
        """
        self.display_name = display_name_
        self.user_id = user_id_

    @classmethod
    def from_dict(cls, body_dict):
        """
        Create a new instance of :class:`CalibrationOperator` using a dictionary.

        :param body_dict: A dictionary representing the body.
        :type body_dict: dict
        :return: A new instance of :class:`CalibrationOperator`.
        :rtype: CalibrationOperator
        """
        display_name_ = _deserialize(body_dict.get('displayName'), 'str')
        user_id_ = _deserialize(body_dict.get('userId'), 'str')
        return cls(
            display_name_=display_name_,
            user_id_=user_id_
        )

    @classmethod
    def from_json(cls, body_json):
        """
        Create a new instance of :class:`CalibrationOperator` using a JSON string.

        :param body_json: A string in JSON format representing the body.
        :type body_json: str
        :return: A new instance of :class:`CalibrationOperator`.
        :rtype: CalibrationOperator
        """
        body_dict = json.loads(body_json)
        return cls.from_dict(body_dict)

    @classmethod
    def from_body_bytes(cls, body_bytes):
        """
        Create a new instance of :class:`CalibrationOperator` using a body
        of type :class:`bytes` or :class:`bytearray`.

        :param body_bytes: The body to use.
        :type body_bytes: bytes or bytearray
        :return: A new instance of :class:`CalibrationOperator`.
        :rtype: CalibrationOperator
        """
        body_json = str(body_bytes, 'utf-8')
        return cls.from_json(body_json)

    def to_dict(self):
        """
        Returns a dictionary representing the data in this object.

        :return: A dictionary representing the data in this object.
        :rtype: dict
        """
        display_name_ = _serialize(self.display_name)
        user_id_ = _serialize(self.user_id)
        return {
            'displayName': display_name_,
            'userId': user_id_
        }

    def to_json(self):
        """
        Returns a JSON string representing the data in this object.

        :return: A JSON string representing the data in this object.
        :rtype: str
        """
        body_dict = self.to_dict()
        return json.dumps(body_dict, separators=(',', ':'))

    def to_body_bytes(self):
        """
        Returns a :class:`bytearray` body representing the data in this object.

        :return: A :class:`bytearray` body representing the data in this object.
        :rtype: bytearray
        """
        body_json = self.to_json()
        return bytearray(body_json, 'utf-8')


class ExternalCalibrationModel(object):
    """
    ExternalCalibrationModel custom data type.
    """
    def __init__(self,
                 temperature_sensors_=None,
                 is_limited_=None,
                 date_=None,
                 recommended_interval_=None,
                 next_recommended_date_=None,
                 comments_=None,
                 entry_type_=None,
                 calibration_operator_=None):
        """
        :param temperature_sensors_: temperature_sensors
        :type temperature_sensors_: list(TemperatureSensor)
        :param is_limited_: is_limited
        :type is_limited_: bool
        :param date_: date
        :type date_: datetime
        :param recommended_interval_: recommended_interval
        :type recommended_interval_: int
        :param next_recommended_date_: next_recommended_date
        :type next_recommended_date_: datetime
        :param comments_: comments
        :type comments_: str
        :param entry_type_: entry_type
        :type entry_type_: CalibrationMode
        :param calibration_operator_: calibration_operator
        :type calibration_operator_: CalibrationOperator
        """
        self.temperature_sensors = temperature_sensors_
        self.is_limited = is_limited_
        self.date = date_
        self.recommended_interval = recommended_interval_
        self.next_recommended_date = next_recommended_date_
        self.comments = comments_
        self.entry_type = entry_type_
        self.calibration_operator = calibration_operator_

    @classmethod
    def from_dict(cls, body_dict):
        """
        Create a new instance of :class:`ExternalCalibrationModel` using a dictionary.

        :param body_dict: A dictionary representing the body.
        :type body_dict: dict
        :return: A new instance of :class:`ExternalCalibrationModel`.
        :rtype: ExternalCalibrationModel
        """
        temperature_sensors_ = _deserialize(body_dict.get('temperatureSensors'), 'list(TemperatureSensor)')
        is_limited_ = _deserialize(body_dict.get('isLimited'), 'bool')
        date_ = _deserialize(body_dict.get('date'), 'datetime')
        recommended_interval_ = _deserialize(body_dict.get('recommendedInterval'), 'int')
        next_recommended_date_ = _deserialize(body_dict.get('nextRecommendedDate'), 'datetime')
        comments_ = _deserialize(body_dict.get('comments'), 'str')
        entry_type_ = _deserialize(body_dict.get('entryType'), 'CalibrationMode')
        calibration_operator_ = _deserialize(body_dict.get('calibrationOperator'), 'CalibrationOperator')
        return cls(
            temperature_sensors_=temperature_sensors_,
            is_limited_=is_limited_,
            date_=date_,
            recommended_interval_=recommended_interval_,
            next_recommended_date_=next_recommended_date_,
            comments_=comments_,
            entry_type_=entry_type_,
            calibration_operator_=calibration_operator_
        )

    @classmethod
    def from_json(cls, body_json):
        """
        Create a new instance of :class:`ExternalCalibrationModel` using a JSON string.

        :param body_json: A string in JSON format representing the body.
        :type body_json: str
        :return: A new instance of :class:`ExternalCalibrationModel`.
        :rtype: ExternalCalibrationModel
        """
        body_dict = json.loads(body_json)
        return cls.from_dict(body_dict)

    @classmethod
    def from_body_bytes(cls, body_bytes):
        """
        Create a new instance of :class:`ExternalCalibrationModel` using a body
        of type :class:`bytes` or :class:`bytearray`.

        :param body_bytes: The body to use.
        :type body_bytes: bytes or bytearray
        :return: A new instance of :class:`ExternalCalibrationModel`.
        :rtype: ExternalCalibrationModel
        """
        body_json = str(body_bytes, 'utf-8')
        return cls.from_json(body_json)

    def to_dict(self):
        """
        Returns a dictionary representing the data in this object.

        :return: A dictionary representing the data in this object.
        :rtype: dict
        """
        temperature_sensors_ = _serialize(self.temperature_sensors)
        is_limited_ = _serialize(self.is_limited)
        date_ = _serialize(self.date)
        recommended_interval_ = _serialize(self.recommended_interval)
        next_recommended_date_ = _serialize(self.next_recommended_date)
        comments_ = _serialize(self.comments)
        entry_type_ = _serialize(self.entry_type)
        calibration_operator_ = _serialize(self.calibration_operator)
        return {
            'temperatureSensors': temperature_sensors_,
            'isLimited': is_limited_,
            'date': date_,
            'recommendedInterval': recommended_interval_,
            'nextRecommendedDate': next_recommended_date_,
            'comments': comments_,
            'entryType': entry_type_,
            'calibrationOperator': calibration_operator_
        }

    def to_json(self):
        """
        Returns a JSON string representing the data in this object.

        :return: A JSON string representing the data in this object.
        :rtype: str
        """
        body_dict = self.to_dict()
        return json.dumps(body_dict, separators=(',', ':'))

    def to_body_bytes(self):
        """
        Returns a :class:`bytearray` body representing the data in this object.

        :return: A :class:`bytearray` body representing the data in this object.
        :rtype: bytearray
        """
        body_json = self.to_json()
        return bytearray(body_json, 'utf-8')


class AssetModel(object):
    """
    AssetModel custom data type.
    """
    def __init__(self,
                 id_=None,
                 serial_number_=None,
                 model_name_=None,
                 model_number_=None,
                 vendor_name_=None,
                 vendor_number_=None,
                 name_=None,
                 firmware_version_=None,
                 hardware_version_=None,
                 bus_type_=None,
                 visa_resource_name_=None,
                 location_=None,
                 temperature_sensors_=None,
                 supports_self_calibration_=None,
                 supports_external_calibration_=None,
                 self_calibration_=None,
                 external_calibration_=None,
                 calibration_status_=None,
                 last_updated_timestamp_=None,
                 is_ni_asset_=None,
                 keywords_=None,
                 properties_=None):
        """
        :param id_: id
        :type id_: str
        :param serial_number_: serial_number
        :type serial_number_: str
        :param model_name_: model_name
        :type model_name_: str
        :param model_number_: model_number
        :type model_number_: long
        :param vendor_name_: vendor_name
        :type vendor_name_: str
        :param vendor_number_: vendor_number
        :type vendor_number_: long
        :param name_: name
        :type name_: str
        :param firmware_version_: firmware_version
        :type firmware_version_: str
        :param hardware_version_: hardware_version
        :type hardware_version_: str
        :param bus_type_: bus_type
        :type bus_type_: BusType
        :param visa_resource_name_: visa_resource_name
        :type visa_resource_name_: str
        :param location_: location
        :type location_: AssetLocation
        :param temperature_sensors_: temperature_sensors
        :type temperature_sensors_: list(TemperatureSensor)
        :param supports_self_calibration_: supports_self_calibration
        :type supports_self_calibration_: bool
        :param supports_external_calibration_: supports_external_calibration
        :type supports_external_calibration_: bool
        :param self_calibration_: self_calibration
        :type self_calibration_: SelfCalibrationModel
        :param external_calibration_: external_calibration
        :type external_calibration_: ExternalCalibrationModel
        :param calibration_status_: calibration_status
        :type calibration_status_: CalibrationStatus
        :param last_updated_timestamp_: last_updated_timestamp
        :type last_updated_timestamp_: datetime
        :param is_ni_asset_: is_ni_asset
        :type is_ni_asset_: bool
        :param keywords_: keywords
        :type keywords_: list(str)
        :param properties_: properties
        :type properties_: dict(str,str)
        """
        self.id = id_  # pylint: disable=invalid-name
        self.serial_number = serial_number_
        self.model_name = model_name_
        self.model_number = model_number_
        self.vendor_name = vendor_name_
        self.vendor_number = vendor_number_
        self.name = name_
        self.firmware_version = firmware_version_
        self.hardware_version = hardware_version_
        self.bus_type = bus_type_
        self.visa_resource_name = visa_resource_name_
        self.location = location_
        self.temperature_sensors = temperature_sensors_
        self.supports_self_calibration = supports_self_calibration_
        self.supports_external_calibration = supports_external_calibration_
        self.self_calibration = self_calibration_
        self.external_calibration = external_calibration_
        self.calibration_status = calibration_status_
        self.last_updated_timestamp = last_updated_timestamp_
        self.is_ni_asset = is_ni_asset_
        self.keywords = keywords_
        self.properties = properties_

    @classmethod
    def from_dict(cls, body_dict):
        """
        Create a new instance of :class:`AssetModel` using a dictionary.

        :param body_dict: A dictionary representing the body.
        :type body_dict: dict
        :return: A new instance of :class:`AssetModel`.
        :rtype: AssetModel
        """
        id_ = _deserialize(body_dict.get('id'), 'str')  # pylint: disable=invalid-name
        serial_number_ = _deserialize(body_dict.get('serialNumber'), 'str')
        model_name_ = _deserialize(body_dict.get('modelName'), 'str')
        model_number_ = _deserialize(body_dict.get('modelNumber'), 'long')
        vendor_name_ = _deserialize(body_dict.get('vendorName'), 'str')
        vendor_number_ = _deserialize(body_dict.get('vendorNumber'), 'long')
        name_ = _deserialize(body_dict.get('name'), 'str')
        firmware_version_ = _deserialize(body_dict.get('firmwareVersion'), 'str')
        hardware_version_ = _deserialize(body_dict.get('hardwareVersion'), 'str')
        bus_type_ = _deserialize(body_dict.get('busType'), 'BusType')
        visa_resource_name_ = _deserialize(body_dict.get('visaResourceName'), 'str')
        location_ = _deserialize(body_dict.get('location'), 'AssetLocation')
        temperature_sensors_ = _deserialize(body_dict.get('temperatureSensors'), 'list(TemperatureSensor)')
        supports_self_calibration_ = _deserialize(body_dict.get('supportsSelfCalibration'), 'bool')
        supports_external_calibration_ = _deserialize(body_dict.get('supportsExternalCalibration'), 'bool')
        self_calibration_ = _deserialize(body_dict.get('selfCalibration'), 'SelfCalibrationModel')
        external_calibration_ = _deserialize(body_dict.get('externalCalibration'), 'ExternalCalibrationModel')
        calibration_status_ = _deserialize(body_dict.get('calibrationStatus'), 'CalibrationStatus')
        last_updated_timestamp_ = _deserialize(body_dict.get('lastUpdatedTimestamp'), 'datetime')
        is_ni_asset_ = _deserialize(body_dict.get('isNIAsset'), 'bool')
        keywords_ = _deserialize(body_dict.get('keywords'), 'list(str)')
        properties_ = _deserialize(body_dict.get('properties'), 'dict(str,str)')
        return cls(
            id_=id_,
            serial_number_=serial_number_,
            model_name_=model_name_,
            model_number_=model_number_,
            vendor_name_=vendor_name_,
            vendor_number_=vendor_number_,
            name_=name_,
            firmware_version_=firmware_version_,
            hardware_version_=hardware_version_,
            bus_type_=bus_type_,
            visa_resource_name_=visa_resource_name_,
            location_=location_,
            temperature_sensors_=temperature_sensors_,
            supports_self_calibration_=supports_self_calibration_,
            supports_external_calibration_=supports_external_calibration_,
            self_calibration_=self_calibration_,
            external_calibration_=external_calibration_,
            calibration_status_=calibration_status_,
            last_updated_timestamp_=last_updated_timestamp_,
            is_ni_asset_=is_ni_asset_,
            keywords_=keywords_,
            properties_=properties_
        )

    @classmethod
    def from_json(cls, body_json):
        """
        Create a new instance of :class:`AssetModel` using a JSON string.

        :param body_json: A string in JSON format representing the body.
        :type body_json: str
        :return: A new instance of :class:`AssetModel`.
        :rtype: AssetModel
        """
        body_dict = json.loads(body_json)
        return cls.from_dict(body_dict)

    @classmethod
    def from_body_bytes(cls, body_bytes):
        """
        Create a new instance of :class:`AssetModel` using a body
        of type :class:`bytes` or :class:`bytearray`.

        :param body_bytes: The body to use.
        :type body_bytes: bytes or bytearray
        :return: A new instance of :class:`AssetModel`.
        :rtype: AssetModel
        """
        body_json = str(body_bytes, 'utf-8')
        return cls.from_json(body_json)

    def to_dict(self):
        """
        Returns a dictionary representing the data in this object.

        :return: A dictionary representing the data in this object.
        :rtype: dict
        """
        id_ = _serialize(self.id)  # pylint: disable=invalid-name
        serial_number_ = _serialize(self.serial_number)
        model_name_ = _serialize(self.model_name)
        model_number_ = _serialize(self.model_number)
        vendor_name_ = _serialize(self.vendor_name)
        vendor_number_ = _serialize(self.vendor_number)
        name_ = _serialize(self.name)
        firmware_version_ = _serialize(self.firmware_version)
        hardware_version_ = _serialize(self.hardware_version)
        bus_type_ = _serialize(self.bus_type)
        visa_resource_name_ = _serialize(self.visa_resource_name)
        location_ = _serialize(self.location)
        temperature_sensors_ = _serialize(self.temperature_sensors)
        supports_self_calibration_ = _serialize(self.supports_self_calibration)
        supports_external_calibration_ = _serialize(self.supports_external_calibration)
        self_calibration_ = _serialize(self.self_calibration)
        external_calibration_ = _serialize(self.external_calibration)
        calibration_status_ = _serialize(self.calibration_status)
        last_updated_timestamp_ = _serialize(self.last_updated_timestamp)
        is_ni_asset_ = _serialize(self.is_ni_asset)
        keywords_ = _serialize(self.keywords)
        properties_ = _serialize(self.properties)
        return {
            'id': id_,
            'serialNumber': serial_number_,
            'modelName': model_name_,
            'modelNumber': model_number_,
            'vendorName': vendor_name_,
            'vendorNumber': vendor_number_,
            'name': name_,
            'firmwareVersion': firmware_version_,
            'hardwareVersion': hardware_version_,
            'busType': bus_type_,
            'visaResourceName': visa_resource_name_,
            'location': location_,
            'temperatureSensors': temperature_sensors_,
            'supportsSelfCalibration': supports_self_calibration_,
            'supportsExternalCalibration': supports_external_calibration_,
            'selfCalibration': self_calibration_,
            'externalCalibration': external_calibration_,
            'calibrationStatus': calibration_status_,
            'lastUpdatedTimestamp': last_updated_timestamp_,
            'isNIAsset': is_ni_asset_,
            'keywords': keywords_,
            'properties': properties_
        }

    def to_json(self):
        """
        Returns a JSON string representing the data in this object.

        :return: A JSON string representing the data in this object.
        :rtype: str
        """
        body_dict = self.to_dict()
        return json.dumps(body_dict, separators=(',', ':'))

    def to_body_bytes(self):
        """
        Returns a :class:`bytearray` body representing the data in this object.

        :return: A :class:`bytearray` body representing the data in this object.
        :rtype: bytearray
        """
        body_json = self.to_json()
        return bytearray(body_json, 'utf-8')


class StringQueryEntry(object):
    """
    StringQueryEntry custom data type.
    """
    def __init__(self,
                 key_=None,
                 value_=None,
                 operation_=None):
        """
        :param key_: key
        :type key_: str
        :param value_: value
        :type value_: str
        :param operation_: operation
        :type operation_: QueryOperator
        """
        self.key = key_
        self.value = value_
        self.operation = operation_

    @classmethod
    def from_dict(cls, body_dict):
        """
        Create a new instance of :class:`StringQueryEntry` using a dictionary.

        :param body_dict: A dictionary representing the body.
        :type body_dict: dict
        :return: A new instance of :class:`StringQueryEntry`.
        :rtype: StringQueryEntry
        """
        key_ = _deserialize(body_dict.get('key'), 'str')
        value_ = _deserialize(body_dict.get('value'), 'str')
        operation_ = _deserialize(body_dict.get('operation'), 'QueryOperator')
        return cls(
            key_=key_,
            value_=value_,
            operation_=operation_
        )

    @classmethod
    def from_json(cls, body_json):
        """
        Create a new instance of :class:`StringQueryEntry` using a JSON string.

        :param body_json: A string in JSON format representing the body.
        :type body_json: str
        :return: A new instance of :class:`StringQueryEntry`.
        :rtype: StringQueryEntry
        """
        body_dict = json.loads(body_json)
        return cls.from_dict(body_dict)

    @classmethod
    def from_body_bytes(cls, body_bytes):
        """
        Create a new instance of :class:`StringQueryEntry` using a body
        of type :class:`bytes` or :class:`bytearray`.

        :param body_bytes: The body to use.
        :type body_bytes: bytes or bytearray
        :return: A new instance of :class:`StringQueryEntry`.
        :rtype: StringQueryEntry
        """
        body_json = str(body_bytes, 'utf-8')
        return cls.from_json(body_json)

    def to_dict(self):
        """
        Returns a dictionary representing the data in this object.

        :return: A dictionary representing the data in this object.
        :rtype: dict
        """
        key_ = _serialize(self.key)
        value_ = _serialize(self.value)
        operation_ = _serialize(self.operation)
        return {
            'key': key_,
            'value': value_,
            'operation': operation_
        }

    def to_json(self):
        """
        Returns a JSON string representing the data in this object.

        :return: A JSON string representing the data in this object.
        :rtype: str
        """
        body_dict = self.to_dict()
        return json.dumps(body_dict, separators=(',', ':'))

    def to_body_bytes(self):
        """
        Returns a :class:`bytearray` body representing the data in this object.

        :return: A :class:`bytearray` body representing the data in this object.
        :rtype: bytearray
        """
        body_json = self.to_json()
        return bytearray(body_json, 'utf-8')


class BoolQueryEntry(object):
    """
    BoolQueryEntry custom data type.
    """
    def __init__(self,
                 key_=None,
                 value_=None,
                 operation_=None):
        """
        :param key_: key
        :type key_: str
        :param value_: value
        :type value_: bool
        :param operation_: operation
        :type operation_: QueryOperator
        """
        self.key = key_
        self.value = value_
        self.operation = operation_

    @classmethod
    def from_dict(cls, body_dict):
        """
        Create a new instance of :class:`BoolQueryEntry` using a dictionary.

        :param body_dict: A dictionary representing the body.
        :type body_dict: dict
        :return: A new instance of :class:`BoolQueryEntry`.
        :rtype: BoolQueryEntry
        """
        key_ = _deserialize(body_dict.get('key'), 'str')
        value_ = _deserialize(body_dict.get('value'), 'bool')
        operation_ = _deserialize(body_dict.get('operation'), 'QueryOperator')
        return cls(
            key_=key_,
            value_=value_,
            operation_=operation_
        )

    @classmethod
    def from_json(cls, body_json):
        """
        Create a new instance of :class:`BoolQueryEntry` using a JSON string.

        :param body_json: A string in JSON format representing the body.
        :type body_json: str
        :return: A new instance of :class:`BoolQueryEntry`.
        :rtype: BoolQueryEntry
        """
        body_dict = json.loads(body_json)
        return cls.from_dict(body_dict)

    @classmethod
    def from_body_bytes(cls, body_bytes):
        """
        Create a new instance of :class:`BoolQueryEntry` using a body
        of type :class:`bytes` or :class:`bytearray`.

        :param body_bytes: The body to use.
        :type body_bytes: bytes or bytearray
        :return: A new instance of :class:`BoolQueryEntry`.
        :rtype: BoolQueryEntry
        """
        body_json = str(body_bytes, 'utf-8')
        return cls.from_json(body_json)

    def to_dict(self):
        """
        Returns a dictionary representing the data in this object.

        :return: A dictionary representing the data in this object.
        :rtype: dict
        """
        key_ = _serialize(self.key)
        value_ = _serialize(self.value)
        operation_ = _serialize(self.operation)
        return {
            'key': key_,
            'value': value_,
            'operation': operation_
        }

    def to_json(self):
        """
        Returns a JSON string representing the data in this object.

        :return: A JSON string representing the data in this object.
        :rtype: str
        """
        body_dict = self.to_dict()
        return json.dumps(body_dict, separators=(',', ':'))

    def to_body_bytes(self):
        """
        Returns a :class:`bytearray` body representing the data in this object.

        :return: A :class:`bytearray` body representing the data in this object.
        :rtype: bytearray
        """
        body_json = self.to_json()
        return bytearray(body_json, 'utf-8')


class IntQueryEntry(object):
    """
    IntQueryEntry custom data type.
    """
    def __init__(self,
                 key_=None,
                 value_=None,
                 operation_=None):
        """
        :param key_: key
        :type key_: str
        :param value_: value
        :type value_: int
        :param operation_: operation
        :type operation_: QueryOperator
        """
        self.key = key_
        self.value = value_
        self.operation = operation_

    @classmethod
    def from_dict(cls, body_dict):
        """
        Create a new instance of :class:`IntQueryEntry` using a dictionary.

        :param body_dict: A dictionary representing the body.
        :type body_dict: dict
        :return: A new instance of :class:`IntQueryEntry`.
        :rtype: IntQueryEntry
        """
        key_ = _deserialize(body_dict.get('key'), 'str')
        value_ = _deserialize(body_dict.get('value'), 'int')
        operation_ = _deserialize(body_dict.get('operation'), 'QueryOperator')
        return cls(
            key_=key_,
            value_=value_,
            operation_=operation_
        )

    @classmethod
    def from_json(cls, body_json):
        """
        Create a new instance of :class:`IntQueryEntry` using a JSON string.

        :param body_json: A string in JSON format representing the body.
        :type body_json: str
        :return: A new instance of :class:`IntQueryEntry`.
        :rtype: IntQueryEntry
        """
        body_dict = json.loads(body_json)
        return cls.from_dict(body_dict)

    @classmethod
    def from_body_bytes(cls, body_bytes):
        """
        Create a new instance of :class:`IntQueryEntry` using a body
        of type :class:`bytes` or :class:`bytearray`.

        :param body_bytes: The body to use.
        :type body_bytes: bytes or bytearray
        :return: A new instance of :class:`IntQueryEntry`.
        :rtype: IntQueryEntry
        """
        body_json = str(body_bytes, 'utf-8')
        return cls.from_json(body_json)

    def to_dict(self):
        """
        Returns a dictionary representing the data in this object.

        :return: A dictionary representing the data in this object.
        :rtype: dict
        """
        key_ = _serialize(self.key)
        value_ = _serialize(self.value)
        operation_ = _serialize(self.operation)
        return {
            'key': key_,
            'value': value_,
            'operation': operation_
        }

    def to_json(self):
        """
        Returns a JSON string representing the data in this object.

        :return: A JSON string representing the data in this object.
        :rtype: str
        """
        body_dict = self.to_dict()
        return json.dumps(body_dict, separators=(',', ':'))

    def to_body_bytes(self):
        """
        Returns a :class:`bytearray` body representing the data in this object.

        :return: A :class:`bytearray` body representing the data in this object.
        :rtype: bytearray
        """
        body_json = self.to_json()
        return bytearray(body_json, 'utf-8')


class LongQueryEntry(object):
    """
    LongQueryEntry custom data type.
    """
    def __init__(self,
                 key_=None,
                 value_=None,
                 operation_=None):
        """
        :param key_: key
        :type key_: str
        :param value_: value
        :type value_: long
        :param operation_: operation
        :type operation_: QueryOperator
        """
        self.key = key_
        self.value = value_
        self.operation = operation_

    @classmethod
    def from_dict(cls, body_dict):
        """
        Create a new instance of :class:`LongQueryEntry` using a dictionary.

        :param body_dict: A dictionary representing the body.
        :type body_dict: dict
        :return: A new instance of :class:`LongQueryEntry`.
        :rtype: LongQueryEntry
        """
        key_ = _deserialize(body_dict.get('key'), 'str')
        value_ = _deserialize(body_dict.get('value'), 'long')
        operation_ = _deserialize(body_dict.get('operation'), 'QueryOperator')
        return cls(
            key_=key_,
            value_=value_,
            operation_=operation_
        )

    @classmethod
    def from_json(cls, body_json):
        """
        Create a new instance of :class:`LongQueryEntry` using a JSON string.

        :param body_json: A string in JSON format representing the body.
        :type body_json: str
        :return: A new instance of :class:`LongQueryEntry`.
        :rtype: LongQueryEntry
        """
        body_dict = json.loads(body_json)
        return cls.from_dict(body_dict)

    @classmethod
    def from_body_bytes(cls, body_bytes):
        """
        Create a new instance of :class:`LongQueryEntry` using a body
        of type :class:`bytes` or :class:`bytearray`.

        :param body_bytes: The body to use.
        :type body_bytes: bytes or bytearray
        :return: A new instance of :class:`LongQueryEntry`.
        :rtype: LongQueryEntry
        """
        body_json = str(body_bytes, 'utf-8')
        return cls.from_json(body_json)

    def to_dict(self):
        """
        Returns a dictionary representing the data in this object.

        :return: A dictionary representing the data in this object.
        :rtype: dict
        """
        key_ = _serialize(self.key)
        value_ = _serialize(self.value)
        operation_ = _serialize(self.operation)
        return {
            'key': key_,
            'value': value_,
            'operation': operation_
        }

    def to_json(self):
        """
        Returns a JSON string representing the data in this object.

        :return: A JSON string representing the data in this object.
        :rtype: str
        """
        body_dict = self.to_dict()
        return json.dumps(body_dict, separators=(',', ':'))

    def to_body_bytes(self):
        """
        Returns a :class:`bytearray` body representing the data in this object.

        :return: A :class:`bytearray` body representing the data in this object.
        :rtype: bytearray
        """
        body_json = self.to_json()
        return bytearray(body_json, 'utf-8')


class DateQueryEntry(object):
    """
    DateQueryEntry custom data type.
    """
    def __init__(self,
                 key_=None,
                 value_=None,
                 operation_=None):
        """
        :param key_: key
        :type key_: str
        :param value_: value
        :type value_: datetime
        :param operation_: operation
        :type operation_: QueryOperator
        """
        self.key = key_
        self.value = value_
        self.operation = operation_

    @classmethod
    def from_dict(cls, body_dict):
        """
        Create a new instance of :class:`DateQueryEntry` using a dictionary.

        :param body_dict: A dictionary representing the body.
        :type body_dict: dict
        :return: A new instance of :class:`DateQueryEntry`.
        :rtype: DateQueryEntry
        """
        key_ = _deserialize(body_dict.get('key'), 'str')
        value_ = _deserialize(body_dict.get('value'), 'datetime')
        operation_ = _deserialize(body_dict.get('operation'), 'QueryOperator')
        return cls(
            key_=key_,
            value_=value_,
            operation_=operation_
        )

    @classmethod
    def from_json(cls, body_json):
        """
        Create a new instance of :class:`DateQueryEntry` using a JSON string.

        :param body_json: A string in JSON format representing the body.
        :type body_json: str
        :return: A new instance of :class:`DateQueryEntry`.
        :rtype: DateQueryEntry
        """
        body_dict = json.loads(body_json)
        return cls.from_dict(body_dict)

    @classmethod
    def from_body_bytes(cls, body_bytes):
        """
        Create a new instance of :class:`DateQueryEntry` using a body
        of type :class:`bytes` or :class:`bytearray`.

        :param body_bytes: The body to use.
        :type body_bytes: bytes or bytearray
        :return: A new instance of :class:`DateQueryEntry`.
        :rtype: DateQueryEntry
        """
        body_json = str(body_bytes, 'utf-8')
        return cls.from_json(body_json)

    def to_dict(self):
        """
        Returns a dictionary representing the data in this object.

        :return: A dictionary representing the data in this object.
        :rtype: dict
        """
        key_ = _serialize(self.key)
        value_ = _serialize(self.value)
        operation_ = _serialize(self.operation)
        return {
            'key': key_,
            'value': value_,
            'operation': operation_
        }

    def to_json(self):
        """
        Returns a JSON string representing the data in this object.

        :return: A JSON string representing the data in this object.
        :rtype: str
        """
        body_dict = self.to_dict()
        return json.dumps(body_dict, separators=(',', ':'))

    def to_body_bytes(self):
        """
        Returns a :class:`bytearray` body representing the data in this object.

        :return: A :class:`bytearray` body representing the data in this object.
        :rtype: bytearray
        """
        body_json = self.to_json()
        return bytearray(body_json, 'utf-8')


class SystemConnectionQuery(object):
    """
    SystemConnectionQuery custom data type.
    """
    def __init__(self,
                 key_=None,
                 value_=None,
                 operation_=None):
        """
        :param key_: key
        :type key_: str
        :param value_: value
        :type value_: SystemConnectionState
        :param operation_: operation
        :type operation_: QueryOperator
        """
        self.key = key_
        self.value = value_
        self.operation = operation_

    @classmethod
    def from_dict(cls, body_dict):
        """
        Create a new instance of :class:`SystemConnectionQuery` using a dictionary.

        :param body_dict: A dictionary representing the body.
        :type body_dict: dict
        :return: A new instance of :class:`SystemConnectionQuery`.
        :rtype: SystemConnectionQuery
        """
        key_ = _deserialize(body_dict.get('key'), 'str')
        value_ = _deserialize(body_dict.get('value'), 'SystemConnectionState')
        operation_ = _deserialize(body_dict.get('operation'), 'QueryOperator')
        return cls(
            key_=key_,
            value_=value_,
            operation_=operation_
        )

    @classmethod
    def from_json(cls, body_json):
        """
        Create a new instance of :class:`SystemConnectionQuery` using a JSON string.

        :param body_json: A string in JSON format representing the body.
        :type body_json: str
        :return: A new instance of :class:`SystemConnectionQuery`.
        :rtype: SystemConnectionQuery
        """
        body_dict = json.loads(body_json)
        return cls.from_dict(body_dict)

    @classmethod
    def from_body_bytes(cls, body_bytes):
        """
        Create a new instance of :class:`SystemConnectionQuery` using a body
        of type :class:`bytes` or :class:`bytearray`.

        :param body_bytes: The body to use.
        :type body_bytes: bytes or bytearray
        :return: A new instance of :class:`SystemConnectionQuery`.
        :rtype: SystemConnectionQuery
        """
        body_json = str(body_bytes, 'utf-8')
        return cls.from_json(body_json)

    def to_dict(self):
        """
        Returns a dictionary representing the data in this object.

        :return: A dictionary representing the data in this object.
        :rtype: dict
        """
        key_ = _serialize(self.key)
        value_ = _serialize(self.value)
        operation_ = _serialize(self.operation)
        return {
            'key': key_,
            'value': value_,
            'operation': operation_
        }

    def to_json(self):
        """
        Returns a JSON string representing the data in this object.

        :return: A JSON string representing the data in this object.
        :rtype: str
        """
        body_dict = self.to_dict()
        return json.dumps(body_dict, separators=(',', ':'))

    def to_body_bytes(self):
        """
        Returns a :class:`bytearray` body representing the data in this object.

        :return: A :class:`bytearray` body representing the data in this object.
        :rtype: bytearray
        """
        body_json = self.to_json()
        return bytearray(body_json, 'utf-8')


class AssetPresenceQuery(object):
    """
    AssetPresenceQuery custom data type.
    """
    def __init__(self,
                 key_=None,
                 value_=None,
                 operation_=None):
        """
        :param key_: key
        :type key_: str
        :param value_: value
        :type value_: AssetPresenceStatus
        :param operation_: operation
        :type operation_: QueryOperator
        """
        self.key = key_
        self.value = value_
        self.operation = operation_

    @classmethod
    def from_dict(cls, body_dict):
        """
        Create a new instance of :class:`AssetPresenceQuery` using a dictionary.

        :param body_dict: A dictionary representing the body.
        :type body_dict: dict
        :return: A new instance of :class:`AssetPresenceQuery`.
        :rtype: AssetPresenceQuery
        """
        key_ = _deserialize(body_dict.get('key'), 'str')
        value_ = _deserialize(body_dict.get('value'), 'AssetPresenceStatus')
        operation_ = _deserialize(body_dict.get('operation'), 'QueryOperator')
        return cls(
            key_=key_,
            value_=value_,
            operation_=operation_
        )

    @classmethod
    def from_json(cls, body_json):
        """
        Create a new instance of :class:`AssetPresenceQuery` using a JSON string.

        :param body_json: A string in JSON format representing the body.
        :type body_json: str
        :return: A new instance of :class:`AssetPresenceQuery`.
        :rtype: AssetPresenceQuery
        """
        body_dict = json.loads(body_json)
        return cls.from_dict(body_dict)

    @classmethod
    def from_body_bytes(cls, body_bytes):
        """
        Create a new instance of :class:`AssetPresenceQuery` using a body
        of type :class:`bytes` or :class:`bytearray`.

        :param body_bytes: The body to use.
        :type body_bytes: bytes or bytearray
        :return: A new instance of :class:`AssetPresenceQuery`.
        :rtype: AssetPresenceQuery
        """
        body_json = str(body_bytes, 'utf-8')
        return cls.from_json(body_json)

    def to_dict(self):
        """
        Returns a dictionary representing the data in this object.

        :return: A dictionary representing the data in this object.
        :rtype: dict
        """
        key_ = _serialize(self.key)
        value_ = _serialize(self.value)
        operation_ = _serialize(self.operation)
        return {
            'key': key_,
            'value': value_,
            'operation': operation_
        }

    def to_json(self):
        """
        Returns a JSON string representing the data in this object.

        :return: A JSON string representing the data in this object.
        :rtype: str
        """
        body_dict = self.to_dict()
        return json.dumps(body_dict, separators=(',', ':'))

    def to_body_bytes(self):
        """
        Returns a :class:`bytearray` body representing the data in this object.

        :return: A :class:`bytearray` body representing the data in this object.
        :rtype: bytearray
        """
        body_json = self.to_json()
        return bytearray(body_json, 'utf-8')


class QueryAssetsFilter(object):
    """
    QueryAssetsFilter custom data type.
    """
    def __init__(self,
                 serial_number_query_=None,
                 model_name_query_=None,
                 vendor_name_query_=None,
                 name_query_=None,
                 firmware_version_query_=None,
                 hardware_version_query_=None,
                 visa_resource_name_query_=None,
                 system_name_query_=None,
                 minion_id_query_=None,
                 model_number_query_=None,
                 vendor_number_query_=None,
                 slot_number_query_=None,
                 supports_self_calibration_query_=None,
                 supports_external_calibration_query_=None,
                 last_self_calibration_date_query_=None,
                 last_external_calibration_date_query_=None,
                 next_recommended_calibration_date_query_=None,
                 last_updated_timestamp_query_=None,
                 system_connection_query_=None,
                 asset_presence_query_=None):
        """
        :param serial_number_query_: serial_number_query
        :type serial_number_query_: StringQueryEntry
        :param model_name_query_: model_name_query
        :type model_name_query_: StringQueryEntry
        :param vendor_name_query_: vendor_name_query
        :type vendor_name_query_: StringQueryEntry
        :param name_query_: name_query
        :type name_query_: StringQueryEntry
        :param firmware_version_query_: firmware_version_query
        :type firmware_version_query_: StringQueryEntry
        :param hardware_version_query_: hardware_version_query
        :type hardware_version_query_: StringQueryEntry
        :param visa_resource_name_query_: visa_resource_name_query
        :type visa_resource_name_query_: StringQueryEntry
        :param system_name_query_: system_name_query
        :type system_name_query_: StringQueryEntry
        :param minion_id_query_: minion_id_query
        :type minion_id_query_: StringQueryEntry
        :param model_number_query_: model_number_query
        :type model_number_query_: LongQueryEntry
        :param vendor_number_query_: vendor_number_query
        :type vendor_number_query_: LongQueryEntry
        :param slot_number_query_: slot_number_query
        :type slot_number_query_: IntQueryEntry
        :param supports_self_calibration_query_: supports_self_calibration_query
        :type supports_self_calibration_query_: BoolQueryEntry
        :param supports_external_calibration_query_: supports_external_calibration_query
        :type supports_external_calibration_query_: BoolQueryEntry
        :param last_self_calibration_date_query_: last_self_calibration_date_query
        :type last_self_calibration_date_query_: DateQueryEntry
        :param last_external_calibration_date_query_: last_external_calibration_date_query
        :type last_external_calibration_date_query_: DateQueryEntry
        :param next_recommended_calibration_date_query_: next_recommended_calibration_date_query
        :type next_recommended_calibration_date_query_: DateQueryEntry
        :param last_updated_timestamp_query_: last_updated_timestamp_query
        :type last_updated_timestamp_query_: DateQueryEntry
        :param system_connection_query_: system_connection_query
        :type system_connection_query_: SystemConnectionQuery
        :param asset_presence_query_: asset_presence_query
        :type asset_presence_query_: AssetPresenceQuery
        """
        self.serial_number_query = serial_number_query_
        self.model_name_query = model_name_query_
        self.vendor_name_query = vendor_name_query_
        self.name_query = name_query_
        self.firmware_version_query = firmware_version_query_
        self.hardware_version_query = hardware_version_query_
        self.visa_resource_name_query = visa_resource_name_query_
        self.system_name_query = system_name_query_
        self.minion_id_query = minion_id_query_
        self.model_number_query = model_number_query_
        self.vendor_number_query = vendor_number_query_
        self.slot_number_query = slot_number_query_
        self.supports_self_calibration_query = supports_self_calibration_query_  # pylint: disable=invalid-name
        self.supports_external_calibration_query = supports_external_calibration_query_  # pylint: disable=invalid-name
        self.last_self_calibration_date_query = last_self_calibration_date_query_  # pylint: disable=invalid-name
        self.last_external_calibration_date_query = last_external_calibration_date_query_  # pylint: disable=invalid-name
        self.next_recommended_calibration_date_query = next_recommended_calibration_date_query_  # pylint: disable=invalid-name
        self.last_updated_timestamp_query = last_updated_timestamp_query_
        self.system_connection_query = system_connection_query_
        self.asset_presence_query = asset_presence_query_

    @classmethod
    def from_dict(cls, body_dict):
        """
        Create a new instance of :class:`QueryAssetsFilter` using a dictionary.

        :param body_dict: A dictionary representing the body.
        :type body_dict: dict
        :return: A new instance of :class:`QueryAssetsFilter`.
        :rtype: QueryAssetsFilter
        """
        serial_number_query_ = _deserialize(body_dict.get('SerialNumberQuery'), 'StringQueryEntry')
        model_name_query_ = _deserialize(body_dict.get('ModelNameQuery'), 'StringQueryEntry')
        vendor_name_query_ = _deserialize(body_dict.get('VendorNameQuery'), 'StringQueryEntry')
        name_query_ = _deserialize(body_dict.get('NameQuery'), 'StringQueryEntry')
        firmware_version_query_ = _deserialize(body_dict.get('FirmwareVersionQuery'), 'StringQueryEntry')
        hardware_version_query_ = _deserialize(body_dict.get('HardwareVersionQuery'), 'StringQueryEntry')
        visa_resource_name_query_ = _deserialize(body_dict.get('VisaResourceNameQuery'), 'StringQueryEntry')
        system_name_query_ = _deserialize(body_dict.get('SystemNameQuery'), 'StringQueryEntry')
        minion_id_query_ = _deserialize(body_dict.get('MinionIdQuery'), 'StringQueryEntry')
        model_number_query_ = _deserialize(body_dict.get('ModelNumberQuery'), 'LongQueryEntry')
        vendor_number_query_ = _deserialize(body_dict.get('VendorNumberQuery'), 'LongQueryEntry')
        slot_number_query_ = _deserialize(body_dict.get('SlotNumberQuery'), 'IntQueryEntry')
        supports_self_calibration_query_ = _deserialize(body_dict.get('SupportsSelfCalibrationQuery'), 'BoolQueryEntry')  # pylint: disable=invalid-name
        supports_external_calibration_query_ = _deserialize(body_dict.get('SupportsExternalCalibrationQuery'), 'BoolQueryEntry')  # pylint: disable=invalid-name
        last_self_calibration_date_query_ = _deserialize(body_dict.get('LastSelfCalibrationDateQuery'), 'DateQueryEntry')  # pylint: disable=invalid-name
        last_external_calibration_date_query_ = _deserialize(body_dict.get('LastExternalCalibrationDateQuery'), 'DateQueryEntry')  # pylint: disable=invalid-name
        next_recommended_calibration_date_query_ = _deserialize(body_dict.get('NextRecommendedCalibrationDateQuery'), 'DateQueryEntry')  # pylint: disable=invalid-name
        last_updated_timestamp_query_ = _deserialize(body_dict.get('LastUpdatedTimestampQuery'), 'DateQueryEntry')
        system_connection_query_ = _deserialize(body_dict.get('SystemConnectionQuery'), 'SystemConnectionQuery')
        asset_presence_query_ = _deserialize(body_dict.get('AssetPresenceQuery'), 'AssetPresenceQuery')
        return cls(
            serial_number_query_=serial_number_query_,
            model_name_query_=model_name_query_,
            vendor_name_query_=vendor_name_query_,
            name_query_=name_query_,
            firmware_version_query_=firmware_version_query_,
            hardware_version_query_=hardware_version_query_,
            visa_resource_name_query_=visa_resource_name_query_,
            system_name_query_=system_name_query_,
            minion_id_query_=minion_id_query_,
            model_number_query_=model_number_query_,
            vendor_number_query_=vendor_number_query_,
            slot_number_query_=slot_number_query_,
            supports_self_calibration_query_=supports_self_calibration_query_,
            supports_external_calibration_query_=supports_external_calibration_query_,
            last_self_calibration_date_query_=last_self_calibration_date_query_,
            last_external_calibration_date_query_=last_external_calibration_date_query_,
            next_recommended_calibration_date_query_=next_recommended_calibration_date_query_,
            last_updated_timestamp_query_=last_updated_timestamp_query_,
            system_connection_query_=system_connection_query_,
            asset_presence_query_=asset_presence_query_
        )

    @classmethod
    def from_json(cls, body_json):
        """
        Create a new instance of :class:`QueryAssetsFilter` using a JSON string.

        :param body_json: A string in JSON format representing the body.
        :type body_json: str
        :return: A new instance of :class:`QueryAssetsFilter`.
        :rtype: QueryAssetsFilter
        """
        body_dict = json.loads(body_json)
        return cls.from_dict(body_dict)

    @classmethod
    def from_body_bytes(cls, body_bytes):
        """
        Create a new instance of :class:`QueryAssetsFilter` using a body
        of type :class:`bytes` or :class:`bytearray`.

        :param body_bytes: The body to use.
        :type body_bytes: bytes or bytearray
        :return: A new instance of :class:`QueryAssetsFilter`.
        :rtype: QueryAssetsFilter
        """
        body_json = str(body_bytes, 'utf-8')
        return cls.from_json(body_json)

    def to_dict(self):
        """
        Returns a dictionary representing the data in this object.

        :return: A dictionary representing the data in this object.
        :rtype: dict
        """
        serial_number_query_ = _serialize(self.serial_number_query)
        model_name_query_ = _serialize(self.model_name_query)
        vendor_name_query_ = _serialize(self.vendor_name_query)
        name_query_ = _serialize(self.name_query)
        firmware_version_query_ = _serialize(self.firmware_version_query)
        hardware_version_query_ = _serialize(self.hardware_version_query)
        visa_resource_name_query_ = _serialize(self.visa_resource_name_query)
        system_name_query_ = _serialize(self.system_name_query)
        minion_id_query_ = _serialize(self.minion_id_query)
        model_number_query_ = _serialize(self.model_number_query)
        vendor_number_query_ = _serialize(self.vendor_number_query)
        slot_number_query_ = _serialize(self.slot_number_query)
        supports_self_calibration_query_ = _serialize(self.supports_self_calibration_query)  # pylint: disable=invalid-name
        supports_external_calibration_query_ = _serialize(self.supports_external_calibration_query)  # pylint: disable=invalid-name
        last_self_calibration_date_query_ = _serialize(self.last_self_calibration_date_query)  # pylint: disable=invalid-name
        last_external_calibration_date_query_ = _serialize(self.last_external_calibration_date_query)  # pylint: disable=invalid-name
        next_recommended_calibration_date_query_ = _serialize(self.next_recommended_calibration_date_query)  # pylint: disable=invalid-name
        last_updated_timestamp_query_ = _serialize(self.last_updated_timestamp_query)
        system_connection_query_ = _serialize(self.system_connection_query)
        asset_presence_query_ = _serialize(self.asset_presence_query)
        return {
            'SerialNumberQuery': serial_number_query_,
            'ModelNameQuery': model_name_query_,
            'VendorNameQuery': vendor_name_query_,
            'NameQuery': name_query_,
            'FirmwareVersionQuery': firmware_version_query_,
            'HardwareVersionQuery': hardware_version_query_,
            'VisaResourceNameQuery': visa_resource_name_query_,
            'SystemNameQuery': system_name_query_,
            'MinionIdQuery': minion_id_query_,
            'ModelNumberQuery': model_number_query_,
            'VendorNumberQuery': vendor_number_query_,
            'SlotNumberQuery': slot_number_query_,
            'SupportsSelfCalibrationQuery': supports_self_calibration_query_,
            'SupportsExternalCalibrationQuery': supports_external_calibration_query_,
            'LastSelfCalibrationDateQuery': last_self_calibration_date_query_,
            'LastExternalCalibrationDateQuery': last_external_calibration_date_query_,
            'NextRecommendedCalibrationDateQuery': next_recommended_calibration_date_query_,
            'LastUpdatedTimestampQuery': last_updated_timestamp_query_,
            'SystemConnectionQuery': system_connection_query_,
            'AssetPresenceQuery': asset_presence_query_
        }

    def to_json(self):
        """
        Returns a JSON string representing the data in this object.

        :return: A JSON string representing the data in this object.
        :rtype: str
        """
        body_dict = self.to_dict()
        return json.dumps(body_dict, separators=(',', ':'))

    def to_body_bytes(self):
        """
        Returns a :class:`bytearray` body representing the data in this object.

        :return: A :class:`bytearray` body representing the data in this object.
        :rtype: bytearray
        """
        body_json = self.to_json()
        return bytearray(body_json, 'utf-8')


class TemperatureData(object):
    """
    TemperatureData custom data type.
    """
    def __init__(self,
                 name_=None,
                 reading_=None):
        """
        :param name_: name
        :type name_: str
        :param reading_: reading
        :type reading_: float
        """
        self.name = name_
        self.reading = reading_

    @classmethod
    def from_dict(cls, body_dict):
        """
        Create a new instance of :class:`TemperatureData` using a dictionary.

        :param body_dict: A dictionary representing the body.
        :type body_dict: dict
        :return: A new instance of :class:`TemperatureData`.
        :rtype: TemperatureData
        """
        name_ = _deserialize(body_dict.get('name'), 'str')
        reading_ = _deserialize(body_dict.get('reading'), 'float')
        return cls(
            name_=name_,
            reading_=reading_
        )

    @classmethod
    def from_json(cls, body_json):
        """
        Create a new instance of :class:`TemperatureData` using a JSON string.

        :param body_json: A string in JSON format representing the body.
        :type body_json: str
        :return: A new instance of :class:`TemperatureData`.
        :rtype: TemperatureData
        """
        body_dict = json.loads(body_json)
        return cls.from_dict(body_dict)

    @classmethod
    def from_body_bytes(cls, body_bytes):
        """
        Create a new instance of :class:`TemperatureData` using a body
        of type :class:`bytes` or :class:`bytearray`.

        :param body_bytes: The body to use.
        :type body_bytes: bytes or bytearray
        :return: A new instance of :class:`TemperatureData`.
        :rtype: TemperatureData
        """
        body_json = str(body_bytes, 'utf-8')
        return cls.from_json(body_json)

    def to_dict(self):
        """
        Returns a dictionary representing the data in this object.

        :return: A dictionary representing the data in this object.
        :rtype: dict
        """
        name_ = _serialize(self.name)
        reading_ = _serialize(self.reading)
        return {
            'name': name_,
            'reading': reading_
        }

    def to_json(self):
        """
        Returns a JSON string representing the data in this object.

        :return: A JSON string representing the data in this object.
        :rtype: str
        """
        body_dict = self.to_dict()
        return json.dumps(body_dict, separators=(',', ':'))

    def to_body_bytes(self):
        """
        Returns a :class:`bytearray` body representing the data in this object.

        :return: A :class:`bytearray` body representing the data in this object.
        :rtype: bytearray
        """
        body_json = self.to_json()
        return bytearray(body_json, 'utf-8')


class ExternalCalibrationData(object):
    """
    ExternalCalibrationData custom data type.
    """
    def __init__(self,
                 date_=None,
                 next_recommended_date_=None,
                 recommended_interval_=None,
                 is_limited_=None,
                 supports_limited_=None,
                 supports_write_=None,
                 temperature_info_=None,
                 checksum_=None,
                 comments_=None):
        """
        :param date_: date
        :type date_: str
        :param next_recommended_date_: next_recommended_date
        :type next_recommended_date_: str
        :param recommended_interval_: recommended_interval
        :type recommended_interval_: int
        :param is_limited_: is_limited
        :type is_limited_: bool
        :param supports_limited_: supports_limited
        :type supports_limited_: bool
        :param supports_write_: supports_write
        :type supports_write_: bool
        :param temperature_info_: temperature_info
        :type temperature_info_: list(TemperatureData)
        :param checksum_: checksum
        :type checksum_: str
        :param comments_: comments
        :type comments_: str
        """
        self.date = date_
        self.next_recommended_date = next_recommended_date_
        self.recommended_interval = recommended_interval_
        self.is_limited = is_limited_
        self.supports_limited = supports_limited_
        self.supports_write = supports_write_
        self.temperature_info = temperature_info_
        self.checksum = checksum_
        self.comments = comments_

    @classmethod
    def from_dict(cls, body_dict):
        """
        Create a new instance of :class:`ExternalCalibrationData` using a dictionary.

        :param body_dict: A dictionary representing the body.
        :type body_dict: dict
        :return: A new instance of :class:`ExternalCalibrationData`.
        :rtype: ExternalCalibrationData
        """
        date_ = _deserialize(body_dict.get('date'), 'str')
        next_recommended_date_ = _deserialize(body_dict.get('nextRecommendedDate'), 'str')
        recommended_interval_ = _deserialize(body_dict.get('recommendedInterval'), 'int')
        is_limited_ = _deserialize(body_dict.get('isLimited'), 'bool')
        supports_limited_ = _deserialize(body_dict.get('supportsLimited'), 'bool')
        supports_write_ = _deserialize(body_dict.get('supportsWrite'), 'bool')
        temperature_info_ = _deserialize(body_dict.get('temperatureInfo'), 'list(TemperatureData)')
        checksum_ = _deserialize(body_dict.get('checksum'), 'str')
        comments_ = _deserialize(body_dict.get('comments'), 'str')
        return cls(
            date_=date_,
            next_recommended_date_=next_recommended_date_,
            recommended_interval_=recommended_interval_,
            is_limited_=is_limited_,
            supports_limited_=supports_limited_,
            supports_write_=supports_write_,
            temperature_info_=temperature_info_,
            checksum_=checksum_,
            comments_=comments_
        )

    @classmethod
    def from_json(cls, body_json):
        """
        Create a new instance of :class:`ExternalCalibrationData` using a JSON string.

        :param body_json: A string in JSON format representing the body.
        :type body_json: str
        :return: A new instance of :class:`ExternalCalibrationData`.
        :rtype: ExternalCalibrationData
        """
        body_dict = json.loads(body_json)
        return cls.from_dict(body_dict)

    @classmethod
    def from_body_bytes(cls, body_bytes):
        """
        Create a new instance of :class:`ExternalCalibrationData` using a body
        of type :class:`bytes` or :class:`bytearray`.

        :param body_bytes: The body to use.
        :type body_bytes: bytes or bytearray
        :return: A new instance of :class:`ExternalCalibrationData`.
        :rtype: ExternalCalibrationData
        """
        body_json = str(body_bytes, 'utf-8')
        return cls.from_json(body_json)

    def to_dict(self):
        """
        Returns a dictionary representing the data in this object.

        :return: A dictionary representing the data in this object.
        :rtype: dict
        """
        date_ = _serialize(self.date)
        next_recommended_date_ = _serialize(self.next_recommended_date)
        recommended_interval_ = _serialize(self.recommended_interval)
        is_limited_ = _serialize(self.is_limited)
        supports_limited_ = _serialize(self.supports_limited)
        supports_write_ = _serialize(self.supports_write)
        temperature_info_ = _serialize(self.temperature_info)
        checksum_ = _serialize(self.checksum)
        comments_ = _serialize(self.comments)
        return {
            'date': date_,
            'nextRecommendedDate': next_recommended_date_,
            'recommendedInterval': recommended_interval_,
            'isLimited': is_limited_,
            'supportsLimited': supports_limited_,
            'supportsWrite': supports_write_,
            'temperatureInfo': temperature_info_,
            'checksum': checksum_,
            'comments': comments_
        }

    def to_json(self):
        """
        Returns a JSON string representing the data in this object.

        :return: A JSON string representing the data in this object.
        :rtype: str
        """
        body_dict = self.to_dict()
        return json.dumps(body_dict, separators=(',', ':'))

    def to_body_bytes(self):
        """
        Returns a :class:`bytearray` body representing the data in this object.

        :return: A :class:`bytearray` body representing the data in this object.
        :rtype: bytearray
        """
        body_json = self.to_json()
        return bytearray(body_json, 'utf-8')


class SelfCalibrationData(object):
    """
    SelfCalibrationData custom data type.
    """
    def __init__(self,
                 date_=None,
                 is_limited_=None,
                 temperature_info_=None):
        """
        :param date_: date
        :type date_: str
        :param is_limited_: is_limited
        :type is_limited_: bool
        :param temperature_info_: temperature_info
        :type temperature_info_: list(TemperatureData)
        """
        self.date = date_
        self.is_limited = is_limited_
        self.temperature_info = temperature_info_

    @classmethod
    def from_dict(cls, body_dict):
        """
        Create a new instance of :class:`SelfCalibrationData` using a dictionary.

        :param body_dict: A dictionary representing the body.
        :type body_dict: dict
        :return: A new instance of :class:`SelfCalibrationData`.
        :rtype: SelfCalibrationData
        """
        date_ = _deserialize(body_dict.get('date'), 'str')
        is_limited_ = _deserialize(body_dict.get('isLimited'), 'bool')
        temperature_info_ = _deserialize(body_dict.get('temperatureInfo'), 'list(TemperatureData)')
        return cls(
            date_=date_,
            is_limited_=is_limited_,
            temperature_info_=temperature_info_
        )

    @classmethod
    def from_json(cls, body_json):
        """
        Create a new instance of :class:`SelfCalibrationData` using a JSON string.

        :param body_json: A string in JSON format representing the body.
        :type body_json: str
        :return: A new instance of :class:`SelfCalibrationData`.
        :rtype: SelfCalibrationData
        """
        body_dict = json.loads(body_json)
        return cls.from_dict(body_dict)

    @classmethod
    def from_body_bytes(cls, body_bytes):
        """
        Create a new instance of :class:`SelfCalibrationData` using a body
        of type :class:`bytes` or :class:`bytearray`.

        :param body_bytes: The body to use.
        :type body_bytes: bytes or bytearray
        :return: A new instance of :class:`SelfCalibrationData`.
        :rtype: SelfCalibrationData
        """
        body_json = str(body_bytes, 'utf-8')
        return cls.from_json(body_json)

    def to_dict(self):
        """
        Returns a dictionary representing the data in this object.

        :return: A dictionary representing the data in this object.
        :rtype: dict
        """
        date_ = _serialize(self.date)
        is_limited_ = _serialize(self.is_limited)
        temperature_info_ = _serialize(self.temperature_info)
        return {
            'date': date_,
            'isLimited': is_limited_,
            'temperatureInfo': temperature_info_
        }

    def to_json(self):
        """
        Returns a JSON string representing the data in this object.

        :return: A JSON string representing the data in this object.
        :rtype: str
        """
        body_dict = self.to_dict()
        return json.dumps(body_dict, separators=(',', ':'))

    def to_body_bytes(self):
        """
        Returns a :class:`bytearray` body representing the data in this object.

        :return: A :class:`bytearray` body representing the data in this object.
        :rtype: bytearray
        """
        body_json = self.to_json()
        return bytearray(body_json, 'utf-8')


class AssetData(object):
    """
    AssetData custom data type.
    """
    def __init__(self,
                 resource_uri_=None,
                 serial_number_=None,
                 vendor_number_=None,
                 model_number_=None,
                 bus_type_=None,
                 supports_self_calibration_=None,
                 self_calibration_entry_=None,
                 supports_external_calibration_=None,
                 external_calibration_entry_=None,
                 temperature_info_=None):
        """
        :param resource_uri_: resource_uri
        :type resource_uri_: str
        :param serial_number_: serial_number
        :type serial_number_: str
        :param vendor_number_: vendor_number
        :type vendor_number_: long
        :param model_number_: model_number
        :type model_number_: long
        :param bus_type_: bus_type
        :type bus_type_: long
        :param supports_self_calibration_: supports_self_calibration
        :type supports_self_calibration_: bool
        :param self_calibration_entry_: self_calibration_entry
        :type self_calibration_entry_: SelfCalibrationData
        :param supports_external_calibration_: supports_external_calibration
        :type supports_external_calibration_: bool
        :param external_calibration_entry_: external_calibration_entry
        :type external_calibration_entry_: ExternalCalibrationData
        :param temperature_info_: temperature_info
        :type temperature_info_: list(TemperatureData)
        """
        self.resource_uri = resource_uri_
        self.serial_number = serial_number_
        self.vendor_number = vendor_number_
        self.model_number = model_number_
        self.bus_type = bus_type_
        self.supports_self_calibration = supports_self_calibration_
        self.self_calibration_entry = self_calibration_entry_
        self.supports_external_calibration = supports_external_calibration_
        self.external_calibration_entry = external_calibration_entry_
        self.temperature_info = temperature_info_

    @classmethod
    def from_dict(cls, body_dict):
        """
        Create a new instance of :class:`AssetData` using a dictionary.

        :param body_dict: A dictionary representing the body.
        :type body_dict: dict
        :return: A new instance of :class:`AssetData`.
        :rtype: AssetData
        """
        resource_uri_ = _deserialize(body_dict.get('resourceUri'), 'str')
        serial_number_ = _deserialize(body_dict.get('serialNumber'), 'str')
        vendor_number_ = _deserialize(body_dict.get('vendorNumber'), 'long')
        model_number_ = _deserialize(body_dict.get('modelNumber'), 'long')
        bus_type_ = _deserialize(body_dict.get('busType'), 'long')
        supports_self_calibration_ = _deserialize(body_dict.get('supportsSelfCalibration'), 'bool')
        self_calibration_entry_ = _deserialize(body_dict.get('selfCalibrationEntry'), 'SelfCalibrationData')
        supports_external_calibration_ = _deserialize(body_dict.get('supportsExternalCalibration'), 'bool')
        external_calibration_entry_ = _deserialize(body_dict.get('externalCalibrationEntry'), 'ExternalCalibrationData')
        temperature_info_ = _deserialize(body_dict.get('temperatureInfo'), 'list(TemperatureData)')
        return cls(
            resource_uri_=resource_uri_,
            serial_number_=serial_number_,
            vendor_number_=vendor_number_,
            model_number_=model_number_,
            bus_type_=bus_type_,
            supports_self_calibration_=supports_self_calibration_,
            self_calibration_entry_=self_calibration_entry_,
            supports_external_calibration_=supports_external_calibration_,
            external_calibration_entry_=external_calibration_entry_,
            temperature_info_=temperature_info_
        )

    @classmethod
    def from_json(cls, body_json):
        """
        Create a new instance of :class:`AssetData` using a JSON string.

        :param body_json: A string in JSON format representing the body.
        :type body_json: str
        :return: A new instance of :class:`AssetData`.
        :rtype: AssetData
        """
        body_dict = json.loads(body_json)
        return cls.from_dict(body_dict)

    @classmethod
    def from_body_bytes(cls, body_bytes):
        """
        Create a new instance of :class:`AssetData` using a body
        of type :class:`bytes` or :class:`bytearray`.

        :param body_bytes: The body to use.
        :type body_bytes: bytes or bytearray
        :return: A new instance of :class:`AssetData`.
        :rtype: AssetData
        """
        body_json = str(body_bytes, 'utf-8')
        return cls.from_json(body_json)

    def to_dict(self):
        """
        Returns a dictionary representing the data in this object.

        :return: A dictionary representing the data in this object.
        :rtype: dict
        """
        resource_uri_ = _serialize(self.resource_uri)
        serial_number_ = _serialize(self.serial_number)
        vendor_number_ = _serialize(self.vendor_number)
        model_number_ = _serialize(self.model_number)
        bus_type_ = _serialize(self.bus_type)
        supports_self_calibration_ = _serialize(self.supports_self_calibration)
        self_calibration_entry_ = _serialize(self.self_calibration_entry)
        supports_external_calibration_ = _serialize(self.supports_external_calibration)
        external_calibration_entry_ = _serialize(self.external_calibration_entry)
        temperature_info_ = _serialize(self.temperature_info)
        return {
            'resourceUri': resource_uri_,
            'serialNumber': serial_number_,
            'vendorNumber': vendor_number_,
            'modelNumber': model_number_,
            'busType': bus_type_,
            'supportsSelfCalibration': supports_self_calibration_,
            'selfCalibrationEntry': self_calibration_entry_,
            'supportsExternalCalibration': supports_external_calibration_,
            'externalCalibrationEntry': external_calibration_entry_,
            'temperatureInfo': temperature_info_
        }

    def to_json(self):
        """
        Returns a JSON string representing the data in this object.

        :return: A JSON string representing the data in this object.
        :rtype: str
        """
        body_dict = self.to_dict()
        return json.dumps(body_dict, separators=(',', ':'))

    def to_body_bytes(self):
        """
        Returns a :class:`bytearray` body representing the data in this object.

        :return: A :class:`bytearray` body representing the data in this object.
        :rtype: bytearray
        """
        body_json = self.to_json()
        return bytearray(body_json, 'utf-8')


class AssetIdentification(object):
    """
    AssetIdentification custom data type.
    """
    def __init__(self,
                 model_name_=None,
                 model_number_=None,
                 serial_number_=None,
                 vendor_name_=None,
                 vendor_number_=None,
                 bus_type_=None):
        """
        :param model_name_: model_name
        :type model_name_: str
        :param model_number_: model_number
        :type model_number_: long
        :param serial_number_: serial_number
        :type serial_number_: str
        :param vendor_name_: vendor_name
        :type vendor_name_: str
        :param vendor_number_: vendor_number
        :type vendor_number_: long
        :param bus_type_: bus_type
        :type bus_type_: str
        """
        self.model_name = model_name_
        self.model_number = model_number_
        self.serial_number = serial_number_
        self.vendor_name = vendor_name_
        self.vendor_number = vendor_number_
        self.bus_type = bus_type_

    @classmethod
    def from_dict(cls, body_dict):
        """
        Create a new instance of :class:`AssetIdentification` using a dictionary.

        :param body_dict: A dictionary representing the body.
        :type body_dict: dict
        :return: A new instance of :class:`AssetIdentification`.
        :rtype: AssetIdentification
        """
        model_name_ = _deserialize(body_dict.get('modelName'), 'str')
        model_number_ = _deserialize(body_dict.get('modelNumber'), 'long')
        serial_number_ = _deserialize(body_dict.get('serialNumber'), 'str')
        vendor_name_ = _deserialize(body_dict.get('vendorName'), 'str')
        vendor_number_ = _deserialize(body_dict.get('vendorNumber'), 'long')
        bus_type_ = _deserialize(body_dict.get('busType'), 'str')
        return cls(
            model_name_=model_name_,
            model_number_=model_number_,
            serial_number_=serial_number_,
            vendor_name_=vendor_name_,
            vendor_number_=vendor_number_,
            bus_type_=bus_type_
        )

    @classmethod
    def from_json(cls, body_json):
        """
        Create a new instance of :class:`AssetIdentification` using a JSON string.

        :param body_json: A string in JSON format representing the body.
        :type body_json: str
        :return: A new instance of :class:`AssetIdentification`.
        :rtype: AssetIdentification
        """
        body_dict = json.loads(body_json)
        return cls.from_dict(body_dict)

    @classmethod
    def from_body_bytes(cls, body_bytes):
        """
        Create a new instance of :class:`AssetIdentification` using a body
        of type :class:`bytes` or :class:`bytearray`.

        :param body_bytes: The body to use.
        :type body_bytes: bytes or bytearray
        :return: A new instance of :class:`AssetIdentification`.
        :rtype: AssetIdentification
        """
        body_json = str(body_bytes, 'utf-8')
        return cls.from_json(body_json)

    def to_dict(self):
        """
        Returns a dictionary representing the data in this object.

        :return: A dictionary representing the data in this object.
        :rtype: dict
        """
        model_name_ = _serialize(self.model_name)
        model_number_ = _serialize(self.model_number)
        serial_number_ = _serialize(self.serial_number)
        vendor_name_ = _serialize(self.vendor_name)
        vendor_number_ = _serialize(self.vendor_number)
        bus_type_ = _serialize(self.bus_type)
        return {
            'modelName': model_name_,
            'modelNumber': model_number_,
            'serialNumber': serial_number_,
            'vendorName': vendor_name_,
            'vendorNumber': vendor_number_,
            'busType': bus_type_
        }

    def to_json(self):
        """
        Returns a JSON string representing the data in this object.

        :return: A JSON string representing the data in this object.
        :rtype: str
        """
        body_dict = self.to_dict()
        return json.dumps(body_dict, separators=(',', ':'))

    def to_body_bytes(self):
        """
        Returns a :class:`bytearray` body representing the data in this object.

        :return: A :class:`bytearray` body representing the data in this object.
        :rtype: bytearray
        """
        body_json = self.to_json()
        return bytearray(body_json, 'utf-8')


class Property(object):
    """
    Property custom data type.
    """
    def __init__(self,
                 key_=None,
                 value_=None):
        """
        :param key_: key
        :type key_: str
        :param value_: value
        :type value_: str
        """
        self.key = key_
        self.value = value_

    @classmethod
    def from_dict(cls, body_dict):
        """
        Create a new instance of :class:`Property` using a dictionary.

        :param body_dict: A dictionary representing the body.
        :type body_dict: dict
        :return: A new instance of :class:`Property`.
        :rtype: Property
        """
        key_ = _deserialize(body_dict.get('key'), 'str')
        value_ = _deserialize(body_dict.get('value'), 'str')
        return cls(
            key_=key_,
            value_=value_
        )

    @classmethod
    def from_json(cls, body_json):
        """
        Create a new instance of :class:`Property` using a JSON string.

        :param body_json: A string in JSON format representing the body.
        :type body_json: str
        :return: A new instance of :class:`Property`.
        :rtype: Property
        """
        body_dict = json.loads(body_json)
        return cls.from_dict(body_dict)

    @classmethod
    def from_body_bytes(cls, body_bytes):
        """
        Create a new instance of :class:`Property` using a body
        of type :class:`bytes` or :class:`bytearray`.

        :param body_bytes: The body to use.
        :type body_bytes: bytes or bytearray
        :return: A new instance of :class:`Property`.
        :rtype: Property
        """
        body_json = str(body_bytes, 'utf-8')
        return cls.from_json(body_json)

    def to_dict(self):
        """
        Returns a dictionary representing the data in this object.

        :return: A dictionary representing the data in this object.
        :rtype: dict
        """
        key_ = _serialize(self.key)
        value_ = _serialize(self.value)
        return {
            'key': key_,
            'value': value_
        }

    def to_json(self):
        """
        Returns a JSON string representing the data in this object.

        :return: A JSON string representing the data in this object.
        :rtype: str
        """
        body_dict = self.to_dict()
        return json.dumps(body_dict, separators=(',', ':'))

    def to_body_bytes(self):
        """
        Returns a :class:`bytearray` body representing the data in this object.

        :return: A :class:`bytearray` body representing the data in this object.
        :rtype: bytearray
        """
        body_json = self.to_json()
        return bytearray(body_json, 'utf-8')


class AssetUpdateProperties(object):
    """
    AssetUpdateProperties custom data type.
    """
    def __init__(self,
                 asset_identification_=None,
                 properties_=None):
        """
        :param asset_identification_: asset_identification
        :type asset_identification_: AssetIdentification
        :param properties_: properties
        :type properties_: list(Property)
        """
        self.asset_identification = asset_identification_
        self.properties = properties_

    @classmethod
    def from_dict(cls, body_dict):
        """
        Create a new instance of :class:`AssetUpdateProperties` using a dictionary.

        :param body_dict: A dictionary representing the body.
        :type body_dict: dict
        :return: A new instance of :class:`AssetUpdateProperties`.
        :rtype: AssetUpdateProperties
        """
        asset_identification_ = _deserialize(body_dict.get('assetIdentification'), 'AssetIdentification')
        properties_ = _deserialize(body_dict.get('properties'), 'list(Property)')
        return cls(
            asset_identification_=asset_identification_,
            properties_=properties_
        )

    @classmethod
    def from_json(cls, body_json):
        """
        Create a new instance of :class:`AssetUpdateProperties` using a JSON string.

        :param body_json: A string in JSON format representing the body.
        :type body_json: str
        :return: A new instance of :class:`AssetUpdateProperties`.
        :rtype: AssetUpdateProperties
        """
        body_dict = json.loads(body_json)
        return cls.from_dict(body_dict)

    @classmethod
    def from_body_bytes(cls, body_bytes):
        """
        Create a new instance of :class:`AssetUpdateProperties` using a body
        of type :class:`bytes` or :class:`bytearray`.

        :param body_bytes: The body to use.
        :type body_bytes: bytes or bytearray
        :return: A new instance of :class:`AssetUpdateProperties`.
        :rtype: AssetUpdateProperties
        """
        body_json = str(body_bytes, 'utf-8')
        return cls.from_json(body_json)

    def to_dict(self):
        """
        Returns a dictionary representing the data in this object.

        :return: A dictionary representing the data in this object.
        :rtype: dict
        """
        asset_identification_ = _serialize(self.asset_identification)
        properties_ = _serialize(self.properties)
        return {
            'assetIdentification': asset_identification_,
            'properties': properties_
        }

    def to_json(self):
        """
        Returns a JSON string representing the data in this object.

        :return: A JSON string representing the data in this object.
        :rtype: str
        """
        body_dict = self.to_dict()
        return json.dumps(body_dict, separators=(',', ':'))

    def to_body_bytes(self):
        """
        Returns a :class:`bytearray` body representing the data in this object.

        :return: A :class:`bytearray` body representing the data in this object.
        :rtype: bytearray
        """
        body_json = self.to_json()
        return bytearray(body_json, 'utf-8')


class CalibrationPolicy(object):
    """
    CalibrationPolicy custom data type.
    """
    def __init__(self,
                 days_for_approaching_calibration_due_date_=None):
        """
        :param days_for_approaching_calibration_due_date_: days_for_approaching_calibration_due_date
        :type days_for_approaching_calibration_due_date_: int
        """
        self.days_for_approaching_calibration_due_date = days_for_approaching_calibration_due_date_  # pylint: disable=invalid-name

    @classmethod
    def from_dict(cls, body_dict):
        """
        Create a new instance of :class:`CalibrationPolicy` using a dictionary.

        :param body_dict: A dictionary representing the body.
        :type body_dict: dict
        :return: A new instance of :class:`CalibrationPolicy`.
        :rtype: CalibrationPolicy
        """
        days_for_approaching_calibration_due_date_ = _deserialize(body_dict.get('daysForApproachingCalibrationDueDate'), 'int')  # pylint: disable=invalid-name
        return cls(
            days_for_approaching_calibration_due_date_=days_for_approaching_calibration_due_date_
        )

    @classmethod
    def from_json(cls, body_json):
        """
        Create a new instance of :class:`CalibrationPolicy` using a JSON string.

        :param body_json: A string in JSON format representing the body.
        :type body_json: str
        :return: A new instance of :class:`CalibrationPolicy`.
        :rtype: CalibrationPolicy
        """
        body_dict = json.loads(body_json)
        return cls.from_dict(body_dict)

    @classmethod
    def from_body_bytes(cls, body_bytes):
        """
        Create a new instance of :class:`CalibrationPolicy` using a body
        of type :class:`bytes` or :class:`bytearray`.

        :param body_bytes: The body to use.
        :type body_bytes: bytes or bytearray
        :return: A new instance of :class:`CalibrationPolicy`.
        :rtype: CalibrationPolicy
        """
        body_json = str(body_bytes, 'utf-8')
        return cls.from_json(body_json)

    def to_dict(self):
        """
        Returns a dictionary representing the data in this object.

        :return: A dictionary representing the data in this object.
        :rtype: dict
        """
        days_for_approaching_calibration_due_date_ = _serialize(self.days_for_approaching_calibration_due_date)  # pylint: disable=invalid-name
        return {
            'daysForApproachingCalibrationDueDate': days_for_approaching_calibration_due_date_
        }

    def to_json(self):
        """
        Returns a JSON string representing the data in this object.

        :return: A JSON string representing the data in this object.
        :rtype: str
        """
        body_dict = self.to_dict()
        return json.dumps(body_dict, separators=(',', ':'))

    def to_body_bytes(self):
        """
        Returns a :class:`bytearray` body representing the data in this object.

        :return: A :class:`bytearray` body representing the data in this object.
        :rtype: bytearray
        """
        body_json = self.to_json()
        return bytearray(body_json, 'utf-8')


class DateIntervalModel(object):
    """
    DateIntervalModel custom data type.
    """
    def __init__(self,
                 start_date_=None,
                 end_date_=None):
        """
        :param start_date_: start_date
        :type start_date_: datetime
        :param end_date_: end_date
        :type end_date_: datetime
        """
        self.start_date = start_date_
        self.end_date = end_date_

    @classmethod
    def from_dict(cls, body_dict):
        """
        Create a new instance of :class:`DateIntervalModel` using a dictionary.

        :param body_dict: A dictionary representing the body.
        :type body_dict: dict
        :return: A new instance of :class:`DateIntervalModel`.
        :rtype: DateIntervalModel
        """
        start_date_ = _deserialize(body_dict.get('startDate'), 'datetime')
        end_date_ = _deserialize(body_dict.get('endDate'), 'datetime')
        return cls(
            start_date_=start_date_,
            end_date_=end_date_
        )

    @classmethod
    def from_json(cls, body_json):
        """
        Create a new instance of :class:`DateIntervalModel` using a JSON string.

        :param body_json: A string in JSON format representing the body.
        :type body_json: str
        :return: A new instance of :class:`DateIntervalModel`.
        :rtype: DateIntervalModel
        """
        body_dict = json.loads(body_json)
        return cls.from_dict(body_dict)

    @classmethod
    def from_body_bytes(cls, body_bytes):
        """
        Create a new instance of :class:`DateIntervalModel` using a body
        of type :class:`bytes` or :class:`bytearray`.

        :param body_bytes: The body to use.
        :type body_bytes: bytes or bytearray
        :return: A new instance of :class:`DateIntervalModel`.
        :rtype: DateIntervalModel
        """
        body_json = str(body_bytes, 'utf-8')
        return cls.from_json(body_json)

    def to_dict(self):
        """
        Returns a dictionary representing the data in this object.

        :return: A dictionary representing the data in this object.
        :rtype: dict
        """
        start_date_ = _serialize(self.start_date)
        end_date_ = _serialize(self.end_date)
        return {
            'startDate': start_date_,
            'endDate': end_date_
        }

    def to_json(self):
        """
        Returns a JSON string representing the data in this object.

        :return: A JSON string representing the data in this object.
        :rtype: str
        """
        body_dict = self.to_dict()
        return json.dumps(body_dict, separators=(',', ':'))

    def to_body_bytes(self):
        """
        Returns a :class:`bytearray` body representing the data in this object.

        :return: A :class:`bytearray` body representing the data in this object.
        :rtype: bytearray
        """
        body_json = self.to_json()
        return bytearray(body_json, 'utf-8')


class OverallAvailabilityInSystemItemModel(object):
    """
    OverallAvailabilityInSystemItemModel custom data type.
    """
    def __init__(self,
                 system_name_=None,
                 availability_percentage_=None):
        """
        :param system_name_: system_name
        :type system_name_: str
        :param availability_percentage_: availability_percentage
        :type availability_percentage_: float
        """
        self.system_name = system_name_
        self.availability_percentage = availability_percentage_

    @classmethod
    def from_dict(cls, body_dict):
        """
        Create a new instance of :class:`OverallAvailabilityInSystemItemModel` using a dictionary.

        :param body_dict: A dictionary representing the body.
        :type body_dict: dict
        :return: A new instance of :class:`OverallAvailabilityInSystemItemModel`.
        :rtype: OverallAvailabilityInSystemItemModel
        """
        system_name_ = _deserialize(body_dict.get('systemName'), 'str')
        availability_percentage_ = _deserialize(body_dict.get('availabilityPercentage'), 'float')
        return cls(
            system_name_=system_name_,
            availability_percentage_=availability_percentage_
        )

    @classmethod
    def from_json(cls, body_json):
        """
        Create a new instance of :class:`OverallAvailabilityInSystemItemModel` using a JSON string.

        :param body_json: A string in JSON format representing the body.
        :type body_json: str
        :return: A new instance of :class:`OverallAvailabilityInSystemItemModel`.
        :rtype: OverallAvailabilityInSystemItemModel
        """
        body_dict = json.loads(body_json)
        return cls.from_dict(body_dict)

    @classmethod
    def from_body_bytes(cls, body_bytes):
        """
        Create a new instance of :class:`OverallAvailabilityInSystemItemModel` using a body
        of type :class:`bytes` or :class:`bytearray`.

        :param body_bytes: The body to use.
        :type body_bytes: bytes or bytearray
        :return: A new instance of :class:`OverallAvailabilityInSystemItemModel`.
        :rtype: OverallAvailabilityInSystemItemModel
        """
        body_json = str(body_bytes, 'utf-8')
        return cls.from_json(body_json)

    def to_dict(self):
        """
        Returns a dictionary representing the data in this object.

        :return: A dictionary representing the data in this object.
        :rtype: dict
        """
        system_name_ = _serialize(self.system_name)
        availability_percentage_ = _serialize(self.availability_percentage)
        return {
            'systemName': system_name_,
            'availabilityPercentage': availability_percentage_
        }

    def to_json(self):
        """
        Returns a JSON string representing the data in this object.

        :return: A JSON string representing the data in this object.
        :rtype: str
        """
        body_dict = self.to_dict()
        return json.dumps(body_dict, separators=(',', ':'))

    def to_body_bytes(self):
        """
        Returns a :class:`bytearray` body representing the data in this object.

        :return: A :class:`bytearray` body representing the data in this object.
        :rtype: bytearray
        """
        body_json = self.to_json()
        return bytearray(body_json, 'utf-8')


class AssetWithAvailabilityModel(object):
    """
    AssetWithAvailabilityModel custom data type.
    """
    def __init__(self,
                 asset_name_=None,
                 asset_identifier_=None,
                 interval_=None,
                 availability_in_system_=None):
        """
        :param asset_name_: asset_name
        :type asset_name_: str
        :param asset_identifier_: asset_identifier
        :type asset_identifier_: str
        :param interval_: interval
        :type interval_: DateIntervalModel
        :param availability_in_system_: availability_in_system
        :type availability_in_system_: list(OverallAvailabilityInSystemItemModel)
        """
        self.asset_name = asset_name_
        self.asset_identifier = asset_identifier_
        self.interval = interval_
        self.availability_in_system = availability_in_system_

    @classmethod
    def from_dict(cls, body_dict):
        """
        Create a new instance of :class:`AssetWithAvailabilityModel` using a dictionary.

        :param body_dict: A dictionary representing the body.
        :type body_dict: dict
        :return: A new instance of :class:`AssetWithAvailabilityModel`.
        :rtype: AssetWithAvailabilityModel
        """
        asset_name_ = _deserialize(body_dict.get('assetName'), 'str')
        asset_identifier_ = _deserialize(body_dict.get('assetIdentifier'), 'str')
        interval_ = _deserialize(body_dict.get('interval'), 'DateIntervalModel')
        availability_in_system_ = _deserialize(body_dict.get('availabilityInSystem'), 'list(OverallAvailabilityInSystemItemModel)')
        return cls(
            asset_name_=asset_name_,
            asset_identifier_=asset_identifier_,
            interval_=interval_,
            availability_in_system_=availability_in_system_
        )

    @classmethod
    def from_json(cls, body_json):
        """
        Create a new instance of :class:`AssetWithAvailabilityModel` using a JSON string.

        :param body_json: A string in JSON format representing the body.
        :type body_json: str
        :return: A new instance of :class:`AssetWithAvailabilityModel`.
        :rtype: AssetWithAvailabilityModel
        """
        body_dict = json.loads(body_json)
        return cls.from_dict(body_dict)

    @classmethod
    def from_body_bytes(cls, body_bytes):
        """
        Create a new instance of :class:`AssetWithAvailabilityModel` using a body
        of type :class:`bytes` or :class:`bytearray`.

        :param body_bytes: The body to use.
        :type body_bytes: bytes or bytearray
        :return: A new instance of :class:`AssetWithAvailabilityModel`.
        :rtype: AssetWithAvailabilityModel
        """
        body_json = str(body_bytes, 'utf-8')
        return cls.from_json(body_json)

    def to_dict(self):
        """
        Returns a dictionary representing the data in this object.

        :return: A dictionary representing the data in this object.
        :rtype: dict
        """
        asset_name_ = _serialize(self.asset_name)
        asset_identifier_ = _serialize(self.asset_identifier)
        interval_ = _serialize(self.interval)
        availability_in_system_ = _serialize(self.availability_in_system)
        return {
            'assetName': asset_name_,
            'assetIdentifier': asset_identifier_,
            'interval': interval_,
            'availabilityInSystem': availability_in_system_
        }

    def to_json(self):
        """
        Returns a JSON string representing the data in this object.

        :return: A JSON string representing the data in this object.
        :rtype: str
        """
        body_dict = self.to_dict()
        return json.dumps(body_dict, separators=(',', ':'))

    def to_body_bytes(self):
        """
        Returns a :class:`bytearray` body representing the data in this object.

        :return: A :class:`bytearray` body representing the data in this object.
        :rtype: bytearray
        """
        body_json = self.to_json()
        return bytearray(body_json, 'utf-8')


class ErrorModel(object):
    """
    ErrorModel custom data type.
    """
    def __init__(self,
                 name_=None,
                 message_=None,
                 args_=None,
                 inner_errors_=None,
                 resource_id_=None,
                 resource_type_=None):
        """
        :param name_: name
        :type name_: str
        :param message_: message
        :type message_: str
        :param args_: args
        :type args_: list(str)
        :param inner_errors_: inner_errors
        :type inner_errors_: list(ErrorModel)
        :param resource_id_: resource_id
        :type resource_id_: str
        :param resource_type_: resource_type
        :type resource_type_: str
        """
        self.name = name_
        self.message = message_
        self.args = args_
        self.inner_errors = inner_errors_
        self.resource_id = resource_id_
        self.resource_type = resource_type_

    @classmethod
    def from_dict(cls, body_dict):
        """
        Create a new instance of :class:`ErrorModel` using a dictionary.

        :param body_dict: A dictionary representing the body.
        :type body_dict: dict
        :return: A new instance of :class:`ErrorModel`.
        :rtype: ErrorModel
        """
        name_ = _deserialize(body_dict.get('name'), 'str')
        message_ = _deserialize(body_dict.get('message'), 'str')
        args_ = _deserialize(body_dict.get('args'), 'list(str)')
        inner_errors_ = _deserialize(body_dict.get('innerErrors'), 'list(ErrorModel)')
        resource_id_ = _deserialize(body_dict.get('resourceId'), 'str')
        resource_type_ = _deserialize(body_dict.get('resourceType'), 'str')
        return cls(
            name_=name_,
            message_=message_,
            args_=args_,
            inner_errors_=inner_errors_,
            resource_id_=resource_id_,
            resource_type_=resource_type_
        )

    @classmethod
    def from_json(cls, body_json):
        """
        Create a new instance of :class:`ErrorModel` using a JSON string.

        :param body_json: A string in JSON format representing the body.
        :type body_json: str
        :return: A new instance of :class:`ErrorModel`.
        :rtype: ErrorModel
        """
        body_dict = json.loads(body_json)
        return cls.from_dict(body_dict)

    @classmethod
    def from_body_bytes(cls, body_bytes):
        """
        Create a new instance of :class:`ErrorModel` using a body
        of type :class:`bytes` or :class:`bytearray`.

        :param body_bytes: The body to use.
        :type body_bytes: bytes or bytearray
        :return: A new instance of :class:`ErrorModel`.
        :rtype: ErrorModel
        """
        body_json = str(body_bytes, 'utf-8')
        return cls.from_json(body_json)

    def to_dict(self):
        """
        Returns a dictionary representing the data in this object.

        :return: A dictionary representing the data in this object.
        :rtype: dict
        """
        name_ = _serialize(self.name)
        message_ = _serialize(self.message)
        args_ = _serialize(self.args)
        inner_errors_ = _serialize(self.inner_errors)
        resource_id_ = _serialize(self.resource_id)
        resource_type_ = _serialize(self.resource_type)
        return {
            'name': name_,
            'message': message_,
            'args': args_,
            'innerErrors': inner_errors_,
            'resourceId': resource_id_,
            'resourceType': resource_type_
        }

    def to_json(self):
        """
        Returns a JSON string representing the data in this object.

        :return: A JSON string representing the data in this object.
        :rtype: str
        """
        body_dict = self.to_dict()
        return json.dumps(body_dict, separators=(',', ':'))

    def to_body_bytes(self):
        """
        Returns a :class:`bytearray` body representing the data in this object.

        :return: A :class:`bytearray` body representing the data in this object.
        :rtype: bytearray
        """
        body_json = self.to_json()
        return bytearray(body_json, 'utf-8')


#
# AssetPerformanceManagement service
#


class AssetPerformanceManagementMinionCalibrationUpdatedBroadcast(BroadcastMessage):
    """
    AssetPerformanceManagementMinionCalibrationUpdatedBroadcast JSON broadcast message.
    """
    MESSAGE_NAME = 'AssetPerformanceManagementMinionCalibrationUpdatedBroadcast'

    def __init__(self,
                 minion_id_=None,
                 assets_=None,
                 message_version_=None):
        """
        :param minion_id_: minion_id
        :type minion_id_: str
        :param assets_: assets
        :type assets_: list(AssetData)
        :param message_version_: message_version
        :type message_version_: int
        """
        self.minion_id = minion_id_
        self.assets = assets_
        self.message_version = message_version_
        header = MessageHeader()
        header.message_name = self.MESSAGE_NAME
        header.content_type = JSON_MESSAGE_CONTENT_TYPE
        routing_key = MessageHeader.generate_routing_key(None, self.MESSAGE_NAME)
        header.routing_key = routing_key
        super(AssetPerformanceManagementMinionCalibrationUpdatedBroadcast, self).__init__(header, None)

    @classmethod
    def from_dict(cls, body_dict):
        """
        Create a new instance of :class:`AssetPerformanceManagementMinionCalibrationUpdatedBroadcast` using a dictionary.

        :param body_dict: The body as a dictionary.
        :type body_dict: dict
        :return: A new instance of :class:`AssetPerformanceManagementMinionCalibrationUpdatedBroadcast`.
        :rtype: AssetPerformanceManagementMinionCalibrationUpdatedBroadcast
        """
        minion_id_ = _deserialize(body_dict.get('minionId'), 'str')
        assets_ = _deserialize(body_dict.get('assets'), 'list(AssetData)')
        message_version_ = _deserialize(body_dict.get('messageVersion'), 'int')
        return cls(
            minion_id_=minion_id_,
            assets_=assets_,
            message_version_=message_version_
        )

    @classmethod
    def from_json(cls, body_json):
        """
        Create a new instance of :class:`AssetPerformanceManagementMinionCalibrationUpdatedBroadcast` using a JSON string.

        :param body_json: A string in JSON format representing the body.
        :type body_json: str
        :return: A new instance of :class:`AssetPerformanceManagementMinionCalibrationUpdatedBroadcast`.
        :rtype: AssetPerformanceManagementMinionCalibrationUpdatedBroadcast
        """
        body_dict = json.loads(body_json)
        return cls.from_dict(body_dict)

    @classmethod
    def from_body_bytes(cls, body_bytes):
        """
        Create a new instance of :class:`AssetPerformanceManagementMinionCalibrationUpdatedBroadcast` using a body
        of type :class:`bytes` or :class:`bytearray`,

        :param body_bytes: The body to use.
        :type body_bytes: bytes or bytearray
        :return: A new instance of :class:`AssetPerformanceManagementMinionCalibrationUpdatedBroadcast`.
        :rtype: AssetPerformanceManagementMinionCalibrationUpdatedBroadcast
        """
        body_json = str(body_bytes, 'utf-8')
        return cls.from_json(body_json)

    @classmethod
    def from_message(cls, message):
        """
        Create a new instance of :class`AssetPerformanceManagementMinionCalibrationUpdatedBroadcast` using a
        :class:`systemlink.messagebus.message_base.MessageBase` derived message.

        :param message: The message to use as the basis for this class instance.
        :type message: systemlink.messagebus.message_base.MessageBase
        :return: A new instance of :class`AssetPerformanceManagementMinionCalibrationUpdatedBroadcast`.
        :rtype: AssetPerformanceManagementMinionCalibrationUpdatedBroadcast
        """
        instance = cls.from_body_bytes(message.body_bytes)
        instance.correlation_id = message.correlation_id
        instance.reply_to = message.reply_to
        return instance

    def to_dict(self):
        """
        Returns a dictionary representing the data in this object.

        :return: A dictionary representing the data in this object.
        :rtype: dict
        """
        minion_id_ = _serialize(self.minion_id)
        assets_ = _serialize(self.assets)
        message_version_ = _serialize(self.message_version)
        return {
            'minionId': minion_id_,
            'assets': assets_,
            'messageVersion': message_version_
        }

    def to_json(self):
        """
        Returns a JSON string representing the data in this object.

        :return: A JSON string representing the data in this object.
        :rtype: str
        """
        body_dict = self.to_dict()
        return json.dumps(body_dict, separators=(',', ':'))

    def to_body_bytes(self):
        """
        Returns a :class:`bytearray` body representing the data in this object.

        :return: A :class:`bytearray` body representing the data in this object.
        :rtype: bytearray
        """
        body_json = self.to_json()
        return bytearray(body_json, 'utf-8')

    def to_message(self, request_message=None):
        """
        Returns a :class:`systemlink.messagebus.message_base.MessageBase`
        object representing the data in this object.

        :param request_message: Request message if this is a response.
        :type request_message: systemlink.messagebus.message_base.MessageBase or None
        :return: A :class:`systemlink.messagebus.message_base.MessageBase`
            object representing the data in this object.
        :rtype: systemlink.messagebus.message_base.MessageBase
        """
        header = self.header
        if request_message:
            request_header = request_message.header
            header.correlation_id = request_header.correlation_id
        body_bytes = self.to_body_bytes()
        return MessageBase(header, body_bytes)

    @property
    def body_bytes(self):
        """
        Returns a :class:`bytes` body representing the data in this object.

        :return: A :class:`bytes` body representing the data in this object.
        :rtype: bytes
        """
        self._body = self.to_body_bytes()  # pylint: disable=attribute-defined-outside-init
        return self._body


class AssetPerformanceManagementMinionAssetsUpdatedBroadcast(BroadcastMessage):
    """
    AssetPerformanceManagementMinionAssetsUpdatedBroadcast JSON broadcast message.
    """
    MESSAGE_NAME = 'AssetPerformanceManagementMinionAssetsUpdatedBroadcast'

    def __init__(self,
                 message_version_=None,
                 minion_id_=None,
                 assets_=None):
        """
        :param message_version_: message_version
        :type message_version_: int
        :param minion_id_: minion_id
        :type minion_id_: str
        :param assets_: assets
        :type assets_: list(AssetUpdateProperties)
        """
        self.message_version = message_version_
        self.minion_id = minion_id_
        self.assets = assets_
        header = MessageHeader()
        header.message_name = self.MESSAGE_NAME
        header.content_type = JSON_MESSAGE_CONTENT_TYPE
        routing_key = MessageHeader.generate_routing_key(None, self.MESSAGE_NAME)
        header.routing_key = routing_key
        super(AssetPerformanceManagementMinionAssetsUpdatedBroadcast, self).__init__(header, None)

    @classmethod
    def from_dict(cls, body_dict):
        """
        Create a new instance of :class:`AssetPerformanceManagementMinionAssetsUpdatedBroadcast` using a dictionary.

        :param body_dict: The body as a dictionary.
        :type body_dict: dict
        :return: A new instance of :class:`AssetPerformanceManagementMinionAssetsUpdatedBroadcast`.
        :rtype: AssetPerformanceManagementMinionAssetsUpdatedBroadcast
        """
        message_version_ = _deserialize(body_dict.get('messageVersion'), 'int')
        minion_id_ = _deserialize(body_dict.get('minionId'), 'str')
        assets_ = _deserialize(body_dict.get('assets'), 'list(AssetUpdateProperties)')
        return cls(
            message_version_=message_version_,
            minion_id_=minion_id_,
            assets_=assets_
        )

    @classmethod
    def from_json(cls, body_json):
        """
        Create a new instance of :class:`AssetPerformanceManagementMinionAssetsUpdatedBroadcast` using a JSON string.

        :param body_json: A string in JSON format representing the body.
        :type body_json: str
        :return: A new instance of :class:`AssetPerformanceManagementMinionAssetsUpdatedBroadcast`.
        :rtype: AssetPerformanceManagementMinionAssetsUpdatedBroadcast
        """
        body_dict = json.loads(body_json)
        return cls.from_dict(body_dict)

    @classmethod
    def from_body_bytes(cls, body_bytes):
        """
        Create a new instance of :class:`AssetPerformanceManagementMinionAssetsUpdatedBroadcast` using a body
        of type :class:`bytes` or :class:`bytearray`,

        :param body_bytes: The body to use.
        :type body_bytes: bytes or bytearray
        :return: A new instance of :class:`AssetPerformanceManagementMinionAssetsUpdatedBroadcast`.
        :rtype: AssetPerformanceManagementMinionAssetsUpdatedBroadcast
        """
        body_json = str(body_bytes, 'utf-8')
        return cls.from_json(body_json)

    @classmethod
    def from_message(cls, message):
        """
        Create a new instance of :class`AssetPerformanceManagementMinionAssetsUpdatedBroadcast` using a
        :class:`systemlink.messagebus.message_base.MessageBase` derived message.

        :param message: The message to use as the basis for this class instance.
        :type message: systemlink.messagebus.message_base.MessageBase
        :return: A new instance of :class`AssetPerformanceManagementMinionAssetsUpdatedBroadcast`.
        :rtype: AssetPerformanceManagementMinionAssetsUpdatedBroadcast
        """
        instance = cls.from_body_bytes(message.body_bytes)
        instance.correlation_id = message.correlation_id
        instance.reply_to = message.reply_to
        return instance

    def to_dict(self):
        """
        Returns a dictionary representing the data in this object.

        :return: A dictionary representing the data in this object.
        :rtype: dict
        """
        message_version_ = _serialize(self.message_version)
        minion_id_ = _serialize(self.minion_id)
        assets_ = _serialize(self.assets)
        return {
            'messageVersion': message_version_,
            'minionId': minion_id_,
            'assets': assets_
        }

    def to_json(self):
        """
        Returns a JSON string representing the data in this object.

        :return: A JSON string representing the data in this object.
        :rtype: str
        """
        body_dict = self.to_dict()
        return json.dumps(body_dict, separators=(',', ':'))

    def to_body_bytes(self):
        """
        Returns a :class:`bytearray` body representing the data in this object.

        :return: A :class:`bytearray` body representing the data in this object.
        :rtype: bytearray
        """
        body_json = self.to_json()
        return bytearray(body_json, 'utf-8')

    def to_message(self, request_message=None):
        """
        Returns a :class:`systemlink.messagebus.message_base.MessageBase`
        object representing the data in this object.

        :param request_message: Request message if this is a response.
        :type request_message: systemlink.messagebus.message_base.MessageBase or None
        :return: A :class:`systemlink.messagebus.message_base.MessageBase`
            object representing the data in this object.
        :rtype: systemlink.messagebus.message_base.MessageBase
        """
        header = self.header
        if request_message:
            request_header = request_message.header
            header.correlation_id = request_header.correlation_id
        body_bytes = self.to_body_bytes()
        return MessageBase(header, body_bytes)

    @property
    def body_bytes(self):
        """
        Returns a :class:`bytes` body representing the data in this object.

        :return: A :class:`bytes` body representing the data in this object.
        :rtype: bytes
        """
        self._body = self.to_body_bytes()  # pylint: disable=attribute-defined-outside-init
        return self._body


class AssetPerformanceManagementCalibrationPolicyUpdatedBroadcast(BroadcastMessage):
    """
    AssetPerformanceManagementCalibrationPolicyUpdatedBroadcast JSON broadcast message.
    """
    MESSAGE_NAME = 'AssetPerformanceManagementCalibrationPolicyUpdatedBroadcast'

    def __init__(self,
                 calibration_policy_=None):
        """
        :param calibration_policy_: calibration_policy
        :type calibration_policy_: CalibrationPolicy
        """
        self.calibration_policy = calibration_policy_
        header = MessageHeader()
        header.message_name = self.MESSAGE_NAME
        header.content_type = JSON_MESSAGE_CONTENT_TYPE
        routing_key = MessageHeader.generate_routing_key(None, self.MESSAGE_NAME)
        header.routing_key = routing_key
        super(AssetPerformanceManagementCalibrationPolicyUpdatedBroadcast, self).__init__(header, None)

    @classmethod
    def from_dict(cls, body_dict):
        """
        Create a new instance of :class:`AssetPerformanceManagementCalibrationPolicyUpdatedBroadcast` using a dictionary.

        :param body_dict: The body as a dictionary.
        :type body_dict: dict
        :return: A new instance of :class:`AssetPerformanceManagementCalibrationPolicyUpdatedBroadcast`.
        :rtype: AssetPerformanceManagementCalibrationPolicyUpdatedBroadcast
        """
        calibration_policy_ = _deserialize(body_dict.get('calibrationPolicy'), 'CalibrationPolicy')
        return cls(
            calibration_policy_=calibration_policy_
        )

    @classmethod
    def from_json(cls, body_json):
        """
        Create a new instance of :class:`AssetPerformanceManagementCalibrationPolicyUpdatedBroadcast` using a JSON string.

        :param body_json: A string in JSON format representing the body.
        :type body_json: str
        :return: A new instance of :class:`AssetPerformanceManagementCalibrationPolicyUpdatedBroadcast`.
        :rtype: AssetPerformanceManagementCalibrationPolicyUpdatedBroadcast
        """
        body_dict = json.loads(body_json)
        return cls.from_dict(body_dict)

    @classmethod
    def from_body_bytes(cls, body_bytes):
        """
        Create a new instance of :class:`AssetPerformanceManagementCalibrationPolicyUpdatedBroadcast` using a body
        of type :class:`bytes` or :class:`bytearray`,

        :param body_bytes: The body to use.
        :type body_bytes: bytes or bytearray
        :return: A new instance of :class:`AssetPerformanceManagementCalibrationPolicyUpdatedBroadcast`.
        :rtype: AssetPerformanceManagementCalibrationPolicyUpdatedBroadcast
        """
        body_json = str(body_bytes, 'utf-8')
        return cls.from_json(body_json)

    @classmethod
    def from_message(cls, message):
        """
        Create a new instance of :class`AssetPerformanceManagementCalibrationPolicyUpdatedBroadcast` using a
        :class:`systemlink.messagebus.message_base.MessageBase` derived message.

        :param message: The message to use as the basis for this class instance.
        :type message: systemlink.messagebus.message_base.MessageBase
        :return: A new instance of :class`AssetPerformanceManagementCalibrationPolicyUpdatedBroadcast`.
        :rtype: AssetPerformanceManagementCalibrationPolicyUpdatedBroadcast
        """
        instance = cls.from_body_bytes(message.body_bytes)
        instance.correlation_id = message.correlation_id
        instance.reply_to = message.reply_to
        return instance

    def to_dict(self):
        """
        Returns a dictionary representing the data in this object.

        :return: A dictionary representing the data in this object.
        :rtype: dict
        """
        calibration_policy_ = _serialize(self.calibration_policy)
        return {
            'calibrationPolicy': calibration_policy_
        }

    def to_json(self):
        """
        Returns a JSON string representing the data in this object.

        :return: A JSON string representing the data in this object.
        :rtype: str
        """
        body_dict = self.to_dict()
        return json.dumps(body_dict, separators=(',', ':'))

    def to_body_bytes(self):
        """
        Returns a :class:`bytearray` body representing the data in this object.

        :return: A :class:`bytearray` body representing the data in this object.
        :rtype: bytearray
        """
        body_json = self.to_json()
        return bytearray(body_json, 'utf-8')

    def to_message(self, request_message=None):
        """
        Returns a :class:`systemlink.messagebus.message_base.MessageBase`
        object representing the data in this object.

        :param request_message: Request message if this is a response.
        :type request_message: systemlink.messagebus.message_base.MessageBase or None
        :return: A :class:`systemlink.messagebus.message_base.MessageBase`
            object representing the data in this object.
        :rtype: systemlink.messagebus.message_base.MessageBase
        """
        header = self.header
        if request_message:
            request_header = request_message.header
            header.correlation_id = request_header.correlation_id
        body_bytes = self.to_body_bytes()
        return MessageBase(header, body_bytes)

    @property
    def body_bytes(self):
        """
        Returns a :class:`bytes` body representing the data in this object.

        :return: A :class:`bytes` body representing the data in this object.
        :rtype: bytes
        """
        self._body = self.to_body_bytes()  # pylint: disable=attribute-defined-outside-init
        return self._body


class AssetPerformanceManagementQueryAssetsRequest(RequestMessage):
    """
    AssetPerformanceManagementQueryAssetsRequest JSON request message.
    """
    MESSAGE_NAME = 'AssetPerformanceManagementQueryAssetsRequest'

    def __init__(self,
                 ids_=None,
                 skip_=None,
                 take_=None,
                 order_by_=None,
                 order_by_descending_=None,
                 filter_=None):
        """
        :param ids_: ids
        :type ids_: list(str)
        :param skip_: skip
        :type skip_: int
        :param take_: take
        :type take_: int
        :param order_by_: order_by
        :type order_by_: str
        :param order_by_descending_: order_by_descending
        :type order_by_descending_: bool
        :param filter_: filter
        :type filter_: QueryAssetsFilter
        """
        self.ids = ids_
        self.skip = skip_
        self.take = take_
        self.order_by = order_by_
        self.order_by_descending = order_by_descending_
        self.filter = filter_
        header = MessageHeader()
        header.message_name = self.MESSAGE_NAME
        header.content_type = JSON_MESSAGE_CONTENT_TYPE
        routing_key = MessageHeader.generate_routing_key('AssetPerformanceManagement', self.MESSAGE_NAME)
        header.routing_key = routing_key
        super(AssetPerformanceManagementQueryAssetsRequest, self).__init__(header, None)

    @classmethod
    def from_dict(cls, body_dict):
        """
        Create a new instance of :class:`AssetPerformanceManagementQueryAssetsRequest` using a dictionary.

        :param body_dict: The body as a dictionary.
        :type body_dict: dict
        :return: A new instance of :class:`AssetPerformanceManagementQueryAssetsRequest`.
        :rtype: AssetPerformanceManagementQueryAssetsRequest
        """
        ids_ = _deserialize(body_dict.get('ids'), 'list(str)')
        skip_ = _deserialize(body_dict.get('skip'), 'int')
        take_ = _deserialize(body_dict.get('take'), 'int')
        order_by_ = _deserialize(body_dict.get('orderBy'), 'str')
        order_by_descending_ = _deserialize(body_dict.get('orderByDescending'), 'bool')
        filter_ = _deserialize(body_dict.get('filter'), 'QueryAssetsFilter')
        return cls(
            ids_=ids_,
            skip_=skip_,
            take_=take_,
            order_by_=order_by_,
            order_by_descending_=order_by_descending_,
            filter_=filter_
        )

    @classmethod
    def from_json(cls, body_json):
        """
        Create a new instance of :class:`AssetPerformanceManagementQueryAssetsRequest` using a JSON string.

        :param body_json: A string in JSON format representing the body.
        :type body_json: str
        :return: A new instance of :class:`AssetPerformanceManagementQueryAssetsRequest`.
        :rtype: AssetPerformanceManagementQueryAssetsRequest
        """
        body_dict = json.loads(body_json)
        return cls.from_dict(body_dict)

    @classmethod
    def from_body_bytes(cls, body_bytes):
        """
        Create a new instance of :class:`AssetPerformanceManagementQueryAssetsRequest` using a body
        of type :class:`bytes` or :class:`bytearray`,

        :param body_bytes: The body to use.
        :type body_bytes: bytes or bytearray
        :return: A new instance of :class:`AssetPerformanceManagementQueryAssetsRequest`.
        :rtype: AssetPerformanceManagementQueryAssetsRequest
        """
        body_json = str(body_bytes, 'utf-8')
        return cls.from_json(body_json)

    @classmethod
    def from_message(cls, message):
        """
        Create a new instance of :class`AssetPerformanceManagementQueryAssetsRequest` using a
        :class:`systemlink.messagebus.message_base.MessageBase` derived message.

        :param message: The message to use as the basis for this class instance.
        :type message: systemlink.messagebus.message_base.MessageBase
        :return: A new instance of :class`AssetPerformanceManagementQueryAssetsRequest`.
        :rtype: AssetPerformanceManagementQueryAssetsRequest
        """
        instance = cls.from_body_bytes(message.body_bytes)
        instance.correlation_id = message.correlation_id
        instance.reply_to = message.reply_to
        return instance

    def to_dict(self):
        """
        Returns a dictionary representing the data in this object.

        :return: A dictionary representing the data in this object.
        :rtype: dict
        """
        ids_ = _serialize(self.ids)
        skip_ = _serialize(self.skip)
        take_ = _serialize(self.take)
        order_by_ = _serialize(self.order_by)
        order_by_descending_ = _serialize(self.order_by_descending)
        filter_ = _serialize(self.filter)
        return {
            'ids': ids_,
            'skip': skip_,
            'take': take_,
            'orderBy': order_by_,
            'orderByDescending': order_by_descending_,
            'filter': filter_
        }

    def to_json(self):
        """
        Returns a JSON string representing the data in this object.

        :return: A JSON string representing the data in this object.
        :rtype: str
        """
        body_dict = self.to_dict()
        return json.dumps(body_dict, separators=(',', ':'))

    def to_body_bytes(self):
        """
        Returns a :class:`bytearray` body representing the data in this object.

        :return: A :class:`bytearray` body representing the data in this object.
        :rtype: bytearray
        """
        body_json = self.to_json()
        return bytearray(body_json, 'utf-8')

    def to_message(self, request_message=None):
        """
        Returns a :class:`systemlink.messagebus.message_base.MessageBase`
        object representing the data in this object.

        :param request_message: Request message if this is a response.
        :type request_message: systemlink.messagebus.message_base.MessageBase or None
        :return: A :class:`systemlink.messagebus.message_base.MessageBase`
            object representing the data in this object.
        :rtype: systemlink.messagebus.message_base.MessageBase
        """
        header = self.header
        if request_message:
            request_header = request_message.header
            header.correlation_id = request_header.correlation_id
        body_bytes = self.to_body_bytes()
        return MessageBase(header, body_bytes)

    @property
    def body_bytes(self):
        """
        Returns a :class:`bytes` body representing the data in this object.

        :return: A :class:`bytes` body representing the data in this object.
        :rtype: bytes
        """
        self._body = self.to_body_bytes()  # pylint: disable=attribute-defined-outside-init
        return self._body


class AssetPerformanceManagementQueryAssetsResponse(ResponseMessage):
    """
    AssetPerformanceManagementQueryAssetsResponse JSON response message.
    """
    MESSAGE_NAME = 'AssetPerformanceManagementQueryAssetsResponse'

    def __init__(self,
                 request_message,
                 assets_=None,
                 total_count_=None):
        """
        :param request_message: The request_message to use for reply information. May be None.
        :type request_message: systemlink.messagebus.message_base.MessageBase or None
        :param assets_: assets
        :type assets_: list(AssetModel)
        :param total_count_: total_count
        :type total_count_: int
        """
        self.assets = assets_
        self.total_count = total_count_
        header = MessageHeader()
        header.message_name = self.MESSAGE_NAME
        header.content_type = JSON_MESSAGE_CONTENT_TYPE
        # If request_message is None, routing key needs to be set outside this constructor.
        if request_message:
            header.correlation_id = request_message.correlation_id
            routing_key = MessageHeader.generate_routing_key(request_message.reply_to, self.MESSAGE_NAME)
            header.routing_key = routing_key
        super(AssetPerformanceManagementQueryAssetsResponse, self).__init__(header, None)

    @classmethod
    def from_dict(cls, request_message, body_dict):
        """
        Create a new instance of :class:`AssetPerformanceManagementQueryAssetsResponse` using a dictionary.

        :param request_message: The request_message to use for reply information. May be None.
        :type request_message: systemlink.messagebus.message_base.MessageBase or None
        :param body_dict: The body as a dictionary.
        :type body_dict: dict
        :return: A new instance of :class:`AssetPerformanceManagementQueryAssetsResponse`.
        :rtype: AssetPerformanceManagementQueryAssetsResponse
        """
        assets_ = _deserialize(body_dict.get('assets'), 'list(AssetModel)')
        total_count_ = _deserialize(body_dict.get('totalCount'), 'int')
        return cls(
            request_message,
            assets_=assets_,
            total_count_=total_count_
        )

    @classmethod
    def from_json(cls, request_message, body_json):
        """
        Create a new instance of :class:`AssetPerformanceManagementQueryAssetsResponse` using a JSON string.

        :param request_message: The request_message to use for reply information. May be None.
        :type request_message: systemlink.messagebus.message_base.MessageBase or None
        :param body_json: A string in JSON format representing the body.
        :type body_json: str
        :return: A new instance of :class:`AssetPerformanceManagementQueryAssetsResponse`.
        :rtype: AssetPerformanceManagementQueryAssetsResponse
        """
        body_dict = json.loads(body_json)
        return cls.from_dict(request_message, body_dict)

    @classmethod
    def from_body_bytes(cls, request_message, body_bytes):
        """
        Create a new instance of :class:`AssetPerformanceManagementQueryAssetsResponse` using a body
        of type :class:`bytes` or :class:`bytearray`,

        :param request_message: The request_message to use for reply information. May be None.
        :type request_message: systemlink.messagebus.message_base.MessageBase or None
        :param body_bytes: The body to use.
        :type body_bytes: bytes or bytearray
        :return: A new instance of :class:`AssetPerformanceManagementQueryAssetsResponse`.
        :rtype: AssetPerformanceManagementQueryAssetsResponse
        """
        body_json = str(body_bytes, 'utf-8')
        return cls.from_json(request_message, body_json)

    @classmethod
    def from_message(cls, message):
        """
        Create a new instance of :class`AssetPerformanceManagementQueryAssetsResponse` using a
        :class:`systemlink.messagebus.message_base.MessageBase` derived message.

        :param message: The message to use as the basis for this class instance.
        :type message: systemlink.messagebus.message_base.MessageBase
        :return: A new instance of :class`AssetPerformanceManagementQueryAssetsResponse`.
        :rtype: AssetPerformanceManagementQueryAssetsResponse
        """
        instance = cls.from_body_bytes(message, message.body_bytes)
        instance.correlation_id = message.correlation_id
        instance.reply_to = message.reply_to
        routing_key = MessageHeader.generate_routing_key(message.reply_to, cls.MESSAGE_NAME)
        instance.routing_key = routing_key
        return instance

    def to_dict(self):
        """
        Returns a dictionary representing the data in this object.

        :return: A dictionary representing the data in this object.
        :rtype: dict
        """
        assets_ = _serialize(self.assets)
        total_count_ = _serialize(self.total_count)
        return {
            'assets': assets_,
            'totalCount': total_count_
        }

    def to_json(self):
        """
        Returns a JSON string representing the data in this object.

        :return: A JSON string representing the data in this object.
        :rtype: str
        """
        body_dict = self.to_dict()
        return json.dumps(body_dict, separators=(',', ':'))

    def to_body_bytes(self):
        """
        Returns a :class:`bytearray` body representing the data in this object.

        :return: A :class:`bytearray` body representing the data in this object.
        :rtype: bytearray
        """
        body_json = self.to_json()
        return bytearray(body_json, 'utf-8')

    def to_message(self, request_message=None):
        """
        Returns a :class:`systemlink.messagebus.message_base.MessageBase`
        object representing the data in this object.

        :param request_message: Request message if this is a response.
        :type request_message: systemlink.messagebus.message_base.MessageBase or None
        :return: A :class:`systemlink.messagebus.message_base.MessageBase`
            object representing the data in this object.
        :rtype: systemlink.messagebus.message_base.MessageBase
        """
        header = self.header
        if request_message:
            request_header = request_message.header
            header.correlation_id = request_header.correlation_id
            routing_key = MessageHeader.generate_routing_key(request_header.reply_to, self.MESSAGE_NAME)
            header.routing_key = routing_key
        body_bytes = self.to_body_bytes()
        return MessageBase(header, body_bytes)

    @property
    def body_bytes(self):
        """
        Returns a :class:`bytes` body representing the data in this object.

        :return: A :class:`bytes` body representing the data in this object.
        :rtype: bytes
        """
        self._body = self.to_body_bytes()  # pylint: disable=attribute-defined-outside-init
        return self._body


class AssetPerformanceManagementQueryAssetsForFileIngestionRequest(RequestMessage):
    """
    AssetPerformanceManagementQueryAssetsForFileIngestionRequest JSON request message.
    """
    MESSAGE_NAME = 'AssetPerformanceManagementQueryAssetsForFileIngestionRequest'

    def __init__(self,
                 ids_=None,
                 skip_=None,
                 take_=None,
                 order_by_=None,
                 order_by_descending_=None,
                 filter_=None):
        """
        :param ids_: ids
        :type ids_: list(str)
        :param skip_: skip
        :type skip_: int
        :param take_: take
        :type take_: int
        :param order_by_: order_by
        :type order_by_: str
        :param order_by_descending_: order_by_descending
        :type order_by_descending_: bool
        :param filter_: filter
        :type filter_: QueryAssetsFilter
        """
        self.ids = ids_
        self.skip = skip_
        self.take = take_
        self.order_by = order_by_
        self.order_by_descending = order_by_descending_
        self.filter = filter_
        header = MessageHeader()
        header.message_name = self.MESSAGE_NAME
        header.content_type = JSON_MESSAGE_CONTENT_TYPE
        routing_key = MessageHeader.generate_routing_key('AssetPerformanceManagement', self.MESSAGE_NAME)
        header.routing_key = routing_key
        super(AssetPerformanceManagementQueryAssetsForFileIngestionRequest, self).__init__(header, None)

    @classmethod
    def from_dict(cls, body_dict):
        """
        Create a new instance of :class:`AssetPerformanceManagementQueryAssetsForFileIngestionRequest` using a dictionary.

        :param body_dict: The body as a dictionary.
        :type body_dict: dict
        :return: A new instance of :class:`AssetPerformanceManagementQueryAssetsForFileIngestionRequest`.
        :rtype: AssetPerformanceManagementQueryAssetsForFileIngestionRequest
        """
        ids_ = _deserialize(body_dict.get('ids'), 'list(str)')
        skip_ = _deserialize(body_dict.get('skip'), 'int')
        take_ = _deserialize(body_dict.get('take'), 'int')
        order_by_ = _deserialize(body_dict.get('orderBy'), 'str')
        order_by_descending_ = _deserialize(body_dict.get('orderByDescending'), 'bool')
        filter_ = _deserialize(body_dict.get('filter'), 'QueryAssetsFilter')
        return cls(
            ids_=ids_,
            skip_=skip_,
            take_=take_,
            order_by_=order_by_,
            order_by_descending_=order_by_descending_,
            filter_=filter_
        )

    @classmethod
    def from_json(cls, body_json):
        """
        Create a new instance of :class:`AssetPerformanceManagementQueryAssetsForFileIngestionRequest` using a JSON string.

        :param body_json: A string in JSON format representing the body.
        :type body_json: str
        :return: A new instance of :class:`AssetPerformanceManagementQueryAssetsForFileIngestionRequest`.
        :rtype: AssetPerformanceManagementQueryAssetsForFileIngestionRequest
        """
        body_dict = json.loads(body_json)
        return cls.from_dict(body_dict)

    @classmethod
    def from_body_bytes(cls, body_bytes):
        """
        Create a new instance of :class:`AssetPerformanceManagementQueryAssetsForFileIngestionRequest` using a body
        of type :class:`bytes` or :class:`bytearray`,

        :param body_bytes: The body to use.
        :type body_bytes: bytes or bytearray
        :return: A new instance of :class:`AssetPerformanceManagementQueryAssetsForFileIngestionRequest`.
        :rtype: AssetPerformanceManagementQueryAssetsForFileIngestionRequest
        """
        body_json = str(body_bytes, 'utf-8')
        return cls.from_json(body_json)

    @classmethod
    def from_message(cls, message):
        """
        Create a new instance of :class`AssetPerformanceManagementQueryAssetsForFileIngestionRequest` using a
        :class:`systemlink.messagebus.message_base.MessageBase` derived message.

        :param message: The message to use as the basis for this class instance.
        :type message: systemlink.messagebus.message_base.MessageBase
        :return: A new instance of :class`AssetPerformanceManagementQueryAssetsForFileIngestionRequest`.
        :rtype: AssetPerformanceManagementQueryAssetsForFileIngestionRequest
        """
        instance = cls.from_body_bytes(message.body_bytes)
        instance.correlation_id = message.correlation_id
        instance.reply_to = message.reply_to
        return instance

    def to_dict(self):
        """
        Returns a dictionary representing the data in this object.

        :return: A dictionary representing the data in this object.
        :rtype: dict
        """
        ids_ = _serialize(self.ids)
        skip_ = _serialize(self.skip)
        take_ = _serialize(self.take)
        order_by_ = _serialize(self.order_by)
        order_by_descending_ = _serialize(self.order_by_descending)
        filter_ = _serialize(self.filter)
        return {
            'ids': ids_,
            'skip': skip_,
            'take': take_,
            'orderBy': order_by_,
            'orderByDescending': order_by_descending_,
            'filter': filter_
        }

    def to_json(self):
        """
        Returns a JSON string representing the data in this object.

        :return: A JSON string representing the data in this object.
        :rtype: str
        """
        body_dict = self.to_dict()
        return json.dumps(body_dict, separators=(',', ':'))

    def to_body_bytes(self):
        """
        Returns a :class:`bytearray` body representing the data in this object.

        :return: A :class:`bytearray` body representing the data in this object.
        :rtype: bytearray
        """
        body_json = self.to_json()
        return bytearray(body_json, 'utf-8')

    def to_message(self, request_message=None):
        """
        Returns a :class:`systemlink.messagebus.message_base.MessageBase`
        object representing the data in this object.

        :param request_message: Request message if this is a response.
        :type request_message: systemlink.messagebus.message_base.MessageBase or None
        :return: A :class:`systemlink.messagebus.message_base.MessageBase`
            object representing the data in this object.
        :rtype: systemlink.messagebus.message_base.MessageBase
        """
        header = self.header
        if request_message:
            request_header = request_message.header
            header.correlation_id = request_header.correlation_id
        body_bytes = self.to_body_bytes()
        return MessageBase(header, body_bytes)

    @property
    def body_bytes(self):
        """
        Returns a :class:`bytes` body representing the data in this object.

        :return: A :class:`bytes` body representing the data in this object.
        :rtype: bytes
        """
        self._body = self.to_body_bytes()  # pylint: disable=attribute-defined-outside-init
        return self._body


class AssetPerformanceManagementQueryAssetsForFileIngestionResponse(ResponseMessage):
    """
    AssetPerformanceManagementQueryAssetsForFileIngestionResponse JSON response message.
    """
    MESSAGE_NAME = 'AssetPerformanceManagementQueryAssetsForFileIngestionResponse'

    def __init__(self,
                 request_message,
                 file_id_=None):
        """
        :param request_message: The request_message to use for reply information. May be None.
        :type request_message: systemlink.messagebus.message_base.MessageBase or None
        :param file_id_: file_id
        :type file_id_: str
        """
        self.file_id = file_id_
        header = MessageHeader()
        header.message_name = self.MESSAGE_NAME
        header.content_type = JSON_MESSAGE_CONTENT_TYPE
        # If request_message is None, routing key needs to be set outside this constructor.
        if request_message:
            header.correlation_id = request_message.correlation_id
            routing_key = MessageHeader.generate_routing_key(request_message.reply_to, self.MESSAGE_NAME)
            header.routing_key = routing_key
        super(AssetPerformanceManagementQueryAssetsForFileIngestionResponse, self).__init__(header, None)

    @classmethod
    def from_dict(cls, request_message, body_dict):
        """
        Create a new instance of :class:`AssetPerformanceManagementQueryAssetsForFileIngestionResponse` using a dictionary.

        :param request_message: The request_message to use for reply information. May be None.
        :type request_message: systemlink.messagebus.message_base.MessageBase or None
        :param body_dict: The body as a dictionary.
        :type body_dict: dict
        :return: A new instance of :class:`AssetPerformanceManagementQueryAssetsForFileIngestionResponse`.
        :rtype: AssetPerformanceManagementQueryAssetsForFileIngestionResponse
        """
        file_id_ = _deserialize(body_dict.get('fileId'), 'str')
        return cls(
            request_message,
            file_id_=file_id_
        )

    @classmethod
    def from_json(cls, request_message, body_json):
        """
        Create a new instance of :class:`AssetPerformanceManagementQueryAssetsForFileIngestionResponse` using a JSON string.

        :param request_message: The request_message to use for reply information. May be None.
        :type request_message: systemlink.messagebus.message_base.MessageBase or None
        :param body_json: A string in JSON format representing the body.
        :type body_json: str
        :return: A new instance of :class:`AssetPerformanceManagementQueryAssetsForFileIngestionResponse`.
        :rtype: AssetPerformanceManagementQueryAssetsForFileIngestionResponse
        """
        body_dict = json.loads(body_json)
        return cls.from_dict(request_message, body_dict)

    @classmethod
    def from_body_bytes(cls, request_message, body_bytes):
        """
        Create a new instance of :class:`AssetPerformanceManagementQueryAssetsForFileIngestionResponse` using a body
        of type :class:`bytes` or :class:`bytearray`,

        :param request_message: The request_message to use for reply information. May be None.
        :type request_message: systemlink.messagebus.message_base.MessageBase or None
        :param body_bytes: The body to use.
        :type body_bytes: bytes or bytearray
        :return: A new instance of :class:`AssetPerformanceManagementQueryAssetsForFileIngestionResponse`.
        :rtype: AssetPerformanceManagementQueryAssetsForFileIngestionResponse
        """
        body_json = str(body_bytes, 'utf-8')
        return cls.from_json(request_message, body_json)

    @classmethod
    def from_message(cls, message):
        """
        Create a new instance of :class`AssetPerformanceManagementQueryAssetsForFileIngestionResponse` using a
        :class:`systemlink.messagebus.message_base.MessageBase` derived message.

        :param message: The message to use as the basis for this class instance.
        :type message: systemlink.messagebus.message_base.MessageBase
        :return: A new instance of :class`AssetPerformanceManagementQueryAssetsForFileIngestionResponse`.
        :rtype: AssetPerformanceManagementQueryAssetsForFileIngestionResponse
        """
        instance = cls.from_body_bytes(message, message.body_bytes)
        instance.correlation_id = message.correlation_id
        instance.reply_to = message.reply_to
        routing_key = MessageHeader.generate_routing_key(message.reply_to, cls.MESSAGE_NAME)
        instance.routing_key = routing_key
        return instance

    def to_dict(self):
        """
        Returns a dictionary representing the data in this object.

        :return: A dictionary representing the data in this object.
        :rtype: dict
        """
        file_id_ = _serialize(self.file_id)
        return {
            'fileId': file_id_
        }

    def to_json(self):
        """
        Returns a JSON string representing the data in this object.

        :return: A JSON string representing the data in this object.
        :rtype: str
        """
        body_dict = self.to_dict()
        return json.dumps(body_dict, separators=(',', ':'))

    def to_body_bytes(self):
        """
        Returns a :class:`bytearray` body representing the data in this object.

        :return: A :class:`bytearray` body representing the data in this object.
        :rtype: bytearray
        """
        body_json = self.to_json()
        return bytearray(body_json, 'utf-8')

    def to_message(self, request_message=None):
        """
        Returns a :class:`systemlink.messagebus.message_base.MessageBase`
        object representing the data in this object.

        :param request_message: Request message if this is a response.
        :type request_message: systemlink.messagebus.message_base.MessageBase or None
        :return: A :class:`systemlink.messagebus.message_base.MessageBase`
            object representing the data in this object.
        :rtype: systemlink.messagebus.message_base.MessageBase
        """
        header = self.header
        if request_message:
            request_header = request_message.header
            header.correlation_id = request_header.correlation_id
            routing_key = MessageHeader.generate_routing_key(request_header.reply_to, self.MESSAGE_NAME)
            header.routing_key = routing_key
        body_bytes = self.to_body_bytes()
        return MessageBase(header, body_bytes)

    @property
    def body_bytes(self):
        """
        Returns a :class:`bytes` body representing the data in this object.

        :return: A :class:`bytes` body representing the data in this object.
        :rtype: bytes
        """
        self._body = self.to_body_bytes()  # pylint: disable=attribute-defined-outside-init
        return self._body


class AssetPerformanceManagementQueryAssetsV2Request(RequestMessage):
    """
    AssetPerformanceManagementQueryAssetsV2Request JSON request message.
    """
    MESSAGE_NAME = 'AssetPerformanceManagementQueryAssetsV2Request'

    def __init__(self,
                 ids_=None,
                 skip_=None,
                 take_=None,
                 order_by_=None,
                 order_by_descending_=None,
                 filter_=None):
        """
        :param ids_: ids
        :type ids_: list(str)
        :param skip_: skip
        :type skip_: int
        :param take_: take
        :type take_: int
        :param order_by_: order_by
        :type order_by_: str
        :param order_by_descending_: order_by_descending
        :type order_by_descending_: bool
        :param filter_: filter
        :type filter_: str
        """
        self.ids = ids_
        self.skip = skip_
        self.take = take_
        self.order_by = order_by_
        self.order_by_descending = order_by_descending_
        self.filter = filter_
        header = MessageHeader()
        header.message_name = self.MESSAGE_NAME
        header.content_type = JSON_MESSAGE_CONTENT_TYPE
        routing_key = MessageHeader.generate_routing_key('AssetPerformanceManagement', self.MESSAGE_NAME)
        header.routing_key = routing_key
        super(AssetPerformanceManagementQueryAssetsV2Request, self).__init__(header, None)

    @classmethod
    def from_dict(cls, body_dict):
        """
        Create a new instance of :class:`AssetPerformanceManagementQueryAssetsV2Request` using a dictionary.

        :param body_dict: The body as a dictionary.
        :type body_dict: dict
        :return: A new instance of :class:`AssetPerformanceManagementQueryAssetsV2Request`.
        :rtype: AssetPerformanceManagementQueryAssetsV2Request
        """
        ids_ = _deserialize(body_dict.get('ids'), 'list(str)')
        skip_ = _deserialize(body_dict.get('skip'), 'int')
        take_ = _deserialize(body_dict.get('take'), 'int')
        order_by_ = _deserialize(body_dict.get('orderBy'), 'str')
        order_by_descending_ = _deserialize(body_dict.get('orderByDescending'), 'bool')
        filter_ = _deserialize(body_dict.get('filter'), 'str')
        return cls(
            ids_=ids_,
            skip_=skip_,
            take_=take_,
            order_by_=order_by_,
            order_by_descending_=order_by_descending_,
            filter_=filter_
        )

    @classmethod
    def from_json(cls, body_json):
        """
        Create a new instance of :class:`AssetPerformanceManagementQueryAssetsV2Request` using a JSON string.

        :param body_json: A string in JSON format representing the body.
        :type body_json: str
        :return: A new instance of :class:`AssetPerformanceManagementQueryAssetsV2Request`.
        :rtype: AssetPerformanceManagementQueryAssetsV2Request
        """
        body_dict = json.loads(body_json)
        return cls.from_dict(body_dict)

    @classmethod
    def from_body_bytes(cls, body_bytes):
        """
        Create a new instance of :class:`AssetPerformanceManagementQueryAssetsV2Request` using a body
        of type :class:`bytes` or :class:`bytearray`,

        :param body_bytes: The body to use.
        :type body_bytes: bytes or bytearray
        :return: A new instance of :class:`AssetPerformanceManagementQueryAssetsV2Request`.
        :rtype: AssetPerformanceManagementQueryAssetsV2Request
        """
        body_json = str(body_bytes, 'utf-8')
        return cls.from_json(body_json)

    @classmethod
    def from_message(cls, message):
        """
        Create a new instance of :class`AssetPerformanceManagementQueryAssetsV2Request` using a
        :class:`systemlink.messagebus.message_base.MessageBase` derived message.

        :param message: The message to use as the basis for this class instance.
        :type message: systemlink.messagebus.message_base.MessageBase
        :return: A new instance of :class`AssetPerformanceManagementQueryAssetsV2Request`.
        :rtype: AssetPerformanceManagementQueryAssetsV2Request
        """
        instance = cls.from_body_bytes(message.body_bytes)
        instance.correlation_id = message.correlation_id
        instance.reply_to = message.reply_to
        return instance

    def to_dict(self):
        """
        Returns a dictionary representing the data in this object.

        :return: A dictionary representing the data in this object.
        :rtype: dict
        """
        ids_ = _serialize(self.ids)
        skip_ = _serialize(self.skip)
        take_ = _serialize(self.take)
        order_by_ = _serialize(self.order_by)
        order_by_descending_ = _serialize(self.order_by_descending)
        filter_ = _serialize(self.filter)
        return {
            'ids': ids_,
            'skip': skip_,
            'take': take_,
            'orderBy': order_by_,
            'orderByDescending': order_by_descending_,
            'filter': filter_
        }

    def to_json(self):
        """
        Returns a JSON string representing the data in this object.

        :return: A JSON string representing the data in this object.
        :rtype: str
        """
        body_dict = self.to_dict()
        return json.dumps(body_dict, separators=(',', ':'))

    def to_body_bytes(self):
        """
        Returns a :class:`bytearray` body representing the data in this object.

        :return: A :class:`bytearray` body representing the data in this object.
        :rtype: bytearray
        """
        body_json = self.to_json()
        return bytearray(body_json, 'utf-8')

    def to_message(self, request_message=None):
        """
        Returns a :class:`systemlink.messagebus.message_base.MessageBase`
        object representing the data in this object.

        :param request_message: Request message if this is a response.
        :type request_message: systemlink.messagebus.message_base.MessageBase or None
        :return: A :class:`systemlink.messagebus.message_base.MessageBase`
            object representing the data in this object.
        :rtype: systemlink.messagebus.message_base.MessageBase
        """
        header = self.header
        if request_message:
            request_header = request_message.header
            header.correlation_id = request_header.correlation_id
        body_bytes = self.to_body_bytes()
        return MessageBase(header, body_bytes)

    @property
    def body_bytes(self):
        """
        Returns a :class:`bytes` body representing the data in this object.

        :return: A :class:`bytes` body representing the data in this object.
        :rtype: bytes
        """
        self._body = self.to_body_bytes()  # pylint: disable=attribute-defined-outside-init
        return self._body


class AssetPerformanceManagementQueryAssetsV2Response(ResponseMessage):
    """
    AssetPerformanceManagementQueryAssetsV2Response JSON response message.
    """
    MESSAGE_NAME = 'AssetPerformanceManagementQueryAssetsV2Response'

    def __init__(self,
                 request_message,
                 assets_=None,
                 total_count_=None):
        """
        :param request_message: The request_message to use for reply information. May be None.
        :type request_message: systemlink.messagebus.message_base.MessageBase or None
        :param assets_: assets
        :type assets_: list(AssetModel)
        :param total_count_: total_count
        :type total_count_: int
        """
        self.assets = assets_
        self.total_count = total_count_
        header = MessageHeader()
        header.message_name = self.MESSAGE_NAME
        header.content_type = JSON_MESSAGE_CONTENT_TYPE
        # If request_message is None, routing key needs to be set outside this constructor.
        if request_message:
            header.correlation_id = request_message.correlation_id
            routing_key = MessageHeader.generate_routing_key(request_message.reply_to, self.MESSAGE_NAME)
            header.routing_key = routing_key
        super(AssetPerformanceManagementQueryAssetsV2Response, self).__init__(header, None)

    @classmethod
    def from_dict(cls, request_message, body_dict):
        """
        Create a new instance of :class:`AssetPerformanceManagementQueryAssetsV2Response` using a dictionary.

        :param request_message: The request_message to use for reply information. May be None.
        :type request_message: systemlink.messagebus.message_base.MessageBase or None
        :param body_dict: The body as a dictionary.
        :type body_dict: dict
        :return: A new instance of :class:`AssetPerformanceManagementQueryAssetsV2Response`.
        :rtype: AssetPerformanceManagementQueryAssetsV2Response
        """
        assets_ = _deserialize(body_dict.get('assets'), 'list(AssetModel)')
        total_count_ = _deserialize(body_dict.get('totalCount'), 'int')
        return cls(
            request_message,
            assets_=assets_,
            total_count_=total_count_
        )

    @classmethod
    def from_json(cls, request_message, body_json):
        """
        Create a new instance of :class:`AssetPerformanceManagementQueryAssetsV2Response` using a JSON string.

        :param request_message: The request_message to use for reply information. May be None.
        :type request_message: systemlink.messagebus.message_base.MessageBase or None
        :param body_json: A string in JSON format representing the body.
        :type body_json: str
        :return: A new instance of :class:`AssetPerformanceManagementQueryAssetsV2Response`.
        :rtype: AssetPerformanceManagementQueryAssetsV2Response
        """
        body_dict = json.loads(body_json)
        return cls.from_dict(request_message, body_dict)

    @classmethod
    def from_body_bytes(cls, request_message, body_bytes):
        """
        Create a new instance of :class:`AssetPerformanceManagementQueryAssetsV2Response` using a body
        of type :class:`bytes` or :class:`bytearray`,

        :param request_message: The request_message to use for reply information. May be None.
        :type request_message: systemlink.messagebus.message_base.MessageBase or None
        :param body_bytes: The body to use.
        :type body_bytes: bytes or bytearray
        :return: A new instance of :class:`AssetPerformanceManagementQueryAssetsV2Response`.
        :rtype: AssetPerformanceManagementQueryAssetsV2Response
        """
        body_json = str(body_bytes, 'utf-8')
        return cls.from_json(request_message, body_json)

    @classmethod
    def from_message(cls, message):
        """
        Create a new instance of :class`AssetPerformanceManagementQueryAssetsV2Response` using a
        :class:`systemlink.messagebus.message_base.MessageBase` derived message.

        :param message: The message to use as the basis for this class instance.
        :type message: systemlink.messagebus.message_base.MessageBase
        :return: A new instance of :class`AssetPerformanceManagementQueryAssetsV2Response`.
        :rtype: AssetPerformanceManagementQueryAssetsV2Response
        """
        instance = cls.from_body_bytes(message, message.body_bytes)
        instance.correlation_id = message.correlation_id
        instance.reply_to = message.reply_to
        routing_key = MessageHeader.generate_routing_key(message.reply_to, cls.MESSAGE_NAME)
        instance.routing_key = routing_key
        return instance

    def to_dict(self):
        """
        Returns a dictionary representing the data in this object.

        :return: A dictionary representing the data in this object.
        :rtype: dict
        """
        assets_ = _serialize(self.assets)
        total_count_ = _serialize(self.total_count)
        return {
            'assets': assets_,
            'totalCount': total_count_
        }

    def to_json(self):
        """
        Returns a JSON string representing the data in this object.

        :return: A JSON string representing the data in this object.
        :rtype: str
        """
        body_dict = self.to_dict()
        return json.dumps(body_dict, separators=(',', ':'))

    def to_body_bytes(self):
        """
        Returns a :class:`bytearray` body representing the data in this object.

        :return: A :class:`bytearray` body representing the data in this object.
        :rtype: bytearray
        """
        body_json = self.to_json()
        return bytearray(body_json, 'utf-8')

    def to_message(self, request_message=None):
        """
        Returns a :class:`systemlink.messagebus.message_base.MessageBase`
        object representing the data in this object.

        :param request_message: Request message if this is a response.
        :type request_message: systemlink.messagebus.message_base.MessageBase or None
        :return: A :class:`systemlink.messagebus.message_base.MessageBase`
            object representing the data in this object.
        :rtype: systemlink.messagebus.message_base.MessageBase
        """
        header = self.header
        if request_message:
            request_header = request_message.header
            header.correlation_id = request_header.correlation_id
            routing_key = MessageHeader.generate_routing_key(request_header.reply_to, self.MESSAGE_NAME)
            header.routing_key = routing_key
        body_bytes = self.to_body_bytes()
        return MessageBase(header, body_bytes)

    @property
    def body_bytes(self):
        """
        Returns a :class:`bytes` body representing the data in this object.

        :return: A :class:`bytes` body representing the data in this object.
        :rtype: bytes
        """
        self._body = self.to_body_bytes()  # pylint: disable=attribute-defined-outside-init
        return self._body


class AssetPerformanceManagementQueryAssetsForFileIngestionV2Request(RequestMessage):
    """
    AssetPerformanceManagementQueryAssetsForFileIngestionV2Request JSON request message.
    """
    MESSAGE_NAME = 'AssetPerformanceManagementQueryAssetsForFileIngestionV2Request'

    def __init__(self,
                 ids_=None,
                 skip_=None,
                 take_=None,
                 order_by_=None,
                 order_by_descending_=None,
                 filter_=None):
        """
        :param ids_: ids
        :type ids_: list(str)
        :param skip_: skip
        :type skip_: int
        :param take_: take
        :type take_: int
        :param order_by_: order_by
        :type order_by_: str
        :param order_by_descending_: order_by_descending
        :type order_by_descending_: bool
        :param filter_: filter
        :type filter_: str
        """
        self.ids = ids_
        self.skip = skip_
        self.take = take_
        self.order_by = order_by_
        self.order_by_descending = order_by_descending_
        self.filter = filter_
        header = MessageHeader()
        header.message_name = self.MESSAGE_NAME
        header.content_type = JSON_MESSAGE_CONTENT_TYPE
        routing_key = MessageHeader.generate_routing_key('AssetPerformanceManagement', self.MESSAGE_NAME)
        header.routing_key = routing_key
        super(AssetPerformanceManagementQueryAssetsForFileIngestionV2Request, self).__init__(header, None)

    @classmethod
    def from_dict(cls, body_dict):
        """
        Create a new instance of :class:`AssetPerformanceManagementQueryAssetsForFileIngestionV2Request` using a dictionary.

        :param body_dict: The body as a dictionary.
        :type body_dict: dict
        :return: A new instance of :class:`AssetPerformanceManagementQueryAssetsForFileIngestionV2Request`.
        :rtype: AssetPerformanceManagementQueryAssetsForFileIngestionV2Request
        """
        ids_ = _deserialize(body_dict.get('ids'), 'list(str)')
        skip_ = _deserialize(body_dict.get('skip'), 'int')
        take_ = _deserialize(body_dict.get('take'), 'int')
        order_by_ = _deserialize(body_dict.get('orderBy'), 'str')
        order_by_descending_ = _deserialize(body_dict.get('orderByDescending'), 'bool')
        filter_ = _deserialize(body_dict.get('filter'), 'str')
        return cls(
            ids_=ids_,
            skip_=skip_,
            take_=take_,
            order_by_=order_by_,
            order_by_descending_=order_by_descending_,
            filter_=filter_
        )

    @classmethod
    def from_json(cls, body_json):
        """
        Create a new instance of :class:`AssetPerformanceManagementQueryAssetsForFileIngestionV2Request` using a JSON string.

        :param body_json: A string in JSON format representing the body.
        :type body_json: str
        :return: A new instance of :class:`AssetPerformanceManagementQueryAssetsForFileIngestionV2Request`.
        :rtype: AssetPerformanceManagementQueryAssetsForFileIngestionV2Request
        """
        body_dict = json.loads(body_json)
        return cls.from_dict(body_dict)

    @classmethod
    def from_body_bytes(cls, body_bytes):
        """
        Create a new instance of :class:`AssetPerformanceManagementQueryAssetsForFileIngestionV2Request` using a body
        of type :class:`bytes` or :class:`bytearray`,

        :param body_bytes: The body to use.
        :type body_bytes: bytes or bytearray
        :return: A new instance of :class:`AssetPerformanceManagementQueryAssetsForFileIngestionV2Request`.
        :rtype: AssetPerformanceManagementQueryAssetsForFileIngestionV2Request
        """
        body_json = str(body_bytes, 'utf-8')
        return cls.from_json(body_json)

    @classmethod
    def from_message(cls, message):
        """
        Create a new instance of :class`AssetPerformanceManagementQueryAssetsForFileIngestionV2Request` using a
        :class:`systemlink.messagebus.message_base.MessageBase` derived message.

        :param message: The message to use as the basis for this class instance.
        :type message: systemlink.messagebus.message_base.MessageBase
        :return: A new instance of :class`AssetPerformanceManagementQueryAssetsForFileIngestionV2Request`.
        :rtype: AssetPerformanceManagementQueryAssetsForFileIngestionV2Request
        """
        instance = cls.from_body_bytes(message.body_bytes)
        instance.correlation_id = message.correlation_id
        instance.reply_to = message.reply_to
        return instance

    def to_dict(self):
        """
        Returns a dictionary representing the data in this object.

        :return: A dictionary representing the data in this object.
        :rtype: dict
        """
        ids_ = _serialize(self.ids)
        skip_ = _serialize(self.skip)
        take_ = _serialize(self.take)
        order_by_ = _serialize(self.order_by)
        order_by_descending_ = _serialize(self.order_by_descending)
        filter_ = _serialize(self.filter)
        return {
            'ids': ids_,
            'skip': skip_,
            'take': take_,
            'orderBy': order_by_,
            'orderByDescending': order_by_descending_,
            'filter': filter_
        }

    def to_json(self):
        """
        Returns a JSON string representing the data in this object.

        :return: A JSON string representing the data in this object.
        :rtype: str
        """
        body_dict = self.to_dict()
        return json.dumps(body_dict, separators=(',', ':'))

    def to_body_bytes(self):
        """
        Returns a :class:`bytearray` body representing the data in this object.

        :return: A :class:`bytearray` body representing the data in this object.
        :rtype: bytearray
        """
        body_json = self.to_json()
        return bytearray(body_json, 'utf-8')

    def to_message(self, request_message=None):
        """
        Returns a :class:`systemlink.messagebus.message_base.MessageBase`
        object representing the data in this object.

        :param request_message: Request message if this is a response.
        :type request_message: systemlink.messagebus.message_base.MessageBase or None
        :return: A :class:`systemlink.messagebus.message_base.MessageBase`
            object representing the data in this object.
        :rtype: systemlink.messagebus.message_base.MessageBase
        """
        header = self.header
        if request_message:
            request_header = request_message.header
            header.correlation_id = request_header.correlation_id
        body_bytes = self.to_body_bytes()
        return MessageBase(header, body_bytes)

    @property
    def body_bytes(self):
        """
        Returns a :class:`bytes` body representing the data in this object.

        :return: A :class:`bytes` body representing the data in this object.
        :rtype: bytes
        """
        self._body = self.to_body_bytes()  # pylint: disable=attribute-defined-outside-init
        return self._body


class AssetPerformanceManagementQueryAssetsForFileIngestionV2Response(ResponseMessage):
    """
    AssetPerformanceManagementQueryAssetsForFileIngestionV2Response JSON response message.
    """
    MESSAGE_NAME = 'AssetPerformanceManagementQueryAssetsForFileIngestionV2Response'

    def __init__(self,
                 request_message,
                 file_id_=None):
        """
        :param request_message: The request_message to use for reply information. May be None.
        :type request_message: systemlink.messagebus.message_base.MessageBase or None
        :param file_id_: file_id
        :type file_id_: str
        """
        self.file_id = file_id_
        header = MessageHeader()
        header.message_name = self.MESSAGE_NAME
        header.content_type = JSON_MESSAGE_CONTENT_TYPE
        # If request_message is None, routing key needs to be set outside this constructor.
        if request_message:
            header.correlation_id = request_message.correlation_id
            routing_key = MessageHeader.generate_routing_key(request_message.reply_to, self.MESSAGE_NAME)
            header.routing_key = routing_key
        super(AssetPerformanceManagementQueryAssetsForFileIngestionV2Response, self).__init__(header, None)

    @classmethod
    def from_dict(cls, request_message, body_dict):
        """
        Create a new instance of :class:`AssetPerformanceManagementQueryAssetsForFileIngestionV2Response` using a dictionary.

        :param request_message: The request_message to use for reply information. May be None.
        :type request_message: systemlink.messagebus.message_base.MessageBase or None
        :param body_dict: The body as a dictionary.
        :type body_dict: dict
        :return: A new instance of :class:`AssetPerformanceManagementQueryAssetsForFileIngestionV2Response`.
        :rtype: AssetPerformanceManagementQueryAssetsForFileIngestionV2Response
        """
        file_id_ = _deserialize(body_dict.get('fileId'), 'str')
        return cls(
            request_message,
            file_id_=file_id_
        )

    @classmethod
    def from_json(cls, request_message, body_json):
        """
        Create a new instance of :class:`AssetPerformanceManagementQueryAssetsForFileIngestionV2Response` using a JSON string.

        :param request_message: The request_message to use for reply information. May be None.
        :type request_message: systemlink.messagebus.message_base.MessageBase or None
        :param body_json: A string in JSON format representing the body.
        :type body_json: str
        :return: A new instance of :class:`AssetPerformanceManagementQueryAssetsForFileIngestionV2Response`.
        :rtype: AssetPerformanceManagementQueryAssetsForFileIngestionV2Response
        """
        body_dict = json.loads(body_json)
        return cls.from_dict(request_message, body_dict)

    @classmethod
    def from_body_bytes(cls, request_message, body_bytes):
        """
        Create a new instance of :class:`AssetPerformanceManagementQueryAssetsForFileIngestionV2Response` using a body
        of type :class:`bytes` or :class:`bytearray`,

        :param request_message: The request_message to use for reply information. May be None.
        :type request_message: systemlink.messagebus.message_base.MessageBase or None
        :param body_bytes: The body to use.
        :type body_bytes: bytes or bytearray
        :return: A new instance of :class:`AssetPerformanceManagementQueryAssetsForFileIngestionV2Response`.
        :rtype: AssetPerformanceManagementQueryAssetsForFileIngestionV2Response
        """
        body_json = str(body_bytes, 'utf-8')
        return cls.from_json(request_message, body_json)

    @classmethod
    def from_message(cls, message):
        """
        Create a new instance of :class`AssetPerformanceManagementQueryAssetsForFileIngestionV2Response` using a
        :class:`systemlink.messagebus.message_base.MessageBase` derived message.

        :param message: The message to use as the basis for this class instance.
        :type message: systemlink.messagebus.message_base.MessageBase
        :return: A new instance of :class`AssetPerformanceManagementQueryAssetsForFileIngestionV2Response`.
        :rtype: AssetPerformanceManagementQueryAssetsForFileIngestionV2Response
        """
        instance = cls.from_body_bytes(message, message.body_bytes)
        instance.correlation_id = message.correlation_id
        instance.reply_to = message.reply_to
        routing_key = MessageHeader.generate_routing_key(message.reply_to, cls.MESSAGE_NAME)
        instance.routing_key = routing_key
        return instance

    def to_dict(self):
        """
        Returns a dictionary representing the data in this object.

        :return: A dictionary representing the data in this object.
        :rtype: dict
        """
        file_id_ = _serialize(self.file_id)
        return {
            'fileId': file_id_
        }

    def to_json(self):
        """
        Returns a JSON string representing the data in this object.

        :return: A JSON string representing the data in this object.
        :rtype: str
        """
        body_dict = self.to_dict()
        return json.dumps(body_dict, separators=(',', ':'))

    def to_body_bytes(self):
        """
        Returns a :class:`bytearray` body representing the data in this object.

        :return: A :class:`bytearray` body representing the data in this object.
        :rtype: bytearray
        """
        body_json = self.to_json()
        return bytearray(body_json, 'utf-8')

    def to_message(self, request_message=None):
        """
        Returns a :class:`systemlink.messagebus.message_base.MessageBase`
        object representing the data in this object.

        :param request_message: Request message if this is a response.
        :type request_message: systemlink.messagebus.message_base.MessageBase or None
        :return: A :class:`systemlink.messagebus.message_base.MessageBase`
            object representing the data in this object.
        :rtype: systemlink.messagebus.message_base.MessageBase
        """
        header = self.header
        if request_message:
            request_header = request_message.header
            header.correlation_id = request_header.correlation_id
            routing_key = MessageHeader.generate_routing_key(request_header.reply_to, self.MESSAGE_NAME)
            header.routing_key = routing_key
        body_bytes = self.to_body_bytes()
        return MessageBase(header, body_bytes)

    @property
    def body_bytes(self):
        """
        Returns a :class:`bytes` body representing the data in this object.

        :return: A :class:`bytes` body representing the data in this object.
        :rtype: bytes
        """
        self._body = self.to_body_bytes()  # pylint: disable=attribute-defined-outside-init
        return self._body


class AssetPerformanceManagementQueryAssetsAvailabilityRequest(RequestMessage):
    """
    AssetPerformanceManagementQueryAssetsAvailabilityRequest JSON request message.
    """
    MESSAGE_NAME = 'AssetPerformanceManagementQueryAssetsAvailabilityRequest'

    def __init__(self,
                 asset_ids_=None,
                 intervals_=None):
        """
        :param asset_ids_: asset_ids
        :type asset_ids_: list(str)
        :param intervals_: intervals
        :type intervals_: list(DateIntervalModel)
        """
        self.asset_ids = asset_ids_
        self.intervals = intervals_
        header = MessageHeader()
        header.message_name = self.MESSAGE_NAME
        header.content_type = JSON_MESSAGE_CONTENT_TYPE
        routing_key = MessageHeader.generate_routing_key('AssetPerformanceManagement', self.MESSAGE_NAME)
        header.routing_key = routing_key
        super(AssetPerformanceManagementQueryAssetsAvailabilityRequest, self).__init__(header, None)

    @classmethod
    def from_dict(cls, body_dict):
        """
        Create a new instance of :class:`AssetPerformanceManagementQueryAssetsAvailabilityRequest` using a dictionary.

        :param body_dict: The body as a dictionary.
        :type body_dict: dict
        :return: A new instance of :class:`AssetPerformanceManagementQueryAssetsAvailabilityRequest`.
        :rtype: AssetPerformanceManagementQueryAssetsAvailabilityRequest
        """
        asset_ids_ = _deserialize(body_dict.get('assetIds'), 'list(str)')
        intervals_ = _deserialize(body_dict.get('intervals'), 'list(DateIntervalModel)')
        return cls(
            asset_ids_=asset_ids_,
            intervals_=intervals_
        )

    @classmethod
    def from_json(cls, body_json):
        """
        Create a new instance of :class:`AssetPerformanceManagementQueryAssetsAvailabilityRequest` using a JSON string.

        :param body_json: A string in JSON format representing the body.
        :type body_json: str
        :return: A new instance of :class:`AssetPerformanceManagementQueryAssetsAvailabilityRequest`.
        :rtype: AssetPerformanceManagementQueryAssetsAvailabilityRequest
        """
        body_dict = json.loads(body_json)
        return cls.from_dict(body_dict)

    @classmethod
    def from_body_bytes(cls, body_bytes):
        """
        Create a new instance of :class:`AssetPerformanceManagementQueryAssetsAvailabilityRequest` using a body
        of type :class:`bytes` or :class:`bytearray`,

        :param body_bytes: The body to use.
        :type body_bytes: bytes or bytearray
        :return: A new instance of :class:`AssetPerformanceManagementQueryAssetsAvailabilityRequest`.
        :rtype: AssetPerformanceManagementQueryAssetsAvailabilityRequest
        """
        body_json = str(body_bytes, 'utf-8')
        return cls.from_json(body_json)

    @classmethod
    def from_message(cls, message):
        """
        Create a new instance of :class`AssetPerformanceManagementQueryAssetsAvailabilityRequest` using a
        :class:`systemlink.messagebus.message_base.MessageBase` derived message.

        :param message: The message to use as the basis for this class instance.
        :type message: systemlink.messagebus.message_base.MessageBase
        :return: A new instance of :class`AssetPerformanceManagementQueryAssetsAvailabilityRequest`.
        :rtype: AssetPerformanceManagementQueryAssetsAvailabilityRequest
        """
        instance = cls.from_body_bytes(message.body_bytes)
        instance.correlation_id = message.correlation_id
        instance.reply_to = message.reply_to
        return instance

    def to_dict(self):
        """
        Returns a dictionary representing the data in this object.

        :return: A dictionary representing the data in this object.
        :rtype: dict
        """
        asset_ids_ = _serialize(self.asset_ids)
        intervals_ = _serialize(self.intervals)
        return {
            'assetIds': asset_ids_,
            'intervals': intervals_
        }

    def to_json(self):
        """
        Returns a JSON string representing the data in this object.

        :return: A JSON string representing the data in this object.
        :rtype: str
        """
        body_dict = self.to_dict()
        return json.dumps(body_dict, separators=(',', ':'))

    def to_body_bytes(self):
        """
        Returns a :class:`bytearray` body representing the data in this object.

        :return: A :class:`bytearray` body representing the data in this object.
        :rtype: bytearray
        """
        body_json = self.to_json()
        return bytearray(body_json, 'utf-8')

    def to_message(self, request_message=None):
        """
        Returns a :class:`systemlink.messagebus.message_base.MessageBase`
        object representing the data in this object.

        :param request_message: Request message if this is a response.
        :type request_message: systemlink.messagebus.message_base.MessageBase or None
        :return: A :class:`systemlink.messagebus.message_base.MessageBase`
            object representing the data in this object.
        :rtype: systemlink.messagebus.message_base.MessageBase
        """
        header = self.header
        if request_message:
            request_header = request_message.header
            header.correlation_id = request_header.correlation_id
        body_bytes = self.to_body_bytes()
        return MessageBase(header, body_bytes)

    @property
    def body_bytes(self):
        """
        Returns a :class:`bytes` body representing the data in this object.

        :return: A :class:`bytes` body representing the data in this object.
        :rtype: bytes
        """
        self._body = self.to_body_bytes()  # pylint: disable=attribute-defined-outside-init
        return self._body


class AssetPerformanceManagementQueryAssetsAvailabilityResponse(ResponseMessage):
    """
    AssetPerformanceManagementQueryAssetsAvailabilityResponse JSON response message.
    """
    MESSAGE_NAME = 'AssetPerformanceManagementQueryAssetsAvailabilityResponse'

    def __init__(self,
                 request_message,
                 assets_with_availability_=None,
                 query_error_=None):
        """
        :param request_message: The request_message to use for reply information. May be None.
        :type request_message: systemlink.messagebus.message_base.MessageBase or None
        :param assets_with_availability_: assets_with_availability
        :type assets_with_availability_: list(AssetWithAvailabilityModel)
        :param query_error_: query_error
        :type query_error_: ErrorModel
        """
        self.assets_with_availability = assets_with_availability_
        self.query_error = query_error_
        header = MessageHeader()
        header.message_name = self.MESSAGE_NAME
        header.content_type = JSON_MESSAGE_CONTENT_TYPE
        # If request_message is None, routing key needs to be set outside this constructor.
        if request_message:
            header.correlation_id = request_message.correlation_id
            routing_key = MessageHeader.generate_routing_key(request_message.reply_to, self.MESSAGE_NAME)
            header.routing_key = routing_key
        super(AssetPerformanceManagementQueryAssetsAvailabilityResponse, self).__init__(header, None)

    @classmethod
    def from_dict(cls, request_message, body_dict):
        """
        Create a new instance of :class:`AssetPerformanceManagementQueryAssetsAvailabilityResponse` using a dictionary.

        :param request_message: The request_message to use for reply information. May be None.
        :type request_message: systemlink.messagebus.message_base.MessageBase or None
        :param body_dict: The body as a dictionary.
        :type body_dict: dict
        :return: A new instance of :class:`AssetPerformanceManagementQueryAssetsAvailabilityResponse`.
        :rtype: AssetPerformanceManagementQueryAssetsAvailabilityResponse
        """
        assets_with_availability_ = _deserialize(body_dict.get('assetsWithAvailability'), 'list(AssetWithAvailabilityModel)')
        query_error_ = _deserialize(body_dict.get('queryError'), 'ErrorModel')
        return cls(
            request_message,
            assets_with_availability_=assets_with_availability_,
            query_error_=query_error_
        )

    @classmethod
    def from_json(cls, request_message, body_json):
        """
        Create a new instance of :class:`AssetPerformanceManagementQueryAssetsAvailabilityResponse` using a JSON string.

        :param request_message: The request_message to use for reply information. May be None.
        :type request_message: systemlink.messagebus.message_base.MessageBase or None
        :param body_json: A string in JSON format representing the body.
        :type body_json: str
        :return: A new instance of :class:`AssetPerformanceManagementQueryAssetsAvailabilityResponse`.
        :rtype: AssetPerformanceManagementQueryAssetsAvailabilityResponse
        """
        body_dict = json.loads(body_json)
        return cls.from_dict(request_message, body_dict)

    @classmethod
    def from_body_bytes(cls, request_message, body_bytes):
        """
        Create a new instance of :class:`AssetPerformanceManagementQueryAssetsAvailabilityResponse` using a body
        of type :class:`bytes` or :class:`bytearray`,

        :param request_message: The request_message to use for reply information. May be None.
        :type request_message: systemlink.messagebus.message_base.MessageBase or None
        :param body_bytes: The body to use.
        :type body_bytes: bytes or bytearray
        :return: A new instance of :class:`AssetPerformanceManagementQueryAssetsAvailabilityResponse`.
        :rtype: AssetPerformanceManagementQueryAssetsAvailabilityResponse
        """
        body_json = str(body_bytes, 'utf-8')
        return cls.from_json(request_message, body_json)

    @classmethod
    def from_message(cls, message):
        """
        Create a new instance of :class`AssetPerformanceManagementQueryAssetsAvailabilityResponse` using a
        :class:`systemlink.messagebus.message_base.MessageBase` derived message.

        :param message: The message to use as the basis for this class instance.
        :type message: systemlink.messagebus.message_base.MessageBase
        :return: A new instance of :class`AssetPerformanceManagementQueryAssetsAvailabilityResponse`.
        :rtype: AssetPerformanceManagementQueryAssetsAvailabilityResponse
        """
        instance = cls.from_body_bytes(message, message.body_bytes)
        instance.correlation_id = message.correlation_id
        instance.reply_to = message.reply_to
        routing_key = MessageHeader.generate_routing_key(message.reply_to, cls.MESSAGE_NAME)
        instance.routing_key = routing_key
        return instance

    def to_dict(self):
        """
        Returns a dictionary representing the data in this object.

        :return: A dictionary representing the data in this object.
        :rtype: dict
        """
        assets_with_availability_ = _serialize(self.assets_with_availability)
        query_error_ = _serialize(self.query_error)
        return {
            'assetsWithAvailability': assets_with_availability_,
            'queryError': query_error_
        }

    def to_json(self):
        """
        Returns a JSON string representing the data in this object.

        :return: A JSON string representing the data in this object.
        :rtype: str
        """
        body_dict = self.to_dict()
        return json.dumps(body_dict, separators=(',', ':'))

    def to_body_bytes(self):
        """
        Returns a :class:`bytearray` body representing the data in this object.

        :return: A :class:`bytearray` body representing the data in this object.
        :rtype: bytearray
        """
        body_json = self.to_json()
        return bytearray(body_json, 'utf-8')

    def to_message(self, request_message=None):
        """
        Returns a :class:`systemlink.messagebus.message_base.MessageBase`
        object representing the data in this object.

        :param request_message: Request message if this is a response.
        :type request_message: systemlink.messagebus.message_base.MessageBase or None
        :return: A :class:`systemlink.messagebus.message_base.MessageBase`
            object representing the data in this object.
        :rtype: systemlink.messagebus.message_base.MessageBase
        """
        header = self.header
        if request_message:
            request_header = request_message.header
            header.correlation_id = request_header.correlation_id
            routing_key = MessageHeader.generate_routing_key(request_header.reply_to, self.MESSAGE_NAME)
            header.routing_key = routing_key
        body_bytes = self.to_body_bytes()
        return MessageBase(header, body_bytes)

    @property
    def body_bytes(self):
        """
        Returns a :class:`bytes` body representing the data in this object.

        :return: A :class:`bytes` body representing the data in this object.
        :rtype: bytes
        """
        self._body = self.to_body_bytes()  # pylint: disable=attribute-defined-outside-init
        return self._body
