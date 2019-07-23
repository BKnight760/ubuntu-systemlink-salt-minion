# -*- coding: utf-8 -*-
'''
National Instruments SystemLink Assets Module
'''
from __future__ import absolute_import, print_function, unicode_literals

# Import Python libs
import atexit
import fnmatch
try:
    from dateutil.parser import parse
    from dateutil.relativedelta import relativedelta
    HAS_DATEUTIL = True
except ImportError:
    HAS_DATEUTIL = False
import json
import logging
import os
import os.path
import sys

# Import salt libs
# pylint: disable=import-error,3rd-party-module-not-gated
try:
    import salt.ext.six.moves.winreg as winreg
except ImportError:
    pass  # We are on Linux, this is not an issue
import salt.utils.files
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
    from _apm_amqp_writer import AssetPerformanceManagmentAmqpWriter
    from _apm_amqp_writer import AssetPerformanceManagmentAmqpWriterException
    import _apm_constants as apm_constants
    import _apm_messages as apm_messages  # pylint: disable=import-error,3rd-party-local-module-not-gated
finally:
    # Remove the extra search path that we added to sys.path
    sys.path.remove(IMPORT_PATH)

__virtualname__ = 'nisysmgmt_assets'

# Set up logging
log = logging.getLogger(__name__)

ATEXIT_REGISTERED = False

# Version indicating the version of AssetPerformanceManagementMinionAssetsUpdatedBroadcast
MESSAGE_VERSION = 1

NI_INSTALLERS_REG_PATH = 'SOFTWARE\\National Instruments\\Common\\Installer'
NI_INSTALLERS_REG_KEY_APP_DATA = 'NIPUBAPPDATADIR'

USER_DEFINED_ENABLE_FILE_PATH = None
USER_DEFINED_DIRECTORY_PATH = None


def __virtual__():
    has_systemlink_sdk = AssetPerformanceManagmentAmqpWriter.has_systemlink_sdk()
    if not has_systemlink_sdk or not HAS_DATEUTIL:
        return False, 'This module requires NI Skyline Message Bus and the python-dateutil module for Python'

    return __virtualname__


def publish_user_defined_assets():  # pylint: disable=unused-argument
    '''
    Function used to retrieve user-specified assets and asset-related information
    from the Data\\Assets\\UserDefined directory on the minion.
    '''
    try:
        _register_atexit_if_not_registered()

        file_paths = _get_all_json_file_paths_recursively()
        feature_enabled = _is_user_defined_assets_feature_enabled()
        if not file_paths and not feature_enabled:
            # The Data\Assets\UserDefined directory does not exist or it is empty -> NoOp
            return apm_constants.PublishUserDefinedAssetsStatusCode.NO_JSON_FILES.value

        asset_bags = _read_all_assets_from_json_files(file_paths)
        assets = _parse_assets_from_bag(asset_bags)
        # Create a file on disk to make sure from this point on we send messages to the
        # server even if no JSON files exist under the UserDefined directory.
        _enable_user_defined_feature_if_not_enabled(feature_enabled)
        _publish_assets(assets)
    except AssetPerformanceManagmentAmqpWriterException as exc:
        if exc.is_warning:
            log.warning(exc.message)
        else:
            log.error(exc.message)
        return apm_constants.PublishUserDefinedAssetsStatusCode.AMQP_ERROR.value
    except Exception as exc:  # pylint: disable=broad-except
        log.error(
            'Unexpected exception in "nisysmgmt_assets module": %s',
            exc, exc_info=True
        )
        return apm_constants.PublishUserDefinedAssetsStatusCode.INTERNAL_ERROR.value

    return apm_constants.PublishUserDefinedAssetsStatusCode.SUCCESS.value


def _is_user_defined_assets_feature_enabled():  # pylint: disable=invalid-name
    '''
    Indicate whether the user defined assets feature is enabled by verifying
    if the .enable file exists on the expected app data directory.
    '''
    enable_file_path = _get_user_defined_enable_file_path()
    return os.path.isfile(enable_file_path)


