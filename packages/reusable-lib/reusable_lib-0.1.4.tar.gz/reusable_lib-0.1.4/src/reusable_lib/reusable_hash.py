#!/usr/bin/env python3
"""Reusable library - Hash

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
"""

import sys
import hashlib
import pprint

import tlsh
import telfhash
#import ssdeep
#import sdhash

BUF_SIZE = 65536


def lsh_distance(a, b, format='tlsh'):
    if format == 'tlsh':
        if a == 'TNULL' or b == 'TNULL':
            return -1
        if a == None or b == None:
            return -1
        return tlsh.diff(a.upper(), b.upper())
    else:
        print('ERROR: lsh_distance unsupported hash')
        sys.exit(1)
    """
    elif format == 'ssdeep':
        return 100 - ssdeep.compare(a.upper(), b.upper())
    """

def get_lsh_string(st, format='tlsh'):
    """
    get an LSH of a set s
    """
    tmp = 'abcdefghijklmnopqrstuvwxyz'

    #print(st)
    encoded = bytes(st, 'utf-8')
    if format == 'tlsh':
        #return tlsh.forcehash(encoded)
        hs = tlsh.hash(encoded)
        while hs == 'TNULL':
            st = st + tmp
            encoded = bytes(st, 'utf-8')
            hs = tlsh.hash(encoded)
        return hs
    else:
        print('ERROR: get_lsh unsupported hash')
        sys.exit(1)
    """
    elif format == 'ssdeep':
        return ssdeep.hash(encoded_st)
    """


def get_lsh(s, format='tlsh'):
    """
    get an LSH of a set s
    """
    l = sorted(s)
    st = ",".join(l)
    stl = len(st)
    tmp = 'abcdefghijklmnopqrstuvwxyz'

    #print(st)
    encoded = bytes(st, 'utf-8')
    if format == 'tlsh':
        #return tlsh.forcehash(encoded)
        hs = tlsh.hash(encoded)
        while hs == 'TNULL':
            st = st + tmp
            encoded = bytes(st, 'utf-8')
            hs = tlsh.hash(encoded)
        return hs
    else:
        print('ERROR: get_lsh unsupported hash')
        sys.exit(1)
    """
    elif format == 'ssdeep':
        return ssdeep.hash(encoded_st)
    """


def get_gen_lsh(f, l, s):
    g = f | l | s
    return get_lsh(g)


def get_telfhash(filename):
    if not isinstance(filename, str):
        filename = str(filename)
    val = telfhash.telfhash(filename)
    if len(val) > 0:
        _v = val[0]
        if not 'telfhash' in _v:
            return None
        v = _v['telfhash']
        if v == '-':
            return None
        else:
            return v
    else:
        return None


def get_md5_hash(filename):
    if not isinstance(filename, str):
        filename = str(filename)
    func = hashlib.md5()
    return get_hash(filename, func)


def get_sha1_hash(filename):
    if not isinstance(filename, str):
        filename = str(filename)
    func = hashlib.sha1()
    return get_hash(filename, func)


def get_sha256_hash(filename):
    if not isinstance(filename, str):
        filename = str(filename)
    func = hashlib.sha256()
    return get_hash(filename, func)


def get_sha512_hash(filename):
    if not isinstance(filename, str):
        filename = str(filename)
    func = hashlib.sha512()
    return get_hash(filename, func)


def get_hash(filename, func):
    with open(filename, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            func.update(data)
    return func.hexdigest()


if __name__ == "__main__":
    filename = "/bin/ls"
    print('md5', get_md5_hash(filename))
    print('sha1', get_sha1_hash(filename))
    print('sha256', get_sha256_hash(filename))
    print('sha512', get_sha512_hash(filename))
    print('telfhash', get_telfhash(filename))
