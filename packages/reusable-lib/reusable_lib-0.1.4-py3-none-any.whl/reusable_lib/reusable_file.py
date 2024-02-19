#!/usr/bin/env python3
"""Reusable library - File

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

from enum import Enum
import magic
import os


class exe_type(Enum):
    ELF = 1
    PE = 2
    MACH = 3
    UNSUPPORTED = 8
    FAIL = 9
    UNKNOWN = 10


class file_type(Enum):
    EXE = 1
    LIB = 2
    UNSUPPORTED = 8
    FAIL = 9
    UNKNOWN = 10


class os_type(Enum):
    LINUX = 1
    WINDOWS = 2
    MACOS = 3
    FREEBSD = 4
    FAIL = 9
    UNKNOWN = 10


class arch_type(Enum):
    I386 = 1
    X64 = 2
    ARM32 = 3
    ARM64 = 4
    RISCV32 = 5
    RISCV64 = 6
    FAIL = 9
    UNKNOWN = 10


def get_executable_format(filename) -> exe_type:
    e_type = exe_type.UNKNOWN
    o_type = os_type.UNKNOWN
    a_type = arch_type.UNKNOWN

    if not os.path.exists(filename):
        return exe.type.UNSUPPORTED

    fs = magic.from_file(filename)
    print(type(fs), fs)

    if 'ELF' in fs:
        e_type = exe_type.ELF
    if 'PE' in fs:
        e_type = exe_type.PE

    if 'Linux' in fs:
        o_type = os_type.LINUX

    if 'aarch64' in fs:
        a_type = arch_type.ARM64
    if 'x86-64' in fs:
        a_type = arch_type.X64

    return (e_type, o_type, a_type)


if __name__ == "__main__":
    print(get_executable_format("/bin/ls"))