def _get_user_defined_enable_file_path():  # pylint: disable=invalid-name
    '''
    Return the file path of the .enable file under the expected app data directory.
    '''
    global USER_DEFINED_ENABLE_FILE_PATH  # pylint: disable=global-statement

    if not USER_DEFINED_ENABLE_FILE_PATH:
        common_appdata_dir = _get_skyline_appdata_dir()
        USER_DEFINED_ENABLE_FILE_PATH = os.path.join(
            common_appdata_dir,
            apm_constants.DATA_DIRECTORY,
            apm_constants.ASSETS_DIRECTORY,
            apm_constants.USER_DEFINED_ENABLE_FILE
        )

    return USER_DEFINED_ENABLE_FILE_PATH


def _get_skyline_appdata_dir():
    '''
    Return the Skyline AppData directory based on the current platform.
    '''
    if salt.utils.platform.is_windows():
        return _get_windows_skyline_appdata_dir()
    return _get_linux_skyline_appdata_dir()


def _get_windows_skyline_appdata_dir():  # pylint: disable=invalid-name
    '''
    Return the Skyline AppData directory on Windows.

    This looks like: 'C:\\ProgramData\\National Instruments\\Skyline'
    '''
    with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            NI_INSTALLERS_REG_PATH,
            0,
            winreg.KEY_READ) as hkey:
        (appdata_dir, _) = winreg.QueryValueEx(
            hkey, NI_INSTALLERS_REG_KEY_APP_DATA)
        return os.path.join(
            appdata_dir,
            'Skyline'
        )


def _get_linux_skyline_appdata_dir():
    '''
    Return the Skyline AppData directory on Windows.

    This looks like: '/etc/natinst/niskyline'
    '''
    return '/etc/natinst/niskyline'


def _register_atexit_if_not_registered():  # pylint: disable=invalid-name
    '''
    Register cleanup functions
    '''
    global ATEXIT_REGISTERED  # pylint: disable=global-statement

    if not ATEXIT_REGISTERED:
        atexit.register(_cleanup_writer)
        ATEXIT_REGISTERED = True


def _cleanup_writer():
    '''
    Call the writer cleanup function
    '''
    AssetPerformanceManagmentAmqpWriter.cleanup()


def _get_all_json_file_paths_recursively():  # pylint: disable=invalid-name
    '''
    Looks at the Data\\Assets\\UserDefined directory from the National Instruments Common Data Directory,
    and identifies all JSON files, returning their absoulte paths.
    '''
    file_paths = []

    assets_dir = _get_user_defined_directory_path()
    for root, _, filenames in os.walk(assets_dir):
        for filename in fnmatch.filter(filenames, '*.json'):
            file_paths.append(os.path.join(root, filename))

    return file_paths


def _get_user_defined_directory_path():  # pylint: disable=invalid-name
    '''
    Return the directory path of the user defined directory under the expected app data directory.
    '''
    global USER_DEFINED_DIRECTORY_PATH  # pylint: disable=global-statement

    if not USER_DEFINED_DIRECTORY_PATH:
        common_appdata_dir = _get_skyline_appdata_dir()
        USER_DEFINED_DIRECTORY_PATH = os.path.join(
            common_appdata_dir,
            apm_constants.DATA_DIRECTORY,
            apm_constants.ASSETS_DIRECTORY,
            apm_constants.USER_DEFINED_DIRECTORY
        )

    return USER_DEFINED_DIRECTORY_PATH


def _read_all_assets_from_json_files(file_paths):  # pylint: disable=invalid-name
    '''
    Given a list of file paths to JSON files, extracts the contents of the assets list
    and merges them into a single list.
    '''
    assets = []

    for file_path in file_paths:
        try:
            file_content = None

            with salt.utils.files.fopen(file_path) as json_file:
                file_content = json.load(json_file)

            if file_content:
                file_assets = file_content['assets']
                if not _islist(file_assets):
                    continue
                assets.extend(file_assets)
        except (IOError, ValueError):
            log.warning(
                'JSON file %s could not be accessed or it was not a valid JSON. File will be skipped.',
                file_path
            )
        except KeyError:
            log.warning(
                'JSON file %s does not contain an assets list. File will be skipped.',
                file_path
            )

    return assets


def _islist(data):
    '''
    Check whether data is a list.
    '''
    return _isinstance(data, list, False)


