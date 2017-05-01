#!/usr/bin/env python3

import os
import re
import argparse

REGEX_FI = re.compile(r'(.....)_(scan|pvol)(?:_(-?[0-9.]+))?_(\d{8}T\d{4}Z)(?:_(0x[0-9a-f]+))?(?:_(\d+))?\.h5')

def traverse(args, dname):
    print('LIST', dname)
    with os.scandir(dname) as items:
        for item in items:
            item_name = os.path.join(dname, item.name)

            if item.is_dir():
                traverse(args, item_name)
                continue

            if REGEX_FI.match(item.name):
                print('MATCH', item_name)
            else:
                print('MISMATCH', item_name)

def main(args):
    traverse(args, args.dir_in)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('dir_in', metavar='DIR_IN', help='directory with raw files')
    main(ap.parse_args())
