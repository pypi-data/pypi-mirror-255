#!/usr/bin/env python3
"""Reusable library - SQL (Sqlite)

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

import sqlite3
from sqlite3 import Error
import json


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


def connect(db):
    con = sqlite3.connect(db)
    return con


def create_table():
    con = connect("db.db")
    cur = con.cursor()
    sql = '''CREATE TABLE data (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	time TEXT, public_ip TEXT, private_ip TEXT, hostname TEXT, mac_address TEXT,
        platform TEXT, platform_release TEXT, platform_version TEXT, architecture TEXT, 
        processor TEXT, physical_cores INTEGER, logical_cores INTEGER, CF_min INTEGER, CF_cur INTEGER, CF_max INTEGER,
        cpu_usage REAL, mem_total INTEGER, mem_available INTEGER, mem_percent REAL,
        swap_total INTEGER, swap_free INTEGER, swap_used INTEGER, swap_percent REAL,
        boot_time INTEGER,
        disk_read INTEGER,
        disk_write INTEGER,
        net_bytes_sent INTEGER,
        net_bytes_received INTEGER,
        nics_json TEXT,
        disk_json TEXT,
	misc_json TEXT);'''
    res = cur.execute(sql)
    for r in res:
        print(r)
    con.commit()
    cur.close()


def insert_entry(d, dbname="db.db"):
    con = connect(dbname)
    if not con:
        return 1

    cur = con.cursor()

    dn = d['net']
    nics = dn['nic']
    ds = d['sys']
    disks = ds['disks']

    data = (d['time'], dn['public_ip'], dn['private_ip'], dn['hostname'],
            dn['mac-address'], ds['platform'], ds['platform-release'],
            ds['platform-version'], ds['architecture'], ds['processor'],
            ds['physical-cores'], ds['logical-cores'], ds['cpu-freq'][0],
            ds['cpu-freq'][1], ds['cpu-freq'][2], ds['cpu-usage'],
            ds['mem-total'], ds['mem-available'], ds['mem-percent'],
            ds['swap-total'], ds['swap-free'], ds['swap-used'],
            ds['swap-percentage'], ds['boot-time'], ds['io-read'],
            ds['io-write'], dn['net bytes sent'], dn['net bytes received'],
            json.dumps(nics), json.dumps(disks), json.dumps({}))
    #print(json.dumps(data, indent=4))

    sql = ''' INSERT INTO data(time,public_ip,private_ip, hostname,mac_address,platform,platform_release,platform_version,architecture,processor,physical_cores, logical_cores, CF_min, CF_cur, CF_max, cpu_usage,mem_total,mem_available,mem_percent,swap_total,swap_free,swap_used,swap_percent,boot_time,disk_read,disk_write,net_bytes_sent, net_bytes_received,nics_json,disk_json,misc_json)
              VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''
    # 31
    res = cur.execute(sql, data)
    for r in res:
        print(r)
    con.commit()
    cur.close()

    return 0


def db_init():
    create_connection("db.db")
    create_table()
    """
    import b
    a = b.a
    j = json.dumps(a, indent=4)
    d = json.loads(j)
    insert_entry(d)
    """


if __name__ == '__main__':
    db_init()
