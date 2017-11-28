#!/usr/bin/env python2

import os
import logging
import argparse
import datetime
import subprocess
from os.path import join as pjoin

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

def recurse(args, dir_in, dir_out, hier_date):
    # if dates have been bounded,
    # then we need to look at the date deduced from directory hierarchy
    if (args.date_from_ts or args.date_to_ts) and len(hier_date) == 3:
        hier_ts = datetime.datetime.strptime('/'.join(hier_date), '%Y/%m/%d')

        if args.date_from_ts and hier_ts < args.date_from_ts:
            # timestamp too low
            return

        if args.date_to_ts and hier_ts > args.date_to_ts:
            # timestamp too high
            # note that --date-to is meant to include the whole day
            # which does not cause problems if we compare only dates
            # (i.e. midnights in terms of timestamps)
            return

    log.info(dir_in)

    try:
        os.makedirs(dir_out)
    except OSError:
        pass  # the dir probably just exists

    h5_files_present = False
    for fname in sorted(os.listdir(dir_in)):
        if fname.startswith('.'):
            # skip hidden files
            continue

        fname_in = pjoin(dir_in, fname)
        if os.path.isdir(fname_in):
            recurse(args, fname_in, pjoin(dir_out, fname), hier_date + [fname])
            continue

        if fname.endswith('.h5'):
            h5_files_present = True

    if not h5_files_present:
        # we recursed into subdirs
        # nothing more to do here
        return

    # h5 files present -- run `run.sh`
    cmd = ['./run.sh', '-c', args.container_name, dir_in, dir_out, args.dir_work]
    if args.radar:
        cmd += ['--radar', args.radar]

    if args.date_from:
        cmd += ['--date-from', args.date_from]

    if args.date_to:
        cmd += ['--date-to', args.date_to]

    subprocess.check_call(cmd)

def main(args):
    DATE_FMT = '%Y/%m/%d'
    args.date_from_ts = args.date_from and datetime.datetime.strptime(args.date_from.strip('/'), DATE_FMT)
    args.date_to_ts = args.date_to and datetime.datetime.strptime(args.date_to.strip('/'), DATE_FMT)

    recurse(args, args.dir_in, args.dir_out, [])    

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('dir_in', help="Input directory (raw files)")
    ap.add_argument('dir_out', help="Output directory (merged files + bird profiles)")
    ap.add_argument('dir_work', help="Working directory (temporary files)")

    ap.add_argument('-f', '--date-from', metavar="YYYY/MM/DD")
    ap.add_argument('-t', '--date-to', metavar="YYYY/MM/DD")
    ap.add_argument('-r', '--radar', metavar="CC|CCRRR|REGEX", help="two- or five-letter radar code (2x country + 3x radar)")
    ap.add_argument('-c', '--container-name', metavar='NAME', default='ziman/baltrad-merge',
        help="docker container name to use [%(default)]")

    main(ap.parse_args())