def _isinstance(data, expected_type, inheritance_lookup=True):
    '''
    This is our own implementation of isinstance(), since in some cases
    we don't want to take inheritance into account when parsing data.

    For example: `isinstance(False, int)` returns True, but we want to make
    sure the user specifed the exact type we expect, which is int. Checking
    `type(False) is int` returns False.

    When you call this as you would call the Python isinstance() function,
    this will behave the same. The inheritance_lookup parameter is set
    by default to True, so it will use the isinstance() function.

    When you call this by specifying the inheritance_lookup parameter
    to False, this will check the data's exact type against the
    expected_type passed in.
    '''
    if inheritance_lookup:
        return isinstance(data, expected_type)

    return type(data) is expected_type  # pylint: disable=unidiomatic-typecheck


def _parse_assets_from_bag(asset_bags):
    '''
    Given a list of asset properties, builds an Asset object to be returned with the mesasge.
    '''
    message_assets = []

    for asset_bag in asset_bags:
        if not _isdict(asset_bag):
            continue
        properties = asset_bag.copy()
        message_asset = _create_asset_with_identification_properties(
            properties)
        if message_asset:
            _set_location_properties_on_asset(properties, message_asset)
            _set_self_calibration_properties_on_asset(
                properties, message_asset)
            _set_external_calibration_properties_on_asset(
                properties, message_asset)
            _set_handled_properties_on_asset(properties, message_asset)
            _set_unhandled_properties_on_asset(properties, message_asset)
            message_assets.append(message_asset)

    return message_assets


def _isdict(data):
    '''
    Check whether data is a dict.
    '''
    return _isinstance(data, dict, False)


def _create_asset_with_identification_properties(properties):  # pylint: disable=invalid-name
    '''
    Extracts and validates identification properties from the bag returning an Asset
    with the identification properties set.

    If any of the properties are not present in the bag or are invalid returns None.
    '''
    if not _is_asset_valid(properties):
        return None

    model_number = properties.pop(_camelcase(apm_constants.MODEL_NUMBER_KEY))
    vendor_number = properties.pop(_camelcase(apm_constants.VENDOR_NUMBER_KEY))
    if not _isint(model_number) or not _isint(vendor_number):
        return None

    # In the future, we might want to add some validation to verify this is indeed a string
    model_name = _to_str(properties.pop(
        _camelcase(apm_constants.MODEL_NAME_KEY)))
    serial_number = _to_str(properties.pop(
        _camelcase(apm_constants.SERIAL_NUMBER_KEY)))
    vendor_name = _to_str(properties.pop(
        _camelcase(apm_constants.VENDOR_NAME_KEY)))
    bus_type = _to_str(properties.pop(
        _camelcase(apm_constants.BUS_TYPE_KEY), apm_constants.BUS_TYPE_DEFAULT_VALUE))

    asset_identification = apm_messages.AssetIdentification(
        model_name,
        model_number,
        serial_number,
        vendor_name,
        vendor_number,
        bus_type
    )

    return apm_messages.AssetUpdateProperties(
        asset_identification,
        []
    )


def _is_asset_valid(properties):
    '''
    Checks that all identification properties exist in the bag.

    Identification properties include:
    - model name
    - model number
    - serial number
    - vendor name
    - vendor number
    - bus type
    '''
    id_keys_count = len(apm_constants.IDENTIFICATION_KEYS)
    asset_id_keys_count = 0

    for identification_property in apm_constants.IDENTIFICATION_KEYS:
        if _camelcase(identification_property) in properties or identification_property == apm_constants.BUS_TYPE_KEY:
            asset_id_keys_count += 1

    return asset_id_keys_count == id_keys_count


def _camelcase(value):
    '''
    Given a PascalCase value, it converts it to camelCase.
    '''
    return value[0].lower() + value[1:]


def _isint(data):
    '''
    Check whether data is an int.
    '''
    return _isinstance(data, int, False)


def _to_str(value):
    '''
    Converts any value or objects to its string representation.
    '''
    # For now we do a simple str() conversion, but in the future we might want to improve
    # it by using salt.utils.stringutils.to_str().
    return str(value)


