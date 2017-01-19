FROM adokter/vol2bird
MAINTAINER Matus Tejiscak

RUN apt-get update && apt-get install -y git python

RUN git clone https://github.com/ziman/baltrad-merge \
    && mkdir -p /opt/radar/baltrad-merge \
    && cp \
        baltrad-merge/src/generate_profiles.py \
        baltrad-merge/src/Scans2Pvol.py \
        /opt/radar/baltrad-merge \
    && rm -rf baltrad-merge

RUN apt-get remove -y git \
    && apt-get clean && apt -y autoremove && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

CMD /opt/radar/baltrad-merge/generate_profiles.py \
    --merge-files /opt/radar/rave/bin/merge_files \
    --scans2pvol /opt/radar/baltrad-merge/Scans2Pvol.py \
    --vol2bird /optc/radar/vol2bird/bin/vol2bird \
    -i /data/in \
    -o /data/out \
    -w /data/work
