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
dir_out="$(realpath "$2")"
dir_work="$(realpath "$3")"
shift
shift
shift

dir_etc="$(dirname "$(realpath "$0")")"

docker run \
    --rm \
    -u "$(id -u)" \
    -v "$dir_in":"/data/in" \
    -v "$dir_out":"/data/out" \
    -v "$dir_work":"/data/work" \
    -v "$dir_etc":"/data/etc" \
    ziman/baltrad-merge \
    "$@"