def _set_location_properties_on_asset(properties, asset):  # pylint: disable=invalid-name
    '''
    Extracts the location property from the bag and inserts the location properties
    in the properties list of the asset.

    Properties include:
    - resource uri
    - slot number
    - parent
    '''
    location_properties = []

    location = properties.pop(_camelcase(apm_constants.LOCATION_KEY), None)
    if not _isdict(location):
        return

    _append_property_with_message_key_if_exists(
        location,
        location_properties,
        apm_constants.RESOURCE_URI_KEY,
        apm_constants.LOCATION_RESOURCE_URI_MESSAGE_KEY
    )

    _append_property_with_message_key_if_exists(
        location,
        location_properties,
        apm_constants.SLOT_NUMBER_KEY,
        apm_constants.LOCATION_SLOT_NUMBER_MESSAGE_KEY
    )

    _append_property_with_message_key_if_exists(
        location,
        location_properties,
        apm_constants.PARENT_KEY,
        apm_constants.LOCATION_PARENT_MESSAGE_KEY
    )

    asset.properties.extend(location_properties)


def _append_property_with_message_key_if_exists(properties, result_properties, property_key, property_message_key):  # pylint: disable=invalid-name
    '''
    Extracts the property with the given key from the bag and appends it to the result properties list
    with the message key.

    If the key does not exists this is a NoOp.
    '''
    property_value = properties.pop(_camelcase(property_key), None)
    if property_value:
        result_properties.append(
            apm_messages.Property(
                property_message_key,
                _to_str(property_value)
            )
        )


def _set_self_calibration_properties_on_asset(properties, asset):  # pylint: disable=invalid-name
    '''
    Extracts the self calibration property from the bag and inserts the calibration properties
    in the properties list of the asset.

    Properties include:
    - calibration date
    - limited
    - operator

    If the calibration date is invalid or if it does not exist this is a NoOp.
    '''
    self_calibration_properties = []

    self_calibration = properties.pop(
        _camelcase(apm_constants.SELF_CALIBRATION_KEY), None)
    if not _isdict(self_calibration):
        return

    date_str = self_calibration.pop(
        _camelcase(apm_constants.CALIBARTION_DATE_KEY), None)
    date = _parse_date(date_str)
    if not date:
        return

    self_calibration_properties.append(
        apm_messages.Property(
            apm_constants.SELF_CALIBRATION_DATE_MESSAGE_KEY,
            date.isoformat()
        )
    )

    limited = self_calibration.pop(
        _camelcase(apm_constants.IS_LIMITED_KEY), None)
    if _isbool(limited):
        self_calibration_properties.append(
            apm_messages.Property(
                apm_constants.SELF_CALIBRATION_IS_LIMITED_MESSAGE_KEY,
                limited
            )
        )

    _append_operator_properties_if_exists(
        self_calibration,
        self_calibration_properties,
        apm_constants.SELF_CALIBRATION_OPERATOR_DISPLAY_NAME_MESSAGE_KEY,
        apm_constants.SELF_CALIBRATION_OPERATOR_USER_ID_MESSAGE_KEY
    )

    asset.properties.extend(self_calibration_properties)


def _parse_date(date_str):
    '''
    Parses a date given as a string into a datetime.
    '''
    try:
        return parse(date_str)
    except Exception:  # pylint: disable=broad-except
        pass

    return None


def _isbool(data):
    '''
    Check whether data is a bool.
    '''
    return _isinstance(data, bool, False)


def _append_operator_properties_if_exists(properties, result_properties, display_name_message_key, user_id_message_key):  # pylint: disable=invalid-name
    '''
    Extracts the operator from the bag and appends the display name and user id properties
    to the result properties list with the message keys.

    If the operator does not exist this is a NoOp.
    '''
    operator_properties = []

    operator = properties.pop(_camelcase(apm_constants.OPERATOR_KEY), None)
    if not _isdict(operator):
        return

    _append_property_with_message_key_if_exists(
        operator,
        operator_properties,
        apm_constants.DISPLAY_NAME_KEY,
        display_name_message_key
    )

    _append_property_with_message_key_if_exists(
        operator,
        operator_properties,
        apm_constants.USER_ID_KEY,
        user_id_message_key
    )

    result_properties.extend(operator_properties)


