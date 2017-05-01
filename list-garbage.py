#!/usr/bin/env python3

import argparse

REGEX_FI = re.compile(r'(.....)_(scan|pvol)(?:_(-?[0-9.]+))?_(\d{8}T\d{4}Z)(?:_(0x[0-9a-f]+))?(?:_(\d+))?\.h5')

def main(args):
    print(args)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('dir_in', metavar='DIR_IN', help='directory with raw files')
    main(ap.parse_args())
