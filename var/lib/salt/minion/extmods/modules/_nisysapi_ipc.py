# -*- coding: utf-8 -*-
'''
IPC transport classes
'''

# Import Python libs
from __future__ import absolute_import
import json
import logging
import os.path
import socket
import struct
import subprocess
import time
import weakref

# Import Tornado libs
import tornado
import tornado.gen
import tornado.concurrent
import tornado.ioloop

# Import salt libs
# pylint: disable=import-error,3rd-party-module-not-gated
from salt.ext import six
# pylint: enable=import-error,3rd-party-module-not-gated

# Import local libs
# pylint: disable=import-error,3rd-party-module-not-gated
import _nisysmgmt_mutex
import _nisysmgmt_utils
# pylint: enable=import-error,3rd-party-module-not-gated

if _nisysmgmt_utils.is_windows():
    # pylint: disable=import-error,3rd-party-local-module-not-gated
    import wmi
    import salt.utils.winapi  # pylint: disable=ungrouped-imports
    # pylint: enable=import-error,3rd-party-local-module-not-gated

    MINIONAGENT_SERVICE_NAME = 'niminionagent'
elif _nisysmgmt_utils.is_linux():
    MINIONAGENT_DAEMON_PATH = '/etc/init.d/niminionagent'

log = logging.getLogger(__name__)

# Used status codes
NISMS_STATUS_OPERATION_TIMED_OUT = -2147220448
NISMS_STATUS_SERVICE_NOT_FOUND = -2147220557
NISMS_STATUS_SERVICE_NOT_FOUND_WARNING = 2147220557

MUTEX_NAME = 'salt.modules.nisysapi'

WMI_FAILURE_LOGGED = False


class SMSIPCClient(object):
    '''
    A Tornado IPC client very similar to Tornado's TCPClient class
    but using either UNIX domain sockets or TCP sockets

    This was written because Tornado does not have its own IPC
    server/client implementation.

    :param IOLoop io_loop: A Tornado ioloop to handle scheduling
    :param str/int socket_path: A path on the filesystem where a socket
                                belonging to a running IPCServer can be
                                found.
                                It may also be of type 'int', in which
                                case it is used as the port for a tcp
                                localhost connection.
    '''

    # Create singleton map between two sockets
    instance_map = weakref.WeakKeyDictionary()

    def __new__(cls, socket_path, io_loop=None):
        io_loop = io_loop or tornado.ioloop.IOLoop.current()
        if io_loop not in SMSIPCClient.instance_map:
            SMSIPCClient.instance_map[io_loop] = weakref.WeakValueDictionary()
        loop_instance_map = SMSIPCClient.instance_map[io_loop]

        key = str(socket_path)

        if key not in loop_instance_map:
            log.debug('Initializing new SMSIPCClient for path: %s', key)
            new_client = object.__new__(cls)

            new_client.__singleton_init__(
                io_loop=io_loop, socket_path=socket_path
            )
            loop_instance_map[key] = new_client
        else:
            log.debug('Re-using SMSIPCClient for %s', key)
        return loop_instance_map[key]

    def __singleton_init__(self, socket_path, io_loop=None):
        '''
        Create a new IPC client

        IPC clients cannot bind to ports, but must connect to
        existing IPC servers. Clients can then send messages
        to the server.

        '''
        self.io_loop = io_loop or tornado.ioloop.IOLoop.current()
        self.socket_path = socket_path
        self._closing = False
        self.stream = None

    def __init__(self, socket_path, io_loop=None):
        # Handled by singleton __new__
        pass

    def connected(self):
        '''
        Return True if connected to the IPC socket
        '''
        return self.stream is not None and not self.stream.closed()

    def connect(self, callback=None, timeout=None):
        '''
        Connect to the IPC socket
        '''
        if (hasattr(self, '_connecting_future') and
                not self._connecting_future.done()):  # pylint: disable=E0203
            future = self._connecting_future  # pylint: disable=E0203
        else:
            future = tornado.concurrent.Future()
            self._connecting_future = future  # pylint: disable=attribute-defined-outside-init
            self.io_loop.add_callback(self._connect, timeout=timeout)

        if callback is not None:
            def _handle_future(future):
                '''
                Internal function that will add a callback to the IO Loop
                when the future completes. The callback will be invoked with
                the future's result.
                '''
                response = future.result()
                self.io_loop.add_callback(callback, response)
            future.add_done_callback(_handle_future)
        return future

    @tornado.gen.coroutine
    def _connect(self, timeout=None):
        '''
        Connect to a running IPCServer
        '''
        if isinstance(self.socket_path, int):
            sock_type = socket.AF_INET
            sock_addr = ('127.0.0.1', self.socket_path)
        else:
            sock_type = socket.AF_UNIX  # pylint: disable=no-member
            sock_addr = self.socket_path

        self.stream = None  # pylint: disable=attribute-defined-outside-init
        if timeout is not None:
            timeout_at = time.time() + timeout

        while True:
            if self._closing:
                break

            if self.stream is None:
                self.stream = tornado.iostream.IOStream(  # pylint: disable=attribute-defined-outside-init
                    socket.socket(sock_type, socket.SOCK_STREAM),
                    io_loop=self.io_loop,
                )

            try:
                # 'trace' is added in salt/log/mixins.py: 'LoggingTraceMixIn'
                log.trace('SMSIPCClient: Connecting to socket: %s', self.socket_path)  # pylint: disable=no-member
                yield self.stream.connect(sock_addr)
                self._connecting_future.set_result(True)
                break
            except Exception as exc:  # pylint: disable=broad-except
                if self.stream.closed():
                    self.stream = None  # pylint: disable=attribute-defined-outside-init

                if timeout is None or time.time() > timeout_at:
                    if self.stream is not None:
                        self.stream.close()
                        self.stream = None  # pylint: disable=attribute-defined-outside-init
                    self._connecting_future.set_exception(exc)
                    break

                yield tornado.gen.sleep(1)

    def __del__(self):
        self.close()

    def close(self):
        '''
        Routines to handle any cleanup before the instance shuts down.
        Sockets and filehandles should be closed explicitly, to prevent
        leaks.
        '''
        if self._closing:
            return
        self._closing = True  # pylint: disable=attribute-defined-outside-init
        if self.stream is not None and not self.stream.closed():
            self.stream.close()

    @tornado.gen.coroutine
    def query(self, request):
        '''
        Send a message to an IPC socket and receive a response.
        If the socket is not currently connected, a connection will be
        established.

        :param dict request: The message to be sent
        '''
        if not self.connected():
            yield self.connect()

        json_data = json.dumps(request, separators=(',', ':'))
        if six.PY2:
            pack = struct.pack('i', len(json_data)) + json_data
        else:
            pack = struct.pack('i', len(json_data)) + bytes(json_data, 'utf-8')
        yield self.stream.write(pack)
        response_len_data = yield self.stream.read_bytes(4)
        response_len = struct.unpack('i', response_len_data)[0]
        response_data = yield self.stream.read_bytes(response_len)
        if six.PY2:
            response = json.loads(response_data)
        else:
            response = json.loads(response_data.decode('utf-8'))
        raise tornado.gen.Return(response)


