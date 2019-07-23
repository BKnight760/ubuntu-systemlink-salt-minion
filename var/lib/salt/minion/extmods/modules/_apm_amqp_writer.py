# -*- coding: utf-8 -*-
'''
Contains the AMQP writer used to communicate with the Asset Performance Management service
'''
from __future__ import absolute_import, print_function, unicode_literals

# Import Python libs
import os
import os.path

# Import local libs
# pylint: disable=import-error,3rd-party-module-not-gated
try:
    import systemlink.messagebus.paths as paths
    from systemlink.messagebus.amqp_connection_manager import AmqpConnectionManager
    from systemlink.messagebus.amqp_configuration_manager import AmqpConfigurationManager
    from systemlink.messagebus.amqp_configuration import SKYLINE_MASTER_CONFIGURATION_ID
    from systemlink.messagebus.exceptions import SystemLinkException
    from systemlink.messagebus.message_service import MessageService
    from systemlink.messagebus.message_service_builder import MessageServiceBuilder
    HAS_SYSTEMLINK_SDK = True
except ImportError:
    HAS_SYSTEMLINK_SDK = False


class AssetPerformanceManagmentAmqpWriterException(Exception):
    '''
    Exception raised by the AssetPerformanceManagmentAmqpWriter class
    '''

    def __init__(self, message, inner_exception=None, is_warning=None):
        msg = None

        if inner_exception:
            msg = '{0}: {1}'.format(message, inner_exception)
        else:
            msg = message

        super(
            AssetPerformanceManagmentAmqpWriterException,
            self
        ).__init__(msg)

        self.is_warning = is_warning is True


class AssetPerformanceManagmentAmqpWriter(object):  # pylint: disable=too-few-public-methods
    '''
    Abstraction over AMQP connection which facilitates communication
    between the minion and the AssetPerformanceManagement service.
    '''
    __instance = None

    @staticmethod
    def has_systemlink_sdk():
        '''
        Check if the module sucessfully loaded NI Skyline Message Bus
        '''
        return HAS_SYSTEMLINK_SDK

    def __new__(cls):
        '''
        Handle instantiation so that only a single instance of this class is created
        '''
        if not AssetPerformanceManagmentAmqpWriter.has_systemlink_sdk():
            raise AssetPerformanceManagmentAmqpWriterException(
                'Import of NI Skyline Message Bus failed.'
            )

        if AssetPerformanceManagmentAmqpWriter.__instance is None:
            AssetPerformanceManagmentAmqpWriter.__instance = object.__new__(
                cls
            )
            # pylint: disable=protected-access
            AssetPerformanceManagmentAmqpWriter.__instance._initialized = False
            AssetPerformanceManagmentAmqpWriter.__instance._connection_manager = None
            AssetPerformanceManagmentAmqpWriter.__instance._message_service = None
            # pylint: enable=protected-access
        return AssetPerformanceManagmentAmqpWriter.__instance

    def __init__(self):
        '''
        Initialize the message service if not already initialized
        '''
        if not self._initialized:
            try:
                self._initialize_message_service()
            except SystemLinkException as exc:
                self._close_message_service()
                if exc.error.name == 'Skyline.AMQPErrorFailedToLogIn':
                    # The salt-master may have changed credentials after the salt-minion
                    # connects to the salt-master through Salt.
                    raise AssetPerformanceManagmentAmqpWriterException(
                        'AMQP Authentication error. Credentials may have changed',
                        exc,
                        is_warning=True
                    )
                else:
                    # All other AMQP exceptions
                    raise AssetPerformanceManagmentAmqpWriterException(
                        'An AMQP error has occurred',
                        exc
                    )

    def _initialize_message_service(self):
        '''
        Initialize the message service

        :return: ``True`` if initialized successfully, ``False`` otherwise.
        :rtype: bool
        '''
        file_path = paths.get_skyline_master_file()
        if not os.path.isfile(file_path):
            # The Skyline Master file is not available.
            # Can't set up the Message Service without it.
            return

        self._setup_amqp_connection()

        self._initialized = True

    def _setup_amqp_connection(self):
        '''
        Open the AMQP connection and instantiate the message service
        '''
        master_config = AmqpConfigurationManager.get_configuration(
            id_=SKYLINE_MASTER_CONFIGURATION_ID,
            enable_fallbacks=False
        )
        service_name = 'AssetPerformanceManagementSaltService'
        connection_timeout = 50

        self._connection_manager = AmqpConnectionManager(config=master_config)
        self._connection_manager.connection_timeout = connection_timeout
        self._connection_manager.auto_reconnect = False
        message_service_builder = MessageServiceBuilder(service_name)
        message_service_builder.connection_manager = self._connection_manager

        self._message_service = MessageService(message_service_builder)

    def _close_message_service(self):
        '''
        Close the AMQP connection and the message service
        '''
        if self._message_service:
            self._message_service.close()
            self._message_service = None
        if self._connection_manager:
            self._connection_manager.close()
            self._connection_manager = None

        self._initialized = False

    @classmethod
    def cleanup(cls):
        '''
        Clean up the writer by closing the connection
        '''
        # This makes sure that if the salt-minion closes before the writer has been initialized
        # we don't create it just to clean it up.
        if cls.__instance is not None:
            cls.__instance._close_message_service()  # pylint: disable=protected-access
            cls.__instance = None

    def publish_minion_assets_updated_broadcast(self, broadcast):  # pylint: disable=invalid-name
        '''
        Publish an AssetPerformanceManagementMinionAssetsUpdatedBroadcast over AMQP
        '''
        try:
            self._message_service.publish_broadcast(broadcast)
        except SystemLinkException as exc:
            raise AssetPerformanceManagmentAmqpWriterException(
                'An AMQP error has occurred',
                exc
            )
