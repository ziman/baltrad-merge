#!/bin/bash

uid_no="$1"
dir_in="$2"
dir_out="$3"
dir_work="$4"

# let's see if we can get away without this
#useradd -u "$uid_no" "baltrad"

LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/opt/radar/lib"
LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/opt/radar/rave/lib"
LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/opt/radar/rave/Lib"
LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/opt/radar/rsl/lib"
LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/opt/radar/vol2bird/lib"
LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/usr/lib/x86_64-linux-gnu"
export LD_LIBRARY_PATH

PATH="${PATH}:/opt/radar/vol2bird/bin"
PATH="${PATH}:/opt/radar/baltrad-merge"
export PATH

PYTHONPATH="${PYTHONPATH}:/opt/radar/vol2bird/share/vol2bird"
PYTHONPATH="${PYTHONPATH}:/opt/radar/vol2bird/share/vol2bird/pyvol2bird"
PYTHONPATH="${PYTHONPATH}:/opt/radar/rave/Lib"
export PYTHONPATH

# 525600 minutes = 1 year
exec sudo -u "#$uid_no" \
    /opt/radar/baltrad-merge/generate_profiles.py \
    --merge-files /opt/radar/rave/bin/merge_files \
    --scans2pvol /opt/radar/baltrad-merge/Scans2Pvol.py \
    --vol2bird /opt/radar/vol2bird/bin/vol2bird \
    --age-limit 525600 \
    -i "${dir_in:-/data/in}" \
    -o "${dir_out:-/data/out}" \
    -w "${dir_work:-/data/work}"

# vim: ts=4 sts=4 sw=4 et
