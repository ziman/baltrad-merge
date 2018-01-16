#!/usr/bin/env python3

import re
import os
import sys
import sqlite3
import logging
from datetime import datetime

log = logging.getLogger(__name__)

def parse_ts_range(s):
    match = re.match(r'(\d{6})T(\d{4})Z?-(\d{6})T(\d{4})Z?', s)
    if match:
        return (
            datetime.strptime(match.group(1) + match.group(2), '%y%m%d%H%M'),
            datetime.strptime(match.group(3) + match.group(4), '%y%m%d%H%M'),
        )

    match = re.match(r'(\d{8})T(\d{4})Z?-(\d{8})T(\d{4})Z?', s)
    if match:
        return (
            datetime.strptime(match.group(1) + match.group(2), '%Y%m%d%H%M'),
            datetime.strptime(match.group(3) + match.group(4), '%Y%m%d%H%M'),
        )

    return None

def parse_radar(s):
    match = re.match(r'[a-z]{5}', s)
    if not match:
        return None

    return s

def list_files(ts_ranges, radars):
    sql_code = """
        SELECT dir_rel, name
        FROM files
        WHERE quantities != ""
    """
    sql_args = []

    if radars:
        sql_code += " AND (" + " OR ".join("radar = ?" for _ in radars) + ")"
        sql_args.extend(radars)

    for lo, hi in ts_ranges:
        sql_code += " AND ts BETWEEN ? AND ?"
        sql_args += [lo, hi]

    db = sqlite3.connect('db.sqlite3')
    c = db.cursor()
    c.execute(sql_code, tuple(sql_args))

    while True:
        rows = c.fetchmany()
        if not rows:
            break

        for dir_rel, name in rows:
            print(os.path.join(dir_rel, name))

def main(args):
    ts_ranges = set()
    radars = set()

    for spec in args:
        ts_range = parse_ts_range(spec)
        if ts_range:
            ts_ranges.add(ts_range)
            continue

        radar = parse_radar(spec)
        if radar:
            radars.add(radar)
            continue

        raise Exception("don't know what to do with: %s" % spec)

    log.debug('selected date ranges:', ts_ranges)
    log.debug('selected radars:', radars)

    list_files(ts_ranges, list(radars))

if __name__ == '__main__':
    main(sys.argv[1:])
