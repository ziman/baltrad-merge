#!/usr/bin/env python3

import argparse

def main(args):
    print(args)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('dir_in', help="Input directory (raw files)")
    ap.add_argument('dir_out', help="Output directory (merged files + bird profiles)")
    ap.add_argument('dir_work', help="Working directory (temporary files)")

    ap.add_argument('--date-from', metavar="YYYY/MM/DD")
    ap.add_argument('--date-to', metavar="YYYY/MM/DD")

    main(ap.parse_args())
