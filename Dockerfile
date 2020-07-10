ARG XCUBE_VERSION=0.5.0

FROM quay.io/bcdev/xcube-python-base:${XCUBE_VERSION}

ARG XCUBE_VERSION=0.5.0
ARG XCUBE_VIEWER_VERSION=0.4.2
ARG XCUBE_GEN_VERSION=1.0.8
ARG XCUBE_USER_NAME=xcube
ENV XCUBE_API_UWSGI_INI_PATH="/home/${XCUBE_USER_NAME}/xcube_gen/resources/uwsgi.yaml"

LABEL maintainer="helge.dzierzon@brockmann-consult.de"
LABEL name="xcube gen service"
LABEL xcube_version=${XCUBE_VERSION}
LABEL xcube_gen_version=${XCUBE_GEN_VERSION}

USER root
RUN apt-get -y update && apt-get -y install curl unzip build-essential iputils-ping vim
RUN mkdir /var/log/uwsgi && chown 1000.1000 /var/log/uwsgi

USER ${XCUBE_USER_NAME}

RUN conda install -c conda-forge -n base mamba

WORKDIR /home/${XCUBE_USER_NAME}
ADD --chown=1000:1000 environment.yml environment.yml

RUN mamba env create

ADD --chown=1000:1000 ./ .
RUN source activate xcube-gen && pip install redis pydevd-pycharm~=201.7846.76
RUN source activate xcube-gen && pip install -e .

COPY --from=quay.io/bcdev/xcube-viewer:0.4.2 /usr/src/app/build /home/${XCUBE_USER_NAME}/viewer

EXPOSE 5000
EXPOSE 5050

# CMD ["/bin/bash", "-c", "source activate xcube-gen && xcube-genserv start -p 8000 -a 0.0.0.0"]
CMD ["/bin/bash", "-c", "source activate xcube-gen && uwsgi --static-index /viewer/index.html --yaml ${XCUBE_API_UWSGI_INI_PATH}"]
