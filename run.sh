#!/bin/bash

# mac os x doesn't have a native realpath(1)
realpath() {
    [[ $1 = /* ]] && echo "$1" || echo "$PWD/${1#./}"
}

container_name="ziman/baltrad-merge"
if [ "$1" = "-c" ]; then
    container_name="$2"
    shift
    shift
fi

if [ -z "$3" ] || [ -z "$2" ]; then
    echo "usage: $0 [-c CONTAINER_NAME=ziman/baltrad-merge] INPUT_DIR OUTPUT_DIR WORK_DIR" >&2
    exit 1
fi

dir_in="$(realpath "$1")"
dir_out="$(realpath "$2")"
dir_work="$(realpath "$3")"
shift
shift
shift

dir_etc="$(dirname "$(realpath "$0")")/etc"

docker run \
    --rm \
    -u "$(id -u)" \
    -v "$dir_in":"/data/in" \
    -v "$dir_out":"/data/out" \
    -v "$dir_work":"/data/work" \
    -v "$dir_etc":"/data/etc" \
    "$container_name" \
    /opt/radar/baltrad-merge/merge.sh \
        '/data/in' '/data/out' '/data/work' \
        "$@"
