#!/usr/bin/python

import os
import magic
import sys
#import reusable_hash


def check_exe(filename):
    fs = magic.from_file(filename)
    if 'ELF' in fs:
        return True
    else:
        return False


def get_ft(full_path):
    ft = magic.from_file(full_path)
    ts = ft.split(',')
    t = ts[0]
    t = ts[0].strip()
    if t.startswith('symbolic'):
        t = 'symbolic'
    return t

def get_filetype_dir(dir_path):

    num_dir = 0
    num_files = 0
    num_elf = 0
    num_apk = 0
    num_link = 0
    
    ft_num = {}
    hashes = {}
    
    # traverse root directory, and list directories as dirs and files as files
    for root, dirs, files in os.walk(dir_path):
        num_dir += 1
        print(root, num_dir, dirs)
        path = root.split(os.sep)
        print((len(path) - 1) * '---', os.path.basename(root))
        for file in files:
            num_files += 1
            full_path = os.path.join(root, file)
            if os.path.islink(full_path):
                num_link += 1
    
            if os.path.exists(full_path):
                print(len(path) * '   ', file, num_files)
                ft = get_ft(full_path)
                if not ft in ft_num:
                    fts = ft_num[ft] = []
                else:
                    fts = ft_num[ft]
                fts.append(full_path)
    
                if file.endswith('.apk'):
                    num_apk += 1
                e = check_exe(full_path)
                if e == True:
                    h = reusable_hash.get_md5_hash(full_path)
                    if not h in hashes:
                        hs = hashes[h] = []
                    else:
                        hs = hashes[h]
                    if not full_path in hs:
                        hs.append(full_path)
    
                    #print(len(path) * '   ', file, num_files)
                    num_elf += 1
    return num_dir, num_files, num_elf, num_apk, num_link, ft_num, hashes
    
if __name__ == "__main__":
    dir_path = sys.argv[1]
    num_dir, num_files, num_elf, num_apk, num_link, ft_num, hashes  = get_filetype_dir(dir_path)

    print('# dirpath', dir_path)
    print('# total dir', num_dir)
    print('# total files', num_files)
    print('# total ELF files', num_elf)
    print('# total APK files', num_apk)
    print('# total unique hashes', len(hashes))
    print('# total links', num_link)
    print()
    
    print('# file types')
    for ft in ft_num:
        fts = ft_num[ft]
        print(ft, len(fts))
    print('# file hashes')
    for h in hashes:
        hs = hashes[h]
        for i in hs:
            print(h, i)