def _set_external_calibration_properties_on_asset(properties, asset):  # pylint: disable=invalid-name
    '''
    Extracts the external calibration property from the bag and inserts the calibration properties
    in the properties list of the asset.

    Properties include:
    - calibration date
    - next recommended date
    - recommended interval
    - limited
    - comments
    - checksum
    - operator

    If either one of the calibration date, recommended interval or next recommended date
    are invalid or if they do not exist in the bag this is a NoOp.
    '''
    external_calibration_properties = []

    external_calibration = properties.pop(
        _camelcase(apm_constants.EXTERNAL_CALIBRATION_KEY), None)
    if not _isdict(external_calibration):
        return

    date_str = external_calibration.pop(
        _camelcase(apm_constants.CALIBARTION_DATE_KEY), None)
    date = _parse_date(date_str)
    interval = external_calibration.pop(
        _camelcase(apm_constants.RECOMMENDED_INTERVAL_KEY), None)
    if not date or not _is_interval_valid(interval):
        return

    next_date = date + relativedelta(months=+interval)

    external_calibration_properties.extend([
        apm_messages.Property(
            apm_constants.EXTERNAL_CALIBRATION_DATE_MESSAGE_KEY,
            date.isoformat()
        ),
        apm_messages.Property(
            apm_constants.EXTERNAL_CALIBRATION_RECOMMENDED_INTERVAL_MESSAGE_KEY,
            _to_str(interval)
        ),
        apm_messages.Property(
            apm_constants.EXTERNAL_CALIBRATION_NEXT_RECOMMENDED_DATE_MESSAGE_KEY,
            next_date.isoformat()
        )
    ])

    _append_property_with_message_key_if_exists(
        external_calibration,
        external_calibration_properties,
        apm_constants.COMMENTS_KEY,
        apm_constants.EXTERNAL_CALIBRATION_COMMENTS_MESSAGE_KEY
    )

    _append_property_with_message_key_if_exists(
        external_calibration,
        external_calibration_properties,
        apm_constants.CHECKSUM_KEY,
        apm_constants.EXTERNAL_CALIBRATION_CHECKSUM_MESSAGE_KEY
    )

    limited = external_calibration.pop(
        _camelcase(apm_constants.IS_LIMITED_KEY), None)
    if _isbool(limited):
        external_calibration_properties.append(
            apm_messages.Property(
                apm_constants.EXTERNAL_CALIBRATION_IS_LIMITED_MESSAGE_KEY,
                limited
            )
        )

    supports_limited = external_calibration.pop(
        _camelcase(apm_constants.SUPPORTS_LIMITED_KEY), None)
    if _isbool(supports_limited):
        external_calibration_properties.append(
            apm_messages.Property(
                apm_constants.EXTERNAL_CALIBRATION_SUPPORTS_LIMITED_MESSAGE_KEY,
                supports_limited
            )
        )

    supports_write = external_calibration.pop(
        _camelcase(apm_constants.SUPPORTS_WRITE_KEY), None)
    if _isbool(supports_write):
        external_calibration_properties.append(
            apm_messages.Property(
                apm_constants.EXTERNAL_CALIBRATION_SUPPORTS_WRITE_MESSAGE_KEY,
                supports_write
            )
        )

    _append_operator_properties_if_exists(
        external_calibration,
        external_calibration_properties,
        apm_constants.EXTERNAL_CALIBRATION_OPERATOR_DISPLAY_NAME_MESSAGE_KEY,
        apm_constants.EXTERNAL_CALIBRATION_OPERATOR_USER_ID_MESSAGE_KEY
    )

    asset.properties.extend(external_calibration_properties)


def _is_interval_valid(data):
    '''
    Check whether data is a valid calibration interval.
    '''
    return _isint(data) and int(data) > 0


