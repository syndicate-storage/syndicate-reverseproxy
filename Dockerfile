# syndicate-reverseproxy
#
# VERSION	1.0

FROM	ubuntu:14.04
MAINTAINER	Illyoung Choi <iychoi@email.arizona.edu>

##############################################
# Setup a Syndicate account
##############################################
ENV HOME /home/syndicate

RUN useradd syndicate && echo 'syndicate:syndicate' | chpasswd && \
    echo "syndicate ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers && \
    mkdir /home/syndicate && \
    chown -R syndicate:syndicate $HOME

ENV USER syndicate
WORKDIR $HOME

##############################################
# Setup packages
##############################################
RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
    apt-get install -y --allow-unauthenticated --no-install-recommends \
    wget python-pip build-essential \
    python python-dev python-pip \
    nginx && \
    apt-get clean autoclean && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt /var/lib/cache /var/lib/log && \
    pip install -v -v greenlet gevent==1.2.2 grequests

COPY start_nginx.sh /usr/bin/
COPY nginx.conf /etc/nginx/
COPY sdm_reverseproxy.conf.template /tmp/sdm_reverseproxy.conf.template
COPY origin_server_setter.py /usr/bin/
COPY configure_nginx.py /usr/bin/

RUN chmod 777 /usr/bin/start_nginx.sh && \
    chmod 755 /usr/bin/origin_server_setter.py && \
    chmod 755 /usr/bin/configure_nginx.py

EXPOSE 31010/tcp

CMD bash -C '/usr/bin/start_nginx.sh'
