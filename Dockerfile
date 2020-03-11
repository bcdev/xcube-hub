ARG XCUBE_VERSION=0.3.0

FROM quay.io/bcdev/xcube-python-deps:${XCUBE_VERSION}

ARG XCUBE_USER_NAME=xcube

LABEL version=0.1.0.dev0
LABEL xcube_version=XCUBE_VERSION
LABEL name=xcube
LABEL maintainer=helge.dzierzon@brockmann-consult.de

SHELL ["/bin/bash", "-c"]

RUN mkdir /home/xcube/xcube-gen
WORKDIR /home/xcube/xcube-gen

ADD --chown=1000:1000 environment.yml environment.yml
RUN source activate xcube && conda env update -n xcube

ADD --chown=1000:1000 ./ .
RUN source activate xcube && python setup.py install

RUN git clone https://github.com/dcs4cop/xcube-sh /home/${XCUBE_USER_NAME}/xcube-sh
WORKDIR /home/${XCUBE_USER_NAME}/xcube-sh
RUN source activate xcube && python setup.py install

WORKDIR /home/${XCUBE_USER_NAME}

ENTRYPOINT ["bash", "-c"]