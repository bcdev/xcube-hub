FROM continuumio/miniconda3

ARG XCUBE_VERSION=0.3.0.dev0
LABEL version=XCUBE_VERSION
LABEL name=xcube
LABEL maintainer=helge.dzierzon@brockmann-consult.de

SHELL ["/bin/bash", "-c"]

WORKDIR /xcube-gen
ADD ./ .

RUN source activate base && conda env create
RUN source activate base && python setup.py install

ENTRYPOINT ["bash", "-c"]