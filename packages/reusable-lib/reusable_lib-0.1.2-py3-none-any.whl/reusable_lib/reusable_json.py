#!/usr/bin/env python3
"""Reusable library - JSON

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

import json
import os


def json_filesave(obj, filename):
    try:
        with open(filename, 'w') as outfile:
            json.dump(obj, outfile, indent=4, sort_keys=True)
    except Exception as e:
        print('ERROR: json_filesave', e)
        return 1

    return 0


def json_fileload(filename):
    data = None
    try:
        with open(filename, 'r') as infile:
            data = json.loads(infile.read())
    except Exception as e:
        print('ERROR: json_fileload', e)
        return None
    return data


def json_print(j):
    print(json.dumps(j, indent=4))
