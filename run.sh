#!/bin/bash

# mac os x doesn't have a native realpath(1)
realpath() {
    [[ $1 = /* ]] && echo "$1" || echo "$PWD/${1#./}"
}

if [ -z "$3" ]; then
    echo "usage: $0 INPUT_DIR OUTPUT_DIR WORK_DIR" >&2
    exit 1
fi

dir_in="$(realpath "$1")"
shift

dir_out="$(realpath "$1")"
shift

dir_work="$(realpath "$1")"
shift

docker run \
    -u "$(id -u)" \
    -v "$dir_in":"/data/in" \
    -v "$dir_out":"/data/out" \
    -v "$dir_work":"/data/work" \
    ziman/baltrad-merge \
    "$@"

# vim: ts=4 sts=4 sw=4 et
