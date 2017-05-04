FROM ubuntu
MAINTAINER Matus Tejiscak

# This builds on the Dockerfile here
# https://github.com/adokter/vol2bird/blob/master/docker/Dockerfile
# 
# but includes improvements to libraries (rave)
# and some extra functionality (data merging)

# this install Python, which we need for the merge script
RUN apt-get update && apt-get install --no-install-recommends -y libconfuse-dev \
    libhdf5-dev gcc make zlib1g-dev python python-dev python-numpy libproj-dev flex file \
    && apt-get install -y git && apt-get install -y libgsl-dev && apt-get install -y libbz2-dev

RUN git clone git://git.baltrad.eu/hlhdf.git \
    && cd hlhdf \
    && ./configure \
        --prefix=/opt/radar \
        --with-hdf5=/usr/include/hdf5/serial,/usr/lib/x86_64-linux-gnu/hdf5/serial \
    && make && make install && cd .. && rm -rf hlhdf

# RAVE is taken from my repository
# (contains the CMT fix, which enables merging the  BE/Jabbeke data)
RUN git clone https://github.com/ziman/rave \
    && cd rave && ./configure --prefix=/opt/radar/rave --with-hlhdf=/opt/radar \
    && make && make install && cd .. && rm -rf rave

RUN git clone https://github.com/adokter/rsl.git && cd rsl \
    && cd decode_ar2v && ./configure --prefix=/usr && make && make install && cd .. \
    && ./configure --prefix=/opt/radar/rsl \
    && make AUTOCONF=: AUTOHEADER=: AUTOMAKE=: ACLOCAL=: \
    && make install AUTOCONF=: AUTOHEADER=: AUTOMAKE=: ACLOCAL=: \
    && cd .. && rm -rf rsl

RUN git clone https://github.com/ziman/vol2bird.git \
    && cd vol2bird \
    && git checkout opts-conf-env \
    && ./configure \
        --prefix=/opt/radar/vol2bird \
        --with-rave=/opt/radar/rave \
        --with-rsl=/opt/radar/rsl \
        --with-gsl=/usr/include/gsl,/usr/lib/x86_64-linux-gnu \
    && make && make install && cd .. && rm -rf vol2bird

# clean up
# what needs to stay: numpy, python
RUN apt-get remove -y git gcc make -y python-dev flex \
    && apt-get clean && apt -y autoremove && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN mkdir -p /opt/radar/baltrad-merge
COPY src/* /opt/radar/baltrad-merge/

CMD /opt/radar/baltrad-merge/merge.sh
