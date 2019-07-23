# -*- coding: utf-8 -*-
'''
National Instruments SystemLink Health Monitoring Shared Component
'''

# Import Python libs
from __future__ import absolute_import
import os
import shutil

# Import third party libs
# pylint: disable=import-error,3rd-party-module-not-gated
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
# pylint: enable=import-error,3rd-party-module-not-gated

# Import salt libs
# pylint: disable=import-error,3rd-party-module-not-gated
import salt.utils.platform
import salt.ext.six as six
from salt.ext.six.moves import range  # pylint: disable=import-error,redefined-builtin
from salt.ext.six.moves import zip  # pylint: disable=import-error,redefined-builtin
# pylint: enable=import-error,3rd-party-module-not-gated

NUM_CPUS = None
CPU_USAGE_INTERVAL = 2
BEGIN_SNAPSHOT_CPU_TIMES = None

# Tag Information
DOUBLE = 'DOUBLE'
INT = 'INT'
STRING = 'STRING'


def setup_tags(tag_info, id_):
    '''
    Set up the tag metadata.

    :param tag_info: The dictionary used to hold the tag metadata and
        values.
    :type tag_info: dict(str, dict)
    :param id_: The ID to use as the root name of the tag.
    :type id_: str
    '''
    global NUM_CPUS  # pylint: disable=global-statement

    NUM_CPUS = psutil.cpu_count(logical=True)
    tag_info['disk_free'] = {'path': id_ + '.Health.Disk.Free', 'type': DOUBLE}
    tag_info['disk_used'] = {'path': id_ + '.Health.Disk.Used', 'type': DOUBLE}
    tag_info['disk_total'] = {'path': id_ + '.Health.Disk.Total', 'type': DOUBLE}
    tag_info['disk_perc'] = {'path': id_ + '.Health.Disk.UsePercentage', 'type': DOUBLE}
    tag_info['mem_free'] = {'path': id_ + '.Health.Memory.Free', 'type': DOUBLE}
    tag_info['mem_used'] = {'path': id_ + '.Health.Memory.Used', 'type': DOUBLE}
    tag_info['mem_total'] = {'path': id_ + '.Health.Memory.Total', 'type': DOUBLE}
    tag_info['mem_perc'] = {'path': id_ + '.Health.Memory.UsePercentage', 'type': DOUBLE}
    tag_info['num_cpus'] = {'path': id_ + '.Health.CPU.Count', 'type': INT, 'value': NUM_CPUS}
    tag_info['cpu_mean_perc'] = {'path': id_ + '.Health.CPU.MeanUsePercentage', 'type': DOUBLE}
    for i in range(NUM_CPUS):
        key_name = 'cpu{0}_perc'.format(i)
        path_name = id_ + '.Health.CPU.{0}.UsePercentage'.format(i)
        tag_info[key_name] = {'path': path_name, 'type': DOUBLE}


def calc_disk(tag_info):
    '''
    Calculate disk related statistics

    :param tag_info: The dictionary used to hold the tag metadata and
        values.
    :type tag_info: dict(str, dict)
    '''
    if salt.utils.platform.is_windows():
        root_disk_path = 'C:\\'
    else:
        root_disk_path = '/'

    if six.PY3:
        disk_usage = shutil.disk_usage(root_disk_path)  # pylint: disable=no-member
        disk_total = float(disk_usage.total)
        disk_used = float(disk_usage.used)
        disk_free = float(disk_usage.free)
    else:
        fd_ = os.open(root_disk_path, os.O_RDONLY)
        try:
            disk_info = os.fstatvfs(fd_)  # pylint: disable=no-member
            disk_total = float(disk_info.f_frsize) * float(disk_info.f_blocks)
            disk_free = float(disk_info.f_frsize) * float(disk_info.f_bfree)
            disk_used = disk_total - disk_free
        finally:
            os.close(fd_)

    tag_info['disk_free']['value'] = disk_free
    tag_info['disk_used']['value'] = disk_used
    tag_info['disk_total']['value'] = disk_total
    tag_info['disk_perc']['value'] = (disk_used / disk_total) * 100


