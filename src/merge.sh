#!/bin/bash

exec /opt/radar/baltrad-merge/generate_profiles.py \
    --merge-files /opt/radar/rave/bin/merge_files \
    --scans2pvol /opt/radar/baltrad-merge/Scans2Pvol.py \
    --vol2bird /optc/radar/vol2bird/bin/vol2bird \
    -i "${1:-/data/in}" \
    -o "${2:-/data/out}" \
    -w "${3:-/data/work}"
