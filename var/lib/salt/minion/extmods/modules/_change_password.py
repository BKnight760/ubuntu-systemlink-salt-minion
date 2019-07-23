# -*- coding: utf-8 -*-
'''
A module for changing the password of superuser.
'''

# Import python libs
from __future__ import absolute_import
# Import salt libs
# pylint: disable=import-error,3rd-party-module-not-gated
import salt.utils.platform
from salt.exceptions import CommandExecutionError

# Import local libs
import _nisysmgmt_grains
# pylint: disable=import-error,3rd-party-module-not-gated

NIAUTH_PASSWD_PATH = '/usr/sbin/niauth-passwd'


def change_password(strategy, grains):
    '''
    Static method that implements the generic algorithm
    '''
    if salt.utils.platform.is_windows():
        raise CommandExecutionError('This feature is not supported by the current target')
    elif 'NILinuxRT' in grains['os_family'] and 'nilrt' == grains['lsb_distrib_id']:
        ret = strategy.do_currentgen_work()
    else:
        ret = strategy.do_nextgen_work()
    if ret:
        _nisysmgmt_grains.set_last_known_is_superuser_password_set(strategy.is_password_set)
    return ret


class DeletePasswordStrategy(object):
    '''
    Class implementing the password-delete functionality
    '''
    def __init__(self):
        '''
        Setting the flag signaling that after this operation the password will not be set
        '''
        self.is_password_set = False

    def do_currentgen_work(self):  # pylint: disable=no-self-use
        '''
        Do CG specific work
        '''
        result = __salt__['cmd.run']('{0} admin'.format(NIAUTH_PASSWD_PATH), stdin='')
        return bool(result == 'Password changed')

    def do_nextgen_work(self):  # pylint: disable=no-self-use
        '''
        Do NG specific work
        '''
        return __salt__['shadow.del_password']('root')


class SetPasswordStrategy(object):
    '''
    Class implementing the password-set functionality
    '''
    def __init__(self, passwd):
        '''
        Setting the flag signaling that after this operation the password will not be set
        Setting the password
        '''
        self.passwd = passwd
        self.is_password_set = True

    def do_currentgen_work(self):
        '''
        Do CG specific work
        '''
        result = __salt__['cmd.run']('{0} admin'.format(NIAUTH_PASSWD_PATH), stdin=self.passwd)
        return bool(result == 'Password changed')

    def do_nextgen_work(self):
        '''
        Do NG specific work
        '''
        password = __salt__['shadow.gen_password'](self.passwd)
        return __salt__['shadow.set_password']('root', password)
