#!/usr/bin/env python3

import os
import argparse
import sqlite3

def main(args):
    db = sqlite3.connect(args.db)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-d', '--db', default='db.sqlite3')
    main(ap.parse_args())
