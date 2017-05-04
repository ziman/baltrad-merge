#!/usr/bin/env python2

import os
import logging
import argparse
import subprocess
from os.path import join as pjoin

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

def recurse(args, dir_in, dir_out):
    log.info(dir_in)

    try:
        os.makedirs(dir_out)
    except OSError:
        pass  # the dir probably just exists

    h5_files_present = False
    for fname in os.listdir(dir_in):
        fname_in = pjoin(dir_in, fname)
        if os.path.isdir(fname_in):
            recurse(args, fname_in, pjoin(dir_out, fname))
            continue

        if fname.endswith('.h5'):
            h5_files_present = True

    if not h5_files_present:
        # we recursed into subdirs
        # nothing more to do here
        return

    # h5 files present -- run `run.sh`
    cmd = ['./run.sh', dir_in, dir_out, args.dir_work]
    if args.radar:
        cmd += ['--radar', args.radar]

    if args.date_from:
        cmd += ['--date-from', args.date_from]

    if args.date_to:
        cmd += ['--date-to', args.date_to]

    subprocess.check_call(cmd)

def main(args):
    recurse(args, args.dir_in, args.dir_out)    

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('dir_in', help="Input directory (raw files)")
    ap.add_argument('dir_out', help="Output directory (merged files + bird profiles)")
    ap.add_argument('dir_work', help="Working directory (temporary files)")

    ap.add_argument('--date-from', metavar="YYYY/MM/DD")
    ap.add_argument('--date-to', metavar="YYYY/MM/DD")
    ap.add_argument('--radar', metavar="CC|CCRRR", help="two- or five-letter radar code (2x country + 3x radar)")

    main(ap.parse_args())
