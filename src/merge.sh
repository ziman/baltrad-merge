#!/bin/bash

export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/opt/radar/lib:/opt/radar/rave/lib:/opt/radar/rsl/lib:/opt/radar/vol2bird/lib:/usr/lib/x86_64-linux-gnu
export PATH=${PATH}:/opt/radar/vol2bird/bin:/opt/radar/baltrad-merge


# 525600 minutes = 1 year
exec /opt/radar/baltrad-merge/generate_profiles.py \
    --merge-files /opt/radar/rave/bin/merge_files \
    --scans2pvol /opt/radar/baltrad-merge/Scans2Pvol.py \
    --vol2bird /optc/radar/vol2bird/bin/vol2bird \
    --age-limit 525600 \
    -i "${1:-/data/in}" \
    -o "${2:-/data/out}" \
    -w "${3:-/data/work}"
