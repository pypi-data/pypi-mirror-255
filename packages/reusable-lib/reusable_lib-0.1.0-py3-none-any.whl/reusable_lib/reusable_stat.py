#!/usr/bin/env python3
"""Reusable library - Stat

MIT License

Copyright (c) 2023 JJR

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Requirements:

"""

import sys
import os

from datetime import datetime
import json
import logging
import time
import psutil
import platform
import socket
import uuid
import re
import subprocess

__version__ = "0.0.2"


def get_time():
    now = datetime.now()
    current_time = now.strftime("%Y%m%d%H%M%S%z")
    #print("Current Time =", current_time)
    return current_time


def get_time_epoch():
    return int(time.time())


def get_net():
    public_ip = os.popen("curl -s http://ifconfig.me").read()
    private_ip = socket.gethostbyname(socket.gethostname())
    info = {"public_ip": public_ip, "private_ip": private_ip}

    info['hostname'] = socket.gethostname()
    info['mac-address'] = ':'.join(re.findall('..', '%012x' % uuid.getnode()))

    try:
        nic = info['nic'] = {}
        # Network
        if_addrs = psutil.net_if_addrs()
        for interface_name, interface_addresses in if_addrs.items():
            n = nic[interface_name] = []
            for address in interface_addresses:
                n.append(\
                    {'family': address.family,
                     'address': address.address,
                     'netmask': address.netmask,
                     'broadcast': address.broadcast})
        net_io = psutil.net_io_counters()
        info['net bytes sent'] = net_io.bytes_sent
        info['net bytes received'] = net_io.bytes_recv
    except Exception as e:
        logging.exception(e)

    return info


def getSystemInfo():
    info = {}
    try:
        info['platform'] = platform.system()
        info['platform-release'] = platform.release()
        info['platform-version'] = platform.version()
        info['architecture'] = platform.machine()
        info['processor'] = platform.processor()
        info['physical-cores'] = psutil.cpu_count(logical=False)
        info['logical-cores'] = psutil.cpu_count(logical=True)
        cpufreq = psutil.cpu_freq()
        info['cpu-freq'] = (cpufreq.min, cpufreq.current, cpufreq.max)
        info['cpu-usage'] = psutil.cpu_percent()

        #info['ram']=str(round(psutil.virtual_memory().total / (1024.0 **3)))+" GB"
        #info['ram']=psutil.virtual_memory().total
        svmem = psutil.virtual_memory()
        info['mem-total'] = svmem.total
        info['mem-available'] = svmem.available
        info['mem-used'] = svmem.used
        info['mem-percent'] = svmem.percent
        swap = psutil.swap_memory()
        info['swap-total'] = swap.total
        info['swap-free'] = swap.free
        info['swap-used'] = swap.used
        info['swap-percentage'] = swap.percent

        # Boot Time
        boot_time_timestamp = psutil.boot_time()
        #bt = datetime.fromtimestamp(boot_time_timestamp)
        #info['boot-time'] = (bt.year, bt.month,bt.day,bt.hour, bt.minute, bt.second)
        info['boot-time'] = int(boot_time_timestamp)

        # Disk
        d = info['disks'] = {}
        partitions = psutil.disk_partitions()
        for partition in partitions:
            dd = d[partition.device] = {
                'device': partition.device,
                'mountpoint': partition.mountpoint,
                'FS type': partition.fstype
            }
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                dd['total size'] = usage.total
                dd['used'] = usage.used
                dd['free'] = usage.free
                dd['percent'] = usage.percent

            except PermissionError:
                continue

        # get IO statistics since boot
        disk_io = psutil.disk_io_counters()
        info['io-read'] = disk_io.read_bytes
        info['io-write'] = disk_io.write_bytes

    except Exception as e:
        logging.exception(e)
    return info


def parse_W_user(s, header):
    """
    # Linux
    USER     TTY      FROM             LOGIN@   IDLE   JCPU   PCPU WHAT
    jrhee2   :0       :0               06Jul23 ?xdm?   5days  0.00s /usr/lib/gdm3/gdm-x-session --run-script env GNOME_SHELL_SESSION_MODE=ubuntu /usr/bin/gnome-session --systemd --session=ubuntu
    jrhee2   pts/4    10.255.14.91     04:59    6.00s  1.79s  0.00s /bin/sh -c w

    # Mac
    USER     TTY      FROM              LOGIN@  IDLE WHAT
rhee     console  -                Wed13   16:43 -
rhee     s000     -                Wed18    9:12 -bash
rhee     s001     -                 4:59       9 ssh jrhee7 s      ��    /usr/bin/ssh
rhee     s004     -                 6:19       - w
    """
    res = {}
    lheader = len(header.split())
    tk = s.split()
    #print(tk)
    if lheader == 8:
        res['user'] = tk[0].strip()
        res['tty'] = tk[1].strip()
        res['from'] = tk[2].strip()
        res['login'] = tk[3].strip()
        res['idle'] = tk[4].strip()
        res['jcpu'] = tk[5].strip()
        res['pcpu'] = tk[6].strip()
        res['what'] = tk[7:]
    elif lheader == 6:
        res['user'] = tk[0].strip()
        res['tty'] = tk[1].strip()
        res['from'] = tk[2].strip()
        res['login'] = tk[3].strip()
        res['idle'] = tk[4].strip()
        res['what'] = tk[5:]
    else:
        log.error('unsupported header [%s]' % header)

    return res


