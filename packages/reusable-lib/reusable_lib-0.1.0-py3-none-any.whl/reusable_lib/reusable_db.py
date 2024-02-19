#!/usr/bin/env python3
"""Reusable library - DB (Postgresql)

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

sudo apt install libpq-dev
pip install psycopg2

"""

import psycopg2
import json
import toml


def get_vt(db, h):
    """
    output is an array of dictionaries.
    """
    conn = psycopg2.connect(db)
    cur = conn.cursor()

    output = []
    for _h in h:
        sql = "select * from data where hash = '%s';"
        print(sql)
        v = cur.execute(sql % _h)
        print(v)
        o = cur.fetchall()
        output = output + o
    conn.close()

    return output


def save_vt(db, k, h, output, debug=False):

    conn = psycopg2.connect(db)
    cur = conn.cursor()

    l = len(h)
    for i in range(l):
        js = json.dumps(output[i])
        v = cur.execute("insert into data(hash, result) values(%s, %s)", \
                (h[i], js))
        if debug:
            print(v)

    conn.commit()

    #v = cur.execute("select * from data")
    #print(v)

    conn.close()


if __name__ == "__main__":
    r = toml.load('default_db.toml')
    conf = r['reusable_db']
    output = get_vt(conf['db'], conf['hash'])
    for i in output:
        j = i[2]
        print('-------')
        print(json.dumps(j, indent=4))
