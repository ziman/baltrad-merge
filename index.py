#!/usr/bin/env python3

import os
import argparse
import sqlite3
import logging
from os.path import join as pjoin

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

def main_add(args, db):
    def process_files(root, files):
        values = []
        db.executemany('''
            insert into files (path, country, radar, ftype, angle, ts, quantities, ts_extra)
            values (?, ?, ?, ?, ?, ?, ?, ?)
        ''', values)

    def browse(root, dname):
        with os.scandir(dname) as it:
            dirs = []
            files = []

            for entry in it:
                if entry.is_dir():
                    dirs.append(entry.path)
                else:
                    files.append(entry.path)

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
