ARG XCUBE_VERSION=0.3.0

FROM quay.io/bcdev/xcube-python-deps:${XCUBE_VERSION}

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

ENTRYPOINT ["bash", "-c"]