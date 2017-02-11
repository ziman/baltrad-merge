#!/bin/bash

# mac os x doesn't have a native realpath(1)
realpath() {
    [[ $1 = /* ]] && echo "$1" || echo "$PWD/${1#./}"
}

recurse() {
    local run_sh="$1"
    local dir_in="$2"
    local dir_out="$3"
    local dir_work="$4"

    cd "$dir_in"
    echo "* $dir_in"

    if ls *.h5 &>/dev/null; then
        mkdir -p "$dir_out"
        "$run_sh" "$dir_in" "$dir_out" "$dir_work"
    fi

    for subdir in */; do
        if [ -d "$subdir" ]; then
            recurse "$run_sh" "$dir_in/$subdir" "$dir_out/$subdir" "$dir_work"
        fi
    done
}

if [ -z "$3" ]; then
    echo "usage: $0 INPUT_DIR OUTPUT_DIR WORK_DIR" >&2
    exit 1
fi

recurse "$(dirname "$(realpath "$0")")/run.sh" "$(realpath "$1")" "$(realpath "$2")" "$(realpath "$3")"
