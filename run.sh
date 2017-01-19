#!/bin/bash

if [ -z "$3" ]; then
    echo "usage: $0 INPUT_DIR OUTPUT_DIR WORK_DIR" >&2
    exit 1
fi

docker run \
    -v "$1":"/data/in" \
    -v "$2":"/data/out" \
    -v "$3":"/data/work" \
    baltrad-merge
