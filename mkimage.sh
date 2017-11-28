#!/bin/bash

container_tag="$1"

docker build -t baltrad-merge-uncompacted"$container_tag" .

container_id=$(docker run -d baltrad-merge-uncompacted"$container_tag" /bin/bash)

# export into TAR, import the TAR
# this is especially important to squash the layers
# where we installed something and then removed it
#
# the default command CMD needs to be put back in
docker export $container_id \
    | docker import \
        --change='CMD /opt/radar/baltrad-merge/merge.sh' \
        /dev/stdin \
        ziman/baltrad-merge"$container_tag"

docker stop $container_id
docker rm $container_id
