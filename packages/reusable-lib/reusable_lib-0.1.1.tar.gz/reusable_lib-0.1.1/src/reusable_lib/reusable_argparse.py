#!/usr/bin/env python3
"""Reusable library - argparse

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

import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Make a VirusTotal Intelligence search and prints the matching objects.')  # pylint: disable=line-too-long

    # multiple items
    parser.add_argument('tscap_filename',
                        nargs='+',
                        help='A required tscap filename')

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

    # alias
    parser.add_argument('-r',
                        "--rule_filename",
                        required=False,
                        help="a rule file name")

    # defined choices
    parser.add_argument('mode', choices=['train', 'predict'])

    args = parser.parse_args()

    #if args.hash
    #    self.print_help()

    print(args)
