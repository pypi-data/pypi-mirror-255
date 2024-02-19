#!/usr/bin/env python3
"""Reusable library - utils

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

import toml
import logging
import os
import json
import pprint

# TOML

default_config = {
    'client': {
        'addr': 'https://clarinet.systems/report/',
        'sleep_time': 3600
    }
}


def toml_load(filename="default.toml", default_configuration=True):
    try:
        if os.path.isfile(filename):
            return toml.load(filename)
        else:
            if default_configuration == True:
                return default_config
            else:
                return {}
    except Exception as ex:
        print('ERROR: ', ex)
        if default_configuration == True:
            return default_config
        else:
            return {}


def toml_print(t):
    print(toml.dumps(t))


def json_print(t):
    print(json.dumps(t, indent=4))


def dict_print(t):
    pprint.pprint(t)


def test():
    print(toml_load())
    pass


def get_dual_log(logpath='.', logname='dual', logmode=logging.DEBUG):
    logFormatter = logging.Formatter(
        "%(asctime)s %(name)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"
    )
    rootLogger = logging.getLogger()

    fileHandler = logging.FileHandler("{0}/{1}.log".format(logpath, logname))
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)
    #rootLogger.setLevel(logging.DEBUG)
    rootLogger.setLevel(logmode)

    return rootLogger


# Log

if __name__ == "__main__":
    test()