def _set_handled_properties_on_asset(properties, asset):  # pylint: disable=invalid-name
    '''
    Extracts all handled properties from the bag (except for identification, asset class and self/external calibration)
    and inserts them in the properties list of the asset.
    '''
    handled_properties = []

    # These could technically be handled by the _set_unhandled_properties_on_asset,
    # but in the future we should be able to easily add some parsing validation to
    # these so that only string values are allowed, not nested JSON objects, which
    # is a valid case for all unhandled properties.
    _append_property_if_exists(
        properties,
        handled_properties,
        apm_constants.ASSET_CLASSS_KEY
    )
    _append_property_if_exists(
        properties,
        handled_properties,
        apm_constants.ASSET_NAME_KEY
    )
    _append_property_if_exists(
        properties,
        handled_properties,
        apm_constants.FIRMWARE_VERSION_KEY
    )
    _append_property_if_exists(
        properties,
        handled_properties,
        apm_constants.HARDWRE_VERSION_KEY
    )
    _append_property_if_exists(
        properties,
        handled_properties,
        apm_constants.VISA_RESOURCE_NAME_KEY
    )

    # This will only be a valid boolean if at least one of SupportsSelfCalibration
    # and SupportsExternalCalibration are valid booleans.
    supports_any_calibration = None

    supports_self_calibration = properties.pop(
        _camelcase(apm_constants.SUPPORTS_SELF_CALIBRATION_KEY), None)
    if _isbool(supports_self_calibration):
        supports_any_calibration = supports_self_calibration
        handled_properties.append(
            apm_messages.Property(
                apm_constants.SUPPORTS_SELF_CALIBRATION_KEY,
                supports_self_calibration
            )
        )

    supports_external_calibration = properties.pop(
        _camelcase(apm_constants.SUPPORTS_EXTERNAL_CALIBRATION_KEY), None)
    if _isbool(supports_external_calibration):
        supports_any_calibration = supports_any_calibration or supports_external_calibration
        handled_properties.append(
            apm_messages.Property(
                apm_constants.SUPPORTS_EXTERNAL_CALIBRATION_KEY,
                supports_external_calibration
            )
        )

    if _isbool(supports_any_calibration):
        handled_properties.append(
            apm_messages.Property(
                apm_constants.SUPPORTS_ANY_CALIBRATION_MESSAGE_KEY,
                supports_any_calibration
            )
        )

    if handled_properties:
        asset.properties.extend(handled_properties)


def _append_property_if_exists(properties, result_properties, property_key):
    '''
    Extracts the property with the given key from the bag and appends it to the result properties list
    with the same key.

    If the key does not exists this is a NoOp.
    '''
    _append_property_with_message_key_if_exists(
        properties,
        result_properties,
        property_key,
        property_key
    )


def _set_unhandled_properties_on_asset(properties, asset):  # pylint: disable=invalid-name
    '''
    Takes all properties from the bag and inserts them in the properties list of the asset.
    '''
    unhandled_properties = []

    _remove_reserved_properties(properties)

    for property_key in properties:
        # This can't be a pop(), because it will raise a `dictionary changed size during iteration` exception
        property_value = properties.get(property_key, None)
        unhandled_properties.append(apm_messages.Property(
            _pascalcase(property_key), _to_str(property_value)))

    asset.properties.extend(unhandled_properties)


def _remove_reserved_properties(properties):
    '''
    Goes through the reserved keys and removes them from the bag.
    '''
    for property_key in apm_constants.RESERVED_KEYS:
        properties.pop(_camelcase(property_key), None)


def _pascalcase(value):
    '''
    Given a camelCase value, it converts it to PascalCase.
    '''
    return value[0].upper() + value[1:]


def _enable_user_defined_feature_if_not_enabled(feature_enabled):  # pylint: disable=invalid-name
    '''
    Enable the user defined assets feature by writing the .enable file on the expected app data directory.
    '''
    if feature_enabled:
        return

    enable_file_path = _get_user_defined_enable_file_path()
    with salt.utils.files.fopen(enable_file_path, 'w'):
        pass


def _publish_assets(assets):
    '''
    Call the writer to publish the AssetPerformanceManagementMinionAssetsUpdatedBroadcast over AMQP
    '''
    minion_id = __grains__['id']

    broadcast = apm_messages.AssetPerformanceManagementMinionAssetsUpdatedBroadcast(
        MESSAGE_VERSION,
        minion_id,
        assets
    )

    writer = AssetPerformanceManagmentAmqpWriter()
    writer.publish_minion_assets_updated_broadcast(broadcast)
