#!/usr/bin/env python3

import os
import re
import sqlite3
import argparse
import logging
import collections
import datetime

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

FileInfo = collections.namedtuple('FileInfo', 'radar ftype angle ts quantities ts_extra')
REGEX_FI = re.compile(r'(.....)_(scan|pvol)(?:_(-?[0-9.]+))?_(\d{8}T\d{4}Z)(?:_(0x[0-9a-f]+))?(?:_(\d+))?\.h5')

def parse_filename(basename):
    match = REGEX_FI.match(basename)
    return FileInfo(
        radar=match.group(1),
        ftype=match.group(2),
        angle=match.group(3) and float(match.group(3)),
        ts=datetime.datetime.strptime(match.group(4), '%Y%m%dT%H%MZ'),
        quantities=match.group(5) and int(match.group(5), 16),
        ts_extra=match.group(6) and datetime.datetime.fromtimestamp(
            int(float(match.group(6)) / 100)
        ),
    )

def add_path(args, db, root_dir_abs):
    def add_directory(source_id, path_abs, path_rel):
        log.info(path_abs)
        with os.scandir(path_abs) as entries:
            for entry in entries:
                if entry.is_dir():
                    add_directory(
                        source_id,
                        os.path.join(path_abs, entry.name),
                        os.path.join(path_rel, entry.name),
                    )
                else:
                    info = parse_filename(entry.name)
                    db.execute("""
                        INSERT INTO files (
                            dir_rel, name, 
                            radar, ftype, angle, ts, quantities, ts_extra,
                            source_id
                        )
                        VALUES (?, ?,
                            ?, ?, ?, ?, ?, ?,
                            ?)
                    """, (path_rel, entry.name,
                        info.radar, info.ftype, info.angle, info.ts,
                        info.quantities, info.ts_extra,
                        source_id
                    ))

    c = db.cursor()
    c.execute("INSERT INTO sources (name, ts) VALUES (?, ?)", (
        args.name or root_dir_abs,
        datetime.datetime.now(),
    ))
    source_id = c.lastrowid

    add_directory(source_id, root_dir_abs, '')

def main(args):
    with sqlite3.connect(args.dbfile) as db:
        if args.add_path:
            add_path(args, db, os.path.abspath(args.add_path))

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('dbfile', metavar='db.sqlite3', help='Database file')
    ap.add_argument('-a', dest='add_path', default=None, metavar='DIRECTORY', help='Add directory')
    ap.add_argument('-n', dest='name', default=None, metavar='DATASET_NAME', help='Name of the dataset')
    main(ap.parse_args())
