#!/bin/bash

if [ -z "$3" ]; then
    echo "usage: $0 INPUT_DIR OUTPUT_DIR WORK_DIR" >&2
    exit 1
fi

dir_in="$(realpath "$1")"
dir_out="$(realpath "$2")"
dir_work="$(realpath "$3")"
shift
shift
shift

docker run \
    -v "$dir_in":"/data/in" \
    -v "$dir_out":"/data/out" \
    -v "$dir_work":"/data/work" \
    ziman/baltrad-merge \
    "$@"
