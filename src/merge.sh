#!/bin/bash

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

export OPTIONS_CONF="/data/etc/options.conf"

data_in="$1"
data_out="$2"
data_work="$3"
shift; shift; shift

# 525600 minutes = 1 year
exec /opt/radar/baltrad-merge/generate_profiles.py \
    --merge-files /opt/radar/rave/bin/merge_files \
    --scans2pvol /opt/radar/baltrad-merge/Scans2Pvol.py \
    --vol2bird /opt/radar/vol2bird/bin/vol2bird \
    --age-limit 525600 \
    --keep-merged \
    -i "$data_in" \
    -o "$data_out" \
    -w "$data_work" \
    "$@"
