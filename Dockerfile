ARG XCUBE_HUB_DOCKER_BASE_VERSION=latest

FROM quay.io/bcdev/miniconda3:latest

ARG XCUBE_VIEWER_VERSION=0.4.2
ARG XCUBE_USER_NAME=xcube
ENV XCUBE_HUB_DOCKER_BASE_VERSION=latest
ENV XCUBE_HUB_VERSION=1.0.14.dev1
ENV XCUBE_API_UWSGI_INI_PATH="/home/${XCUBE_USER_NAME}/xcube_hub/resources/uwsgi.yaml"

LABEL maintainer="helge.dzierzon@brockmann-consult.de"
LABEL name="xcube hub service"
LABEL xcubehub_base_version=${XCUBE_HUB_DOCKER_BASE_VERSION}
LABEL xcubehub_version=${XCUBE_HUB_VERSION}

USER root
SHELL ["/bin/bash", "-c"]
RUN useradd -u 1000 -g 100 -ms /bin/bash ${XCUBE_USER_NAME}
RUN chown -R ${XCUBE_USER_NAME}.users /opt/conda

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get -y install curl unzip build-essential iputils-ping vim
RUN mkdir /var/log/uwsgi && chown 1000.users /var/log/uwsgi

RUN conda update -n base conda && conda init
RUN conda install -n base -y anaconda-client
RUN conda install -n base -y -c conda-forge mamba

USER ${XCUBE_USER_NAME}

WORKDIR /home/${XCUBE_USER_NAME}

ADD --chown=1000:100 ./ .

RUN mamba env create
RUN pip install -e .
