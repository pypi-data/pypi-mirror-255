#!/usr/bin/env python3
"""Reusable library - Virustotal

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

import argparse
import vt
import json
import toml


def get_hash(k, h):
    output = {}
    try:
        with vt.Client(k) as client:
            """
        it = client.iterator('/intelligence/search',
            params={'query': ' '.join(args.query)},
            limit=args.limit)
        """
            f = client.get_json('/files/' + h)
            output = f
            #print(type(f))
            #print(json.dumps(f, indent=4))
    except Exception as ex:
        #print("ERROR: get_hash %s" % ex)
        pass

    return output


def query_hash(db, k, h):
    output = get_hash(k, h)
    #reusable_db.save_vt(db, k, h, output)
    return output


def main():

    parser = argparse.ArgumentParser(
        description='Make a VirusTotal Intelligence search and prints the matching objects.')  # pylint: disable=line-too-long

    parser.add_argument('--hash',
                        type=str,
                        required=True,
                        nargs='+',
                        help='a hash.')

    parser.add_argument('--apikey',
                        required=True,
                        help='your VirusTotal API key')

    parser.add_argument('--limit',
                        type=int,
                        required=False,
                        help='maximum number of objects that will be retrieved',
                        default=50)

    args = parser.parse_args()

    print(args.hash, type(args.hash))
    get_hash(args.apikey, args.hash)


if __name__ == '__main__':
    r = toml.load('default_db.toml')
    conf = r['reusable_db']
    output = get_hash(conf['key'], conf['hash'])
    #reusable_db.save_vt(conf['db'], conf['k'], conf['h'], output, True)
