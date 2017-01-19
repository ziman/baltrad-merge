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
        --change='CMD /opt/radar/baltrad-merge/merge.sh' \
        /dev/stdin \
        ziman/baltrad-merge

docker stop $container_id
docker rm $container_id