def calc_mem(tag_info):
    '''
    Calculate memory related statistics

    :param tag_info: The dictionary used to hold the tag metadata and
        values.
    :type tag_info: dict(str, dict)
    '''
    virt = psutil.virtual_memory()
    # virt.free != virt.available
    # On Linux, virt.free corresponds to 'MemFree' in '/proc/meminfo'.
    # On Linux, virt.available corresponds to 'MemAvailable' in '/proc/meminfo'.
    #
    # An explanation of the difference here:
    # https://superuser.com/questions/980820/what-is-the-difference-between-memfree-and-memavailable-in-proc-meminfo
    #
    # For our purposes, we will use the more conservative virt.free and
    # calculate 'used' and 'percentage' values based on that (psutil uses
    # virt.available to calculate its corresponding virt.used value).
    #
    # Output of the 'free' command shows this:
    #              total       used       free     shared    buffers     cached
    # Mem:        903252     229020     674232       1056      26492      73448
    # -/+ buffers/cache:     129080     774172
    # Swap:            0          0          0
    #
    # Notice that the first row in the output uses 'MemFree' for the 'free'
    # column and the second row uses 'MemAvailable'. Our data will correspond
    # to the first row of the 'free' command.
    mem_used = virt.total - virt.free
    tag_info['mem_free']['value'] = virt.free
    tag_info['mem_used']['value'] = mem_used
    tag_info['mem_total']['value'] = virt.total
    tag_info['mem_perc']['value'] = (float(mem_used) / float(virt.total)) * 100


def _cpu_total_time(per_cpu_times):
    '''
    Given per_cpu_times, calculate the total CPU time including idle time.
    '''
    total_time = sum(per_cpu_times)
    if salt.utils.platform.is_linux():
        # On Linux, guest times are already accounted in 'user' or
        # 'nice' times, so we subtract them from total.
        total_time -= getattr(per_cpu_times, 'guest', 0)
        total_time -= getattr(per_cpu_times, 'guest_nice', 0)
    return total_time


def _cpu_busy_time(per_cpu_times):
    '''
    Given per_cpu_times, calculate the busy CPU time.
    '''
    busy_time = _cpu_total_time(per_cpu_times)
    busy_time -= per_cpu_times.idle
    if salt.utils.platform.is_linux():
        # On Linux, 'iowait' is time during which the CPU does not do anything
        # (waits for IO to complete). 'iowait' is not accounted for
        # in 'idle' time, so we subtract it.
        busy_time -= getattr(per_cpu_times, 'iowait', 0)
    return busy_time


def _calc_per_cpu_usage(per_cpu_times1, per_cpu_times2):
    '''
    Given two CPU times snapshots, calculate the CPU usage
    in percentage.
    '''
    total_time1 = _cpu_total_time(per_cpu_times1)
    busy_time1 = _cpu_busy_time(per_cpu_times1)

    total_time2 = _cpu_total_time(per_cpu_times2)
    busy_time2 = _cpu_busy_time(per_cpu_times2)

    # This usually indicates a float precision issue.
    if busy_time2 <= busy_time1:
        return 0.0

    busy_time_diff = busy_time2 - busy_time1
    total_time_diff = total_time2 - total_time1
    try:
        busy_perc = (busy_time_diff / total_time_diff) * 100
    except ZeroDivisionError:
        return 0.0
    return busy_perc


def cpu_usage_snapshot():
    '''
    Take the beginning snapshot of CPU usage.
    '''
    global BEGIN_SNAPSHOT_CPU_TIMES  # pylint: disable=global-statement

    BEGIN_SNAPSHOT_CPU_TIMES = psutil.cpu_times(percpu=True)


def calc_cpu(tag_info):
    '''
    Calculate CPU related statistics

    :param tag_info: The dictionary used to hold the tag metadata and
        values.
    :type tag_info: dict(str, dict)
    '''
    # This is the ending snapshot of CPU usage. The beginning snapshot
    # should have been taken CPU_USAGE_INTERVAL seconds prior to
    # this invocation, via the _cpu_usage_snapshot() function.
    end_cpu_times = psutil.cpu_times(percpu=True)

    cpu_times_sum = 0.0
    cpu_idx = 0
    for per_cpu_times1, per_cpu_times2 in zip(
            BEGIN_SNAPSHOT_CPU_TIMES, end_cpu_times):
        per_cpu_usage = _calc_per_cpu_usage(
            per_cpu_times1, per_cpu_times2
        )
        key_name = 'cpu{0}_perc'.format(cpu_idx)
        tag_info[key_name]['value'] = round(per_cpu_usage, 1)
        cpu_times_sum += per_cpu_usage
        cpu_idx += 1

    tag_info['cpu_mean_perc']['value'] = round(cpu_times_sum / NUM_CPUS, 1)
