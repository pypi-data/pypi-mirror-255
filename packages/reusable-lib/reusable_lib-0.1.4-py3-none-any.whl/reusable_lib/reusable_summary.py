# !/usr/bin/python

import sys
import os
import argparse
import magic
import pathlib

KB = 1024
MB = KB * 1024
GB = MB * 1024
TB = GB * 1024
EB = TB * 1024

#debug = True
#debug_link = True
debug = False
debug_link = False

magic_type = {}
ext_type = {}


def more_than_one_link(filename):
    try:
        n = os.stat(filename).st_nlink
        if n > 1:
            if debug_link:
                print('NUMLINK', filename, n)
            return True
    except Exception as ex:
        print('ERROR: more_than_one_link %s %s' % (filename, ex))
    return False


def nav(path):
    if os.path.isfile(path):
        return nav_file(path)
    elif os.path.isdir(path):
        return nav_dir(path)
    else:
        print('ERROR: nav %s' % (path))
        return None


def nav_file(path):
    cache = {}

    dirnum = 0
    filenum = 1
    total_size = 0
    slinknum = 0
    hlinknum = 0
    invalid_file = 0
    invalid_dir = 0

    if os.path.islink(path):
        slinknum = 1
    if not os.path.isfile(path):
        invalid_file += 1
        print('-INVALID FILE 2: %s' % c)
    else:
        if more_than_one_link(path):
            hlinknum = 1
        try:
            stat = os.stat(path)
            total_size += stat.st_size
        except Exception as ex:
            print('ERROR: %s %s' % (path, ex))
            invalid_file += 1

    return (dirnum, filenum, total_size, slinknum, hlinknum, invalid_file,
            invalid_dir)


def nav_dir(path):
    cache = {}

    for root, dirs, files in os.walk(path, topdown=False):
        dirnum = 0
        filenum = 0
        total_size = 0
        slinknum = 0
        hlinknum = 0
        invalid_file = 0
        invalid_dir = 0

        filenum += len(files)

        for name in files:
            c = os.path.join(root, name)
            ft = magic.from_file(c)

            if not ft in magic_type:
                fts = magic_type[ft] = []
            else:
                fts = magic_type[ft]
            fts.append(c)

            ext = pathlib.Path(c).suffix
            if not ext in ext_type:
                exts = ext_type[ext] = []
            else:
                exts = ext_type[ext]
            exts.append(c)

            print(ext, ft, c)

            if os.path.islink(c):
                if debug_link:
                    print('-SYMLINK', root, '-f-', c)
                slinknum += 1
                #continue
            if not os.path.isfile(c):
                invalid_file += 1
                print('-INVALID FILE 1: %s' % c)
                continue
            if more_than_one_link(c):
                if debug_link:
                    print('-HARDLINK', root, '-f-', c)
                hlinknum += 1
                #continue
            if debug:
                print('-', root, '-f-', c)
            try:
                stat = os.stat(c)
                total_size += stat.st_size
            except Exception as ex:
                print('ERROR: %s %s' % (c, ex))

        if debug:
            print(root, dirs)
        for name in dirs:
            c = os.path.join(root, name)

            if os.path.islink(c):
                slinknum += 1
                #continue
            if not os.path.isdir(c):
                print('INVALID DIR 1: %s' % c)
                invalid_dir += 1
                continue

            hlink = False
            if more_than_one_link(c):
                if debug_link:
                    print('-HARDLINK', root, '-f-', c)
                hlinknum += 1
                #continue
                hlink = True

            if not c in cache:
                #print('ERROR: %s has no cache' % c)
                invalid_dir += 1
                continue

            c_dirnum, c_filenum, c_total_size, c_slinknum, c_hlinknum, c_invalid_file, c_invalid_dir = cache[
                c]
            if debug:
                print('-', root, '-d-', c, cache[c])
            dirnum += c_dirnum
            filenum += c_filenum
            total_size += c_total_size

            slinknum += c_slinknum
            hlinknum += c_hlinknum
            invalid_file += c_invalid_file
            invalid_dir += c_invalid_dir

        dirnum += len(dirs)

        cache[root] = (dirnum, filenum, total_size, slinknum, hlinknum,
                       invalid_file, invalid_dir)
        #print('+', root, cache[root])

    #print(path, cache[path])
    if not path in cache:
        return None
    return cache[path]


def unit_print(v):
    global KB
    global MB
    global GB
    global TB

    res = ''
    if v < KB:
        res = '%d' % v
    elif v < MB:
        res = '%d KB' % (v / KB)
    elif v < GB:
        res = '%d MB' % (v / MB)
    elif v < TB:
        res = '%d GB' % (v / GB)
    elif v < EB:
        res = '%d TB' % (v / TB)
    else:
        res = '%d EB' % (v / EB)

    return res


def summary():
    """
    print('magic_type')
    for i in magic_type:
        print('   ', len(magic_type[i]), i)
    """
    print('ext_type')
    for i in ext_type:
        print('   ', len(ext_type[i]), i)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='File/Dir analysis.')
    parser.add_argument('objects', nargs='+', help='Dirs or files')
    args = parser.parse_args()
    for i in args.objects:
        v = nav(i)
        if v == None:
            print('ERROR', i)
            continue

        print()
        print('%40s : %10d dirs %10d files %10s slinks %5d hlinks %5d invalid file %5d invalid dir %3d'\
                % (i, v[0], v[1], unit_print(v[2]), v[3], v[4], v[5], v[6]))
        """
        print('*', i, ':', v[0], 'dirs', v[1], \
                'files', unit_print(v[2]),\
                'slinks', v[3],
                'hlinks', v[4])
        """
    summary()