def parse_uptime(s):
    """
     - Mac
     5:24  up 15:39, 6 users, load averages: 6.54 5.15 4.85
     - Linux
    05:23:26 up 6 days,  8:06,  2 users,  load average: 0.02, 0.07, 0.08
    """
    res = {}
    # Linux
    if 'load average:' in s:
        tk = s.split('load average:')
    # Mac
    elif 'load averages:' in s:
        tk = s.split('load averages:')
    if len(tk) == 2:
        # up and user tk1
        tk1 = tk[0].split(',')
        #print(tk1)
        for i in tk1:
            if 'up' in i:
                tk2 = i.split('up')
                #print(tk2)
                if len(tk2) == 2:
                    res['now'] = tk2[0].strip()
                    res['now2'] = get_time()
                    res['now_epoch'] = get_time_epoch()
                    res['up'] = tk2[1].strip()
            elif 'users' in i:
                tk3 = i.split()
                if len(tk3) == 2:
                    res['num_users'] = int(tk3[0])
                #print(tk3)

        # load tk2
        if ',' in tk[1]:
            tk2 = tk[1].split(',')
        else:
            tk2 = tk[1].split()
        # there should be three
        load = res['load'] = []
        #print(tk2)
        if len(tk2) == 3:
            for i in tk2:
                try:
                    load.append(float(i.strip()))
                except Exception as ex:
                    logging.error(ex)
    """
    load = tk[1]
    print('load', load)
    print(tk[0])
    tk = s.split(',')
    tk_len = len(tk)
    print(tk)
    idx = 0
    for i in tk:
        i = i.strip()
        print(i)
        if 'up' in i:
            print(1, i)
        elif 'users' in i:
            print(2, i)
        elif 'load average:' in i:
            print(3, i)

        idx += 1
    """
    return res


def get_uptime():
    res = {}
    try:
        u = os.popen("uptime").read()
    except Exception as e:
        logging.error(e)
        return res

    u = u.split('\n')
    if len(u) > 0:
        res['uptime'] = parse_uptime(u[0])

    try:
        # Only Linux
        u = os.popen("uptime -s").read()
        res['uptime-s'] = u.strip()
    except Exception as e:
        logging.error(e)
        logging.error('uptime -s')
        return res

    return res


def getW():
    res = {}
    try:
        #w = os.popen("w -h").read()
        w = subprocess.run(['w'], stdout=subprocess.PIPE).stdout
        w = w.decode('utf-8', 'ignore')
    except Exception as e:
        logging.error(e)
        return res

    users = res['users'] = []
    w = w.split('\n')
    if len(w) >= 3:
        res['uptime'] = parse_uptime(w[0])
        header = w[1]
        for i in w[2:]:
            if i.strip() == '':
                continue
            users.append(parse_W_user(i, header))

    return res


def test():
    res = {}
    #res["time"]= get_time(),
    #res["net"] = get_net(),
    #res["sys"] = getSystemInfo()
    #res['w'] = getW()
    #res['uptime'] = get_uptime()
    res['ps'] = get_ps()
    return res


"""
def get_size(bytes, suffix="B"):
    #Scale bytes to its proper format
    #e.g:
    #    1253656 => '1.20MB'
    #    1253656678 => '1.17GB'
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor
"""


def get_ps():
    res = {}
    ps = res['ps'] = []
    for p in psutil.process_iter():
        pinfo = {}
        try:
            pinfo['pid'] = int(p.pid)
        except Exception as ex:
            pass
        try:
            pinfo['ppid'] = int(p.ppid())
        except Exception as ex:
            pass
        try:
            pinfo['name'] = str(p.name())
        except Exception as ex:
            pass
        try:
            c = p.cmdline()
            #pinfo['cmdline'] = list(filter(lambda x: len(x) > 0, c))
            pinfo['cmdline'] = list(filter(None, c))
        except Exception as ex:
            pass
        try:
            pinfo['environment'] = p.environ()
        except Exception as ex:
            pass
        try:
            #pinfo['create_time_format'] = datetime.datetime.fromtimestamp(p.create_time()).strftime("%Y%m%d%H%M%S%z")
            pinfo['create_time'] = p.create_time()
        except Exception as ex:
            pass

        ps.append(pinfo)
    return res


def make_data():
    global __version__
    data = {
        "time": get_time(),
        "time_epoch": get_time_epoch(),
        "net": get_net(),
        "sys": getSystemInfo(),
        "w": getW(),
        "uptime": get_uptime(),
        "ps": get_ps(),
        "version": __version__,
    }
    return data


if __name__ == "__main__":
    print(json.dumps(make_data(), indent=4))
