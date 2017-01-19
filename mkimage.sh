#!/bin/bash

docker build -t baltrad-merge-uncompacted .

container_id=$(docker run -d baltrad-merge-uncompacted /bin/bash)

# export into TAR, import the TAR
# this is especially important to squash the layers
# where we installed something and then removed it
#
# the default command CMD needs to be put back in
docker export $container_id \
    | docker import \
        --change='CMD /opt/radar/baltrad-merge/generate_profiles.py --merge-files /opt/radar/rave/bin/merge_files --scans2pvol /opt/radar/baltrad-merge/Scans2Pvol.py --vol2bird /optc/radar/vol2bird/bin/vol2bird -i /data/in -o /data/out -w /data/work' \
        /dev/stdin \
        ziman/baltrad-merge

docker stop baltrad-merge-uncompacted
docker rm baltrad-merge-uncompacted
