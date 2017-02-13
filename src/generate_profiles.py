#!/usr/bin/env python2
#
# The Baltrad server has Python 2.6.6.

try:
    import argparse
except ImportError:
    import os
    os.system('pip install --user argparse')
    print('\n\n** installed dependency: argparse\n   please rerun the script')

import os
import re
import sys
import time
import shutil
import datetime
import argparse
import logging
import collections
import subprocess
from os.path import join as pjoin

logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s %(message)s',
)
log = logging.getLogger('generate_profiles')

FileInfo = collections.namedtuple('FileInfo', 'path radar ftype angle ts quantities ts_extra')
REGEX_FI = re.compile(r'(.....)_(scan|pvol)(?:_(-?[0-9.]+))?_(\d{8}T\d{4}Z)(?:_(0x[0-9a-f]+))?(?:_(\d+))?\.h5')

class ProgressMeter(object):
    def human(self, sec):
        result = ""

        if sec > 86400:
            result += "%dd" % (sec / 86400)
            sec %= 86400

        if sec > 3600:
            result += "%dh" % (sec / 3600)
            sec %= 3600

        if sec > 60:
            result += "%dm" % (sec / 60)
            sec %= 60

        if sec > 0:
            result += "%ds" % sec

        return result

    def __init__(self, totalItemCount):
        self.totalItemCount = totalItemCount
        self.startTime = time.time()
        self.secondsElapsed = 0.0
        self.itemsDone = 0
        self.last_print = None
        
    def nextItem(self):
        self.secondsElapsed = int(time.time() - self.startTime)
        self.itemsDone += 1

    def secs_since_print(self, seconds):
        if self.last_print is not None:
            return (self.secondsElapsed - self.last_print) >= seconds
        else:
            return True

    def __str__(self):
        self.last_print = self.secondsElapsed

        es = self.secondsElapsed % 60
        em = self.secondsElapsed / 60
        
        if self.itemsDone:
            eta = self.secondsElapsed * (self.totalItemCount - self.itemsDone) / self.itemsDone
        else:
            eta = 0
        
        pp = 100*self.itemsDone / self.totalItemCount
        
        return "[%d/%d, %s, %.1f/s, %d%%, ETA %s]" % (
            self.itemsDone,
            self.totalItemCount,
            self.human(self.secondsElapsed),
            float(self.itemsDone) / (self.secondsElapsed or 1),
            pp,
            self.human(eta),
        )

class ProgramError(Exception):
    pass

def check_output(cmd):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, _ = p.communicate()
    retcode = p.wait()
    return retcode, stdout

def mktmp_linked(args, tmp_name, files):
    dirname = pjoin(args.dirname_work, tmp_name + str(os.getpid()))
    dirname_src = pjoin(dirname, 'src')
    dirname_dst = pjoin(dirname, 'dst')

    os.makedirs(dirname_src)
    os.makedirs(dirname_dst)

    # create symlinks to inputs
    for info in files:
        os.symlink(os.path.abspath(info.path), pjoin(dirname_src, os.path.basename(info.path)))

    return dirname_src, dirname_dst

def rmtmp_linked(args, tmp_name):
    dirname = pjoin(args.dirname_work, tmp_name + str(os.getpid()))
    shutil.rmtree(dirname)

def merge_volumes(args, files, fname_out):
    by_quantity = collections.defaultdict(list)
    for info in files:
        by_quantity[info.quantities].append(info)

    # XXX TODO
    # we (arbitrarily) select the first polar volume in each group for merging
    merge_inputs = [min(files, key=lambda f: f.ts_extra) for files in by_quantity.itervalues()]

    if len(merge_inputs) == 1:
        info = merge_inputs[0]
        log.info('singleton group, just copying file: ' + info.path)
        shutil.copy(info.path, fname_out)
        return

    # there should be no empty datasets after this point
    assert merge_inputs

    # create temporary dirs
    dir_src, dir_dst = mktmp_linked(args, 'merge', merge_inputs)

    # merge!
    try:
        subprocess.check_call([
            'python',
            args.merge_files,
            '--indir', dir_src,
            '--outdir', dir_dst,
            '--type', 'pvol'
        ])

        # move the result out
        for fname in os.listdir(dir_dst):
            shutil.move(
                pjoin(dir_dst, fname),
                fname_out
            )
    except subprocess.CalledProcessError as e:
        log.warn('merge_files failed: %s' % e)

    # clean up
    rmtmp_linked(args, 'merge')

def merge_scans(args, files, fname_out):
    dir_src, dir_dst = mktmp_linked(args, 'merge_scans', files)

    cwd = os.getcwd()
    scans2pvol_abs = os.path.abspath(args.scans2pvol)
    fname_out_abs = os.path.abspath(fname_out)

    try:
        os.chdir(dir_src)
        files_before = set(os.listdir('.'))

        subprocess.check_call(['python', scans2pvol_abs])

        # move the result out
        for fname in os.listdir('.'):
            if fname in files_before:
                continue

            shutil.move(fname, fname_out_abs)
    except subprocess.CalledProcessError as e:
        log.warn('scans2pvol failed: %s' % e)
    finally:
        os.chdir(cwd)

    # clean up
    rmtmp_linked(args, 'merge_scans')

