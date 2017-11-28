#!/usr/bin/env python3

import os
import h5py
import argparse
import sqlite3
import logging
from os.path import join as pjoin

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

def main_add(args, db):
    def process_file(root, fname):
        log.debug(fname)
        with h5py.File(fname, 'r') as f:
            print(f)

    def process_files(root, files):
        db.executemany('''
            insert into files (path, country, radar, ftype, angle, ts, quantities, ts_extra)
            values (?, ?, ?, ?, ?, ?, ?, ?)
        ''', [process_file(root, fname) for fname in files])

    def browse(root, dname):
        log.debug(dname)

        with os.scandir(dname) as it:
            dirs = []
            files = []

            for entry in it:
                if entry.is_dir():
                    dirs.append(entry.path)
                elif entry.path.endswith('.h5'):
                    files.append(entry.path)

            if files:
                log.info('%s: %d files' % (dname, len(files)))
                process_files(root, files)

            for dname in dirs:
                browse(root, dname)

    browse(args.dirname, args.dirname)

def main_query(args, db):
    pass

def main(args):
    if not args.action:
        return

    db = sqlite3.connect(args.db)
    args.func(args, db)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-d', '--db', default='db.sqlite3')

    subp = ap.add_subparsers(dest='action')

    add = subp.add_parser('add', help='add files from directory hierarchy')
    add.add_argument('dirname', help='root of the directory hierarchy')
    add.set_defaults(func=main_add)

    query = subp.add_parser('query', help='list files from index')
    query.add_argument('query', help='SQL query')
    query.set_defaults(func=main_query)

    main(ap.parse_args())
