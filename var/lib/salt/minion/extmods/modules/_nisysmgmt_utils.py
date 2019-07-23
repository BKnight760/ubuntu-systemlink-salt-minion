#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Utility functions for use by NI Systems Management
related Salt modules and Python scripts.
'''
from __future__ import absolute_import

# Import python libs
import argparse  # pylint: disable=minimum-python-version
import os
import os.path
import subprocess
import sys
import time
import yaml

# Import local libs
import _nisysmgmt_config  # pylint: disable=import-error,3rd-party-module-not-gated
import _nisysmgmt_mutex  # pylint: disable=import-error,3rd-party-module-not-gated


MUTEX_NAME = 'salt.modules.nisysmgmt'
DEFAULT_HEALTH_MONITORING_ENABLED = True
DEFAULT_HEALTH_MONITORING_INTERVAL = 300
DEFAULT_HEALTH_MONITORING_RETENTION_TYPE = 'duration'
DEFAULT_HEALTH_MONITORING_RETENTION_DURATION_DAYS = 30
DEFAULT_HEALTH_MONITORING_RETENTION_MAX_HISTORY_COUNT = 10000
HEALTH_MONITORING_RETENTION_TYPES = [
    'none',
    'duration',
    'count',
    'permanent'
]

NIPKG_REG_PATH = 'SOFTWARE\\National Instruments\\NI Package Manager\\CurrentVersion'
NIPKG_REG_VALUE_PATH = 'Path'
NIPKG_REG_VALUE_EXE_FULL_PATH = 'CLIExecutableFullPath'
NIPKG_BIN = None
NIPKG_UPDATER_BIN = None

NISMS_UTILS_HELPER_FILE = '_nisysmgmt_utils.py'


def is_windows():
    '''
    Return True if the system platform is Windows. Return False otherwise.
    '''
    return sys.platform.startswith('win')


def is_linux():
    '''
    Return True if the system platform is Linux. Return False otherwise.
    '''
    return sys.platform.startswith('linux')


def get_ni_package_directories(winreg):
    '''
    Return the path for nipkg.exe and nipgk updater
    '''
    with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            NIPKG_REG_PATH,
            0,
            winreg.KEY_READ) as hkey:
        (exe_dir, _) = winreg.QueryValueEx(hkey, NIPKG_REG_VALUE_PATH)
        (exe_path, _) = winreg.QueryValueEx(hkey, NIPKG_REG_VALUE_EXE_FULL_PATH)
        updater_path = os.path.join(exe_dir, 'Updater', 'Install.exe')
        if os.path.isfile(exe_path) and os.path.isfile(updater_path):
            return exe_path, updater_path


if is_windows():
    # pylint: disable=import-error,3rd-party-local-module-not-gated,wrong-import-position
    import winreg
    import win32con
    import win32file
    import pywintypes
    from win32com.shell import shellcon, shell  # pylint: disable=no-name-in-module
    # pylint: enable=import-error,3rd-party-local-module-not-gated,wrong-import-position

    NI_INSTALLERS_REG_PATH = 'SOFTWARE\\National Instruments\\Common\\Installer'
    NI_INSTALLERS_REG_KEY_APP_DATA = 'NIPUBAPPDATADIR'
else:
    # Non-Windows platforms are typically POSIX compliant.
    import fcntl  # pylint: disable=import-error,3rd-party-local-module-not-gated,wrong-import-position


class FileLockException(Exception):
    '''
    Class for file locking exceptions
    '''
    # Error codes:
    LOCK_FAILED = 1


class FileLock(object):
    '''
    Class that implements file-based locking
    '''
    def __init__(self, filename):
        self.filename = filename
        # This will create it if it does not exist already
        self.handle = open(filename, 'w')  # pylint: disable=resource-leakage
        if is_windows():
            self.hfile = win32file._get_osfhandle(self.handle.fileno())  # pylint: disable=no-member,protected-access
            self.overlapped = pywintypes.OVERLAPPED()  # pylint: disable=no-member

    def acquire(self):
        '''
        Acquire the file-based lock.
        Will raise a FileLockException if the lock cannot be acquired.
        '''
        if is_windows():
            try:
                win32file.LockFileEx(  # pylint: disable=no-member
                    self.hfile,
                    win32con.LOCKFILE_EXCLUSIVE_LOCK,
                    0,
                    -0x10000,
                    self.overlapped
                )
            except pywintypes.error as exc_value:  # pylint: disable=no-member
                # error: (33, 'LockFileEx',
                #         'The process cannot access the file because another
                #          process has locked a portion of the file.')
                if exc_value[0] == 33:
                    raise FileLockException(
                        FileLockException.LOCK_FAILED,
                        exc_value[2]
                    )
                else:
                    raise
        else:
            try:
                fcntl.flock(self.handle, fcntl.LOCK_EX)
            except IOError as exc_value:
                #  IOError: [Errno 11] Resource temporarily unavailable
                if exc_value[0] == 11:
                    raise FileLockException(
                        FileLockException.LOCK_FAILED,
                        exc_value[1]
                    )
                else:
                    raise

    def release(self):
        '''
        Release the file-based lock.
        The lock must already be previously acquired via acquire().
        '''
        if is_windows():
            try:
                win32file.UnlockFileEx(  # pylint: disable=no-member
                    self.hfile, 0, -0x10000, self.overlapped
                )
            except pywintypes.error as exc_value:  # pylint: disable=no-member
                if exc_value[0] == 158:
                    # error: (158, 'UnlockFileEx',
                    #         'The segment is already unlocked.')
                    # To match the 'posix' implementation, silently ignore
                    # this error
                    pass
                else:
                    raise
        else:
            fcntl.flock(self.handle, fcntl.LOCK_UN)

    def __del__(self):
        self.handle.close()

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()


def get_computer_desc_grains(salt_module_funcs):
    '''
    Return the computer description
    '''
    computer_desc = salt_module_funcs['system.get_computer_desc']()
    if sys.version_info[0] == 2:
        if not isinstance(computer_desc, basestring):
            computer_desc = ''
    elif not isinstance(computer_desc, str):
        computer_desc = ''
    grains = {
        'computer_desc': computer_desc
    }
    return grains


def get_lock_file_path(filename=None):
    '''
    Return path for concurrency control lock file.
    eg: '/var/lock/nisysmgmt_register_minion.py.lock'
    '''
    if is_windows():
        # Use the Windows services temp directory which is typically:
        # 'C:\Windows\Temp'
        lock_file = shell.SHGetFolderPath(0, shellcon.CSIDL_WINDOWS, 0, 0)
        lock_file = os.path.join(lock_file, 'Temp')
    elif is_linux():
        lock_file = '/var/lock'
    else:
        raise RuntimeError('Unsupported platform')
    if not filename:
        filename = '{0}.lock'.format(os.path.basename(__file__))
    lock_file = os.path.join(lock_file, filename)
    return lock_file


if is_windows():
    def get_ni_common_appdata_dir():
        '''
        Return the National Instruments Common Application Data Directory.
        This looks like: 'C:\\ProgramData\\National Instruments'

        :return: The National Instruments Common Application Data Directory.
        :rtype: str
        '''
        with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                NI_INSTALLERS_REG_PATH,
                0,
                winreg.KEY_READ) as hkey:
            (appdata_dir, _) = winreg.QueryValueEx(hkey, NI_INSTALLERS_REG_KEY_APP_DATA)
            return appdata_dir


def get_nisms_utils_helper_abs_path():  # pylint: disable=invalid-name
    '''
    Return the absolute path to the nisms helper module
    '''
    dir_path = os.path.dirname(os.path.abspath(__file__))
    if os.path.basename(dir_path) == '__pycache__':
        dir_path = os.path.dirname(dir_path)
    return os.path.join(dir_path, NISMS_UTILS_HELPER_FILE)


def get_salt_config_dir():
    '''
    Return Salt configuration directory.
    eg: '/etc/salt'
    '''
    if is_windows():
        config_dir = get_ni_common_appdata_dir()
        config_dir = os.path.join(
            config_dir, 'salt', 'conf'
        )
        return config_dir
    elif is_linux():
        return '/etc/salt'
    else:
        raise RuntimeError('Unsupported platform')


def get_salt_minion_config_subdir():
    '''
    Return Salt Minion configuration subdirectory.
    eg: '/etc/salt/minion.d'
    '''
    config_dir = get_salt_config_dir()
    config_dir = os.path.join(config_dir, 'minion.d')
    return config_dir


def get_salt_minion_master_config_file():  # pylint: disable=invalid-name
    '''
    Return Salt Minion's configuration file that specifies which master to use.
    eg: '/etc/salt/minion.d/master.conf'
    '''
    config_file = get_salt_minion_config_subdir()
    config_file = os.path.join(config_file, 'master.conf')
    return config_file


def get_salt_pki_dir():
    '''
    Return Salt Public Key Infrastructure (PKI) directory.
    eg: '/etc/salt/pki'
    '''
    pki_dir = get_salt_config_dir()
    pki_dir = os.path.join(pki_dir, 'pki')
    return pki_dir


def get_salt_pki_minion_subdir():
    '''
    Return Salt PKI Minion-specific subdirectory.
    eg: '/etc/salt/pki/minion'
    '''
    pki_dir = get_salt_pki_dir()
    pki_dir = os.path.join(pki_dir, 'minion')
    return pki_dir


def get_salt_pki_minion_master_pubkey_file():  # pylint: disable=invalid-name
    '''
    Return Salt PKI public key file that is generated by the salt-master.
    eg: '/etc/salt/pki/minion/minion_master.pub'
    '''
    pki_file = get_salt_pki_minion_subdir()
    pki_file = os.path.join(pki_file, 'minion_master.pub')
    return pki_file


def get_skyline_master_file():
    '''
    Return path to the Skyline Master AMQP credentials file on the minion.

    @return: Path to Skyline Master AMQP credentials file
    @rtype: str
    '''
    if is_windows():
        file_path = get_ni_common_appdata_dir()
        file_path = os.path.join(
            file_path, 'Skyline',
            'SkylineConfigurations', 'skyline_master.json'
        )
        return file_path
    elif is_linux():
        return '/etc/natinst/niskyline/SkylineConfigurations/skyline_master.json'
    else:
        raise RuntimeError('Unsupported platform')


def get_http_master_file():
    '''
    Return path to the Master HTTP credentials file on the minion.

    @return: Path to Master HTTP credentials file
    @rtype: str
    '''
    if is_windows():
        file_path = get_ni_common_appdata_dir()
        file_path = os.path.join(
            file_path, 'Skyline',
            'HttpConfigurations', 'http_master.json'
        )
        return file_path
    elif is_linux():
        return '/etc/natinst/niskyline/HttpConfigurations/http_master.json'
    else:
        raise RuntimeError('Unsupported platform')


def get_rabbitmq_cert_file():
    '''
    Return path to the RabbitMQ certificate file on the minion

    @return: Path to the RabbitMQ certificate file
    @rtype: str
    '''
    if is_windows():
        file_path = get_ni_common_appdata_dir()
        file_path = os.path.join(
            file_path, 'Skyline',
            'Certificates', 'rabbitmq-client', 'rabbitmq-client.cer'
        )
        return file_path
    elif is_linux():
        return '/etc/natinst/niskyline/Certificates/rabbitmq-client/rabbitmq-client.cer'
    else:
        raise RuntimeError('Unsupported platform')


def get_http_cert_file():
    '''
    Return path to the HTTP certificate file on the minion

    @return: Path to the HTTP certificate file
    @rtype: str
    '''
    if is_windows():
        file_path = get_ni_common_appdata_dir()
        file_path = os.path.join(
            file_path, 'Skyline',
            'Certificates', 'http-client', 'http-client.cer'
        )
        return file_path
    elif is_linux():
        return '/etc/natinst/niskyline/Certificates/http-client/http-client.cer'
    else:
        raise RuntimeError('Unsupported platform')


def health_monitoring_grains(opts):
    '''
    Health Monitoring related grains
    '''
    # Provides:
    #    health_monitoring_enabled
    #    health_monitoring_interval
    grains = {}

    dynamic_conf = _nisysmgmt_config.read_dynamic_config(opts)

    health_monitoring_conf = dynamic_conf.get('health_monitoring', {})
    grains['health_monitoring_enabled'] = health_monitoring_conf.get(
        'enabled', DEFAULT_HEALTH_MONITORING_ENABLED
    )
    grains['health_monitoring_interval'] = health_monitoring_conf.get(
        'interval', DEFAULT_HEALTH_MONITORING_INTERVAL
    )
    grains['health_monitoring_retention_type'] = health_monitoring_conf.get(
        'retention_type', DEFAULT_HEALTH_MONITORING_RETENTION_TYPE
    )
    grains['health_monitoring_retention_duration_days'] = health_monitoring_conf.get(
        'retention_duration_days', DEFAULT_HEALTH_MONITORING_RETENTION_DURATION_DAYS
    )
    grains['health_monitoring_retention_max_history_count'] = health_monitoring_conf.get(
        'retention_max_history_count', DEFAULT_HEALTH_MONITORING_RETENTION_MAX_HISTORY_COUNT
    )
    return grains


def uniquify_list(list_arg):
    '''
    Return a list of the unique elements in the list argument while
    preserving their order.
    '''
    added = set()
    ordered_list = []
    for element in list_arg:
        if element in added:
            continue
        added.add(element)
        ordered_list.append(element)
    return ordered_list


def set_salt_minion_master_config(unregister=False, master_list=None, master_finger=None):
    '''
    Changes the configuration of the Master hostname and fingerprint.

    :param bool unregister: True when unregistering. False when registering.
    :param list master_list: List of masters to register. Required when
                             'unregister' is False.
    :param str master_finger: The fingerprint to use when validating a master.
                              Optional when 'unregister' is False.

    :return: old_master, master_changed
             old_master: The Master hostname or list of addresses used
                         previously. Empty string if none was found.
             master_changed: True if the new Master hostname is different
                             from the previous one. False otherwise.
    '''
    if unregister is True:
        # Set the Master address to an unroutable address (empty string) and
        # set the master fingerprint to an empty string
        new_master = ''
    else:
        # The master_list argument is always a list.
        # A list is required for the yaml dump and to preserve order.
        new_master = uniquify_list(master_list)
        if len(new_master) == 1:
            new_master = new_master[-1]

    if master_finger is None:
        master_finger = ''

    master_changed = True
    old_master = ''

    config_file = get_salt_minion_master_config_file()
    if os.path.isfile(config_file):
        with open(config_file, 'r') as fp_:  # pylint: disable=resource-leakage
            config_data = yaml.load(fp_)

        if isinstance(config_data, dict):
            if 'master' in config_data:
                old_master = config_data['master']
                if new_master == old_master:
                    master_changed = False
        else:
            config_data = {}
    else:
        config_data = {}

    config_data['master_finger'] = master_finger
    if master_changed:
        config_data['master'] = new_master
        if isinstance(new_master, str):
            config_data['master_type'] = 'str'
        else:
            config_data['master_type'] = 'failover'
            # Avoid this error in the log:
            #     [CRITICAL][2205] 'master_type' set to 'failover' but
            #     'retry_dns' is not 0. Setting 'retry_dns' to 0 to
            #     failover to the next master on DNS errors.
            config_data['retry_dns'] = 0
    if unregister is True:
        config_data['master_type'] = 'disable'
    with open(config_file, 'w') as fp_:  # pylint: disable=resource-leakage
        yaml.dump(config_data, fp_, default_flow_style=False)

    return old_master, master_changed


def clear_pki_minion_master_cache():
    '''
    Removes the Minion's PKI cache of the Master public key.
    Meant to be called if the Minion ID or Master hostname has changed.
    '''
    pki_file = get_salt_pki_minion_master_pubkey_file()
    if os.path.isfile(pki_file):
        os.remove(pki_file)


def remove_skyline_master_file():
    '''
    Removes the Skyline Master AMQP credentials file from the minion
    (if it exists).
    '''
    file_path = get_skyline_master_file()
    if os.path.isfile(file_path):
        os.remove(file_path)


def remove_http_master_file():
    '''
    Removes the Master HTTP credentials file from the minion
    (if it exists).
    '''
    file_path = get_http_master_file()
    if os.path.isfile(file_path):
        os.remove(file_path)


def remove_rabbitmq_cert_file():
    '''
    Removes the RabbitMQ certificate file from the minion
    (if it exists).
    '''
    file_path = get_rabbitmq_cert_file()
    if os.path.isfile(file_path):
        os.remove(file_path)


def remove_http_cert_file():
    '''
    Removes the HTTP certificate file from the minion
    (if it exists).
    '''
    file_path = get_http_cert_file()
    if os.path.isfile(file_path):
        # On Windows, do not remove the certificate from the Windows
        # Certificate Store because it may be used for other purposes.
        os.remove(file_path)


def open_detached_process(cmd, forward_stdin = True, capture_stdout = True, capture_stderr = True):
    '''
    Create a process that is not a child of the current process,
    otherwise known as a detached process.
    '''
    kwargs = {}
    if is_windows():
        CREATE_NEW_PROCESS_GROUP = 0x00000200  # pylint: disable=invalid-name
        DETACHED_PROCESS = 0x00000008  # pylint: disable=invalid-name
        kwargs.update(
            creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
        )
    elif sys.version_info < (3, 2):
        # Python < 3.2, Unix
        kwargs.update(preexec_fn=os.setsid)  # pylint: disable=no-member
    else:
        # Python >= 3.2, Unix
        kwargs.update(start_new_session=True)

    stdin_pipe = subprocess.PIPE
    stdout_pipe = subprocess.PIPE
    stderr_pipe = subprocess.PIPE

    if not forward_stdin:
        stdin_pipe = subprocess.DEVNULL
    if not capture_stdout:
        stdout_pipe = subprocess.DEVNULL
    if not capture_stderr:
        stderr_pipe = subprocess.DEVNULL

    proc = subprocess.Popen(
        cmd,
        stdin=stdin_pipe,
        stdout=stdout_pipe,
        stderr=stderr_pipe,
        **kwargs
    )
    return proc


def restart_salt_minion(params=[]):  # pylint: disable=dangerous-default-value
    '''
    Restart salt minion

    :param list params: Extra parameters
    '''
    helper_file_path = get_nisms_utils_helper_abs_path()
    # Start non-blocking python process. This call cannot block
    # because the spawned process can restart the minion
    cmd = [sys.executable, helper_file_path, '--restart-minion']
    cmd.extend(params)
    result = open_detached_process(cmd, False, False, False)
    return result.returncode


def stop_minion_if_running():
    '''
    This will stop the Salt Minion if it is running.
    This will do nothing if the Salt Minion is not running.
    '''
    if is_windows():
        retcode = subprocess.call(['net', 'stop', 'nisaltminion'])
        # retcode of 2 means that the service is not running
        if retcode not in (0, 2):
            sys.stderr.write(
                '{0}: Could not stop the salt-minion service. '
                'Return code: {1}.'.format(
                    os.path.basename(__file__),
                    retcode
                )
            )
            sys.exit(1)
    else:
        # This will still return 0 even if the daemon is already stopped
        retcode = subprocess.call(['/etc/init.d/salt-minion', 'stop'])
        if retcode != 0:
            sys.stderr.write(
                '{0}: Could not stop the salt-minion daemon. '
                'Return code: {1}.'.format(
                    os.path.basename(__file__),
                    retcode
                )
            )
            sys.exit(1)


def start_minion_if_not_running():
    '''
    This will start the Salt Minion if it is not running.
    This will do nothing if the Salt Minion is running.
    '''
    if is_windows():
        retcode = subprocess.call(['net', 'start', 'nisaltminion'])
        # retcode of 2 means that the service is already running
        if retcode not in (0, 2):
            sys.stderr.write(
                '{0}: Could not start the salt-minion service. '
                'Return code: {1}.'.format(
                    os.path.basename(__file__),
                    retcode
                )
            )
            sys.exit(1)
    else:
        # This will still return 0 even if the daemon is already running
        retcode = subprocess.call(['/etc/init.d/salt-minion', 'start'])
        if retcode != 0:
            sys.stderr.write(
                '{0}: Could not restart the salt-minion daemon. '
                'Return code: {1}.'.format(
                    os.path.basename(__file__),
                    retcode
                )
            )
            sys.exit(1)


def parse_args():
    '''
    This will parse the command-line arguments passed in.
    Returns a dictionary of the parsed command-line arguments.

    The master and master-list arguments are stored in the same list to
    preserve order.
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--restart-minion',
        action='store_true',
        dest='restart_minion',
        default=False,
        help='Restart the salt-minion daemon'
    )
    parser.add_argument(
        '--delay',
        dest='delay',
        default=0,
        type=int,
        help='Number of seconds to delay before starting'
    )
    parser.add_argument(
        '--clear-pki-cache',
        action='store_true',
        dest='clear_pki_cache',
        default=False,
        help='Removes the Minion\'s PKI cache of the Master public key.'
    )
    parser.add_argument(
        '--clear-master',
        action='store_true',
        dest='clear_master',
        default=False,
        help='Clear reference to any Master(s) from the Minion\'s configuration.'
    )
    args = parser.parse_args()
    return args


def main():
    '''
    This is the main entry point for this script.
    '''
    if not is_windows() and not is_linux():
        sys.stderr.write(
            '{0}: Unsupported platform. Only Windows and Linux are '
            'supported.'.format(
                os.path.basename(__file__)
            )
        )
        sys.exit(1)

    args = parse_args()

    if args.delay:
        time.sleep(args.delay)

    mutex = _nisysmgmt_mutex.NamedMutex(MUTEX_NAME)
    with mutex:
        if args.restart_minion:
            stop_minion_if_running()
        if args.clear_master:
            set_salt_minion_master_config(unregister=True)
            remove_skyline_master_file()
            remove_rabbitmq_cert_file()
            remove_http_master_file()
            remove_http_cert_file()
        if args.clear_pki_cache:
            clear_pki_minion_master_cache()
        if args.restart_minion:
            start_minion_if_not_running()

        sys.exit(0)


if __name__ == '__main__':
    main()