def merge_group(args, files, fname_out):
    file_names = [os.path.basename(f.path) for f in files]

    file_types = list(sorted(set(info.ftype for info in files)))

    if file_types == ['pvol']:
        merge_volumes(args, [info for info in files if not info.ts_extra], fname_out)
    elif file_types == ['scan']:
        merge_scans(args, files, fname_out)
    elif file_types == ['pvol', 'scan']:
        # if we've got both, work from the scans
        merge_scans(args, [i for i in files if i.ftype == 'scan'], fname_out)
    else:
        raise ProgramError('unrecognised file types "%s" in %s ' % (file_types, file_names))

def make_bird_profile(args, fname_pvol, fname_bird_profile):
    retcode, output = check_output([
        args.vol2bird,
        fname_pvol,
        fname_bird_profile
    ])

    if retcode != 0:
        log.debug(output)
        log.warn('vol2bird failed')

def process_files(args, files):
    grouped = collections.defaultdict(list)
    for info in files:
        grouped[(info.radar, info.ts)].append(info)

    if args.keep_merged:
        dirname_merged = pjoin(args.dirname_out, 'merged')
    else:
        dirname_merged = pjoin(args.dirname_work, 'merged')

    if not os.path.exists(dirname_merged):
        os.makedirs(dirname_merged)

    pm = ProgressMeter(len(grouped))
    for (radar, ts), group_files in sorted(grouped.items(), key=lambda x: x[0]):
        base_filename = lambda ftype: \
            make_filename(FileInfo(
                path=None,
                radar=radar,
                ftype=ftype,
                angle=None,
                ts=ts,
                quantities=None,
                ts_extra=None,
            ))

        fname_merged = pjoin(dirname_merged, base_filename('pvol'))
        fname_bird_profile = pjoin(args.dirname_out, base_filename('vp'))

        merge_group(args, group_files, fname_merged)
        make_bird_profile(args, fname_merged, fname_bird_profile)

        pm.nextItem()
        log.info('%s %s %s' % (pm, radar, ts.strftime('%Y-%m-%d %H:%M')))

def parse_filename(path, match):
    return FileInfo(
        path=path,
        radar=match.group(1),
        ftype=match.group(2),
        angle=match.group(3) and float(match.group(3)),
        ts=datetime.datetime.strptime(match.group(4), '%Y%m%dT%H%MZ'),
        quantities=match.group(5),
        ts_extra=match.group(6) and datetime.datetime.fromtimestamp(
            int(float(match.group(6)) / 100)
        ),
    )

def make_filename(info):
    fields = [info.radar, info.ftype]

    if info.angle:
        fields.append('%f' % info.angle)

    fields.append(
        info.ts.strftime('%Y%m%dT%H%MZ')
    )

    if info.quantities:
        fields.append(info.quantities)

    if info.ts_extra:
        fields.append('%s' % info.ts_extra.strftime('%s'))

    return '_'.join(fields) + '.h5'

def is_raw_data(info):
    if info.ftype == 'pvol':
        return bool(info.quantities) and not bool(info.ts_extra)
    elif info.ftype == 'scan':
        return not bool(info.ts_extra)
    else:
        raise ProgramError('unknown file type "%s": %s' % (info.ftype, info.path))

def main(args):
    files_in = []
    for fname in os.listdir(args.dirname_in):
        match = REGEX_FI.match(fname)
        if not match:
            log.warn('skipping unrecognised filename: ' + fname)
            continue

        info = parse_filename(
            pjoin(args.dirname_in, fname),
            match
        )

        files_in.append(info)

    # filter out files that are too old
    thresh = datetime.datetime.now() - datetime.timedelta(minutes=args.age_limit)
    files_in = [
        info
        for info in files_in
        if info.ts >= thresh    # recent enough
           and is_raw_data(info)
    ]

    if not os.path.exists(args.dirname_work):
        os.makedirs(args.dirname_work)

    process_files(args, files_in)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()

    ap.add_argument('-a', '--age-limit', type=int, default=60, metavar='MINUTES',
        help='skip files older than MINUTES ago [%(default)s min]')
    ap.add_argument('--merge-files', default='merge_files', metavar='PATH',
        help='path to merge_files')
    ap.add_argument('--scans2pvol', default='Scans2Pvol.py', metavar='PATH',
        help='path to Scans2Pvol.py')
    ap.add_argument('--vol2bird', default='vol2bird', metavar='PATH',
        help='path to vol2bird')
    ap.add_argument('--keep-merged', default=False, action='store_true',
        help='add merged files (input to vol2bird) to the output directory')

    rn = ap.add_argument_group('required named arguments')
    rn.add_argument('-i', dest='dirname_in', required=True, metavar='PATH',
        help='directory to read raw data from')
    rn.add_argument('-o', dest='dirname_out', required=True, metavar='PATH',
        help='directory to write bird profiles to')
    ap.add_argument('-w', dest='dirname_work', required=True, metavar='PATH',
        help='directory for intermediate files')

    main(ap.parse_args())
