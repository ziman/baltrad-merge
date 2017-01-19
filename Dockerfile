FROM adokter/vol2bird
MAINTAINER Matus Tejiscak

RUN apt-get update && apt-get install -y git python

RUN git clone https://github.com/ziman/baltrad-merge \
    && mkdir -p /opt/radar/baltrad-merge \
    && cp \
        baltrad-merge/src/generate_profiles.py \
        baltrad-merge/src/Scans2Pvol.py \
        /opt/radar/baltrad-merge \
    && cp \
        baltrad-merge/src/merge.sh \
        /usr/local/bin \
    && rm -rf baltrad-merge

RUN apt-get remove -y git \
    && apt-get clean && apt -y autoremove && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

CMD merge.sh
