# -*- coding: utf-8 -*-

'''
Named mutex handling.
'''

# Windows implementation based on:
# http://code.activestate.com/recipes/577794-win32-named-mutex-class-for-system-wide-mutex/

from __future__ import absolute_import
import sys


def is_windows():
    '''
    Return True if the system platform is Windows. Return False otherwise.
    '''
    return sys.platform.startswith('win')


if is_windows():
    import win32api  # pylint: disable=3rd-party-local-module-not-gated
    import win32event  # pylint: disable=3rd-party-local-module-not-gated
    import win32security  # pylint: disable=3rd-party-local-module-not-gated
else:
    # Not Windows
    import errno
    import fcntl  # pylint: disable=import-error,3rd-party-local-module-not-gated
    import os.path
    import signal
    from contextlib import contextmanager

    @contextmanager
    def _timeout_context(seconds):
        '''
        A context manager to enforce timeout conditions.
        Will throw an IOError with its 'errno' attribute set to
        'errno.EINTR' on a timeout condition.
        '''
        def _timeout_handler(signum, frame):  # pylint: disable=unused-argument
            '''
            Signal handler for the '_timeout_context' context manager.
            '''
            pass

        original_handler = signal.signal(signal.SIGALRM, _timeout_handler)  # pylint: disable=no-member

        try:
            signal.alarm(seconds)  # pylint: disable=no-member
            yield
        finally:
            signal.alarm(0)  # pylint: disable=no-member
            signal.signal(signal.SIGALRM, original_handler)  # pylint: disable=no-member


class NamedMutexTimeoutException(Exception):
    '''
    Class for named mutex timeout exceptions
    '''
    pass


class NamedMutex(object):
    '''
    A named, system-wide mutex that can be acquired and released.
    '''
    def __init__(self, name, acquired=False, timeout=None):
        '''
        Create named mutex with given name, also acquiring mutex if acquired
        is True. Mutex names are case sensitive, and a filename (with
        slashes or backslashes in it) is not a valid mutex name. On an acquire
        timeout condition, will raise NamedMutexTimeoutException. Raises
        IOError on other errors.
        '''
        self.name = name
        self.acquired = False
        self.handle = None  # In case an exception is thrown below

        if is_windows():
            if '\\' not in name:
                name = 'Global\\' + name
            attr = win32security.SECURITY_ATTRIBUTES()  # pylint: disable=no-member
            attr.bInheritHandle = False
            desc = win32security.SECURITY_DESCRIPTOR()  # pylint: disable=no-member
            desc.SetSecurityDescriptorDacl(1, None, 0)
            attr.SECURITY_DESCRIPTOR = desc
            ret = win32event.CreateMutex(attr, False, name)  # pylint: disable=no-member
            if not ret:
                raise IOError(
                    'Failed to created named mutex "{0}". Error code: {1}'.format(
                        self.name, win32api.GetLastError()  # pylint: disable=no-member
                    )
                )
            self.handle = ret
        else:
            filename = name + '.lock'
            filename = os.path.join('/var/lock', filename)
            self.handle = open(filename, 'w')  # pylint: disable=resource-leakage

        if acquired:
            # self.acquire() will set 'self.acquired'
            self.acquire(timeout=timeout)

    def acquire(self, timeout=None):
        '''
        Acquire ownership of the mutex. If a
        timeout is specified, it will wait a maximum of timeout seconds to
        acquire the mutex. On an acquire timeout condition, will raise
        NamedMutexTimeoutException. Raises IOError on other errors.
        '''
        if is_windows():
            if timeout is None:
                # Wait forever (INFINITE)
                win_timeout = 0xFFFFFFFF
            else:
                win_timeout = int(round(timeout * 1000))
            ret = win32event.WaitForSingleObject(self.handle, win_timeout)  # pylint: disable=no-member
            if ret in (0, 0x80):
                # Note that this doesn't distinguish between normally acquired (0)
                # and acquired due to another owning process terminating without
                # releasing (0x80)
                pass
            elif ret == 0x102:
                # Timeout
                raise NamedMutexTimeoutException(
                    'Failed to acquire named mutex "{0}" due to timeout'.format(self.name)
                )
            else:
                # Acquire failed
                raise IOError(
                    'Failed to acquire named mutex "{0}". Error code: {1}'.format(
                        self.name, win32api.GetLastError()  # pylint: disable=no-member
                    )
                )
        else:
            if timeout is None:
                # Wait forever (INFINITE)
                fcntl.flock(self.handle, fcntl.LOCK_EX)
            elif timeout == 0:
                try:
                    fcntl.flock(self.handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except IOError as exc:
                    if exc.errno == errno.EWOULDBLOCK:
                        raise NamedMutexTimeoutException(
                            'Failed to acquire named mutex "{0}" due to timeout'.format(self.name)
                        )
                    else:
                        raise
            else:
                with _timeout_context(timeout):
                    try:
                        fcntl.flock(self.handle, fcntl.LOCK_EX)
                    except IOError as exc:
                        if exc.errno == errno.EINTR:
                            raise NamedMutexTimeoutException(
                                'Failed to acquire named mutex "{0}" due to timeout'.format(self.name)
                            )
                        else:
                            raise
        self.acquired = True

    def release(self):
        '''
        Release an acquired mutex. Raises IOError on error.
        '''
        if is_windows():
            win32event.ReleaseMutex(self.handle)  # pylint: disable=no-member
        else:
            fcntl.flock(self.handle, fcntl.LOCK_UN)
        self.acquired = False

    def close(self):
        '''
        Close the mutex and release the handle.
        '''
        if self.handle is None:
            # Already closed
            return
        if is_windows():
            win32api.CloseHandle(self.handle)  # pylint: disable=no-member
        else:
            self.handle.close()
        self.handle = None

    __del__ = close

    def __repr__(self):
        '''
        Return the Python representation of this mutex.
        '''
        return '{0}({1!r}, acquired={2})'.format(  # pylint: disable=repr-flag-used-in-string
            self.__class__.__name__, self.name, self.acquired
        )

    __str__ = __repr__

    # Make it a context manager so it can be used with the "with" statement
    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