def niminionagent_enabled():
    '''
    Return True if the National Instruments Minion Agent is running.
    False otherwise.
    '''
    if _nisysmgmt_utils.is_windows():
        try:
            with salt.utils.winapi.Com():
                wmi_c = wmi.WMI()
                matched_services = wmi_c.Win32_Service(name=MINIONAGENT_SERVICE_NAME)
                if not matched_services:
                    return False
                return matched_services[0].State == 'Running'
        except Exception as exc:  # pylint: disable=broad-except
            global WMI_FAILURE_LOGGED  # pylint: disable=global-statement
            if not WMI_FAILURE_LOGGED:
                WMI_FAILURE_LOGGED = True
                log.error(
                    'Exception occurred when using WMI Win32_Service: %s',
                    exc, exc_info=True
                )
            # On WMI Error, treat as if the Minion Agent is not running.
            return False
    elif _nisysmgmt_utils.is_linux():
        if not os.path.isfile(MINIONAGENT_DAEMON_PATH):
            return False
        retcode = subprocess.call([MINIONAGENT_DAEMON_PATH, 'status'])
        return retcode == 0
    else:
        return False


def query_minionagent(request, service_optional, connect_timeout=5):
    '''
    Send a job request to the NI Minion Agent
    and receive a response with the job return info.
    '''
    if not niminionagent_enabled():
        if service_optional:
            return {'status_code': NISMS_STATUS_SERVICE_NOT_FOUND_WARNING}
        return {'status_code': NISMS_STATUS_SERVICE_NOT_FOUND}

    mutex = _nisysmgmt_mutex.NamedMutex(MUTEX_NAME)
    with mutex:
        io_loop = tornado.ioloop.IOLoop()
        client = None
        try:
            uri = 7890
            client = SMSIPCClient(uri, io_loop=io_loop)
            try:
                io_loop.run_sync(
                    lambda: client.connect(timeout=connect_timeout))
            except Exception:  # pylint: disable=broad-except
                log.error('Connection failed to: %s', uri)
                return {'status_code': NISMS_STATUS_SERVICE_NOT_FOUND}

            try:
                log.info('About to send request to: %s', uri)
                response = io_loop.run_sync(
                    lambda: client.query(request))
            except Exception as exc:  # pylint: disable=broad-except
                log.error('Request to: %s failed. Exception = %s', uri, exc)
                return {'status_code': NISMS_STATUS_OPERATION_TIMED_OUT}
        finally:
            if client is not None:
                client.close()
            io_loop.close()

    log.info('Response received!')
    return response
