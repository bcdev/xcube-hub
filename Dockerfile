ARG XCUBE_VERSION=0.4.2

FROM quay.io/bcdev/xcube-python-base:${XCUBE_VERSION}

ARG XCUBE_VERSION=0.4.2
ARG XCUBE_GEN_VERSION=1.0.5
ARG XCUBE_USER_NAME=xcube
ARG XCUBE_API_UWSGI_INI_PATH="/home/${XCUBE_USER_NAME}/xcube_gen/resources/uwsgi.ini"

LABEL maintainer="helge.dzierzon@brockmann-consult.de"
LABEL name="xcube python dependencies"
LABEL xcube_version=${XCUBE_VERSION}
LABEL xcube_gen_version=${XCUBE_GEN_VERSION}

USER root
RUN apt-get -y update && apt-get -y install curl unzip build-essential iputils-ping vim

USER ${XCUBE_USER_NAME}

RUN conda install -c conda-forge -n base mamba

WORKDIR /home/${XCUBE_USER_NAME}
ADD --chown=1000:1000 environment.yml environment.yml
RUN mamba env create

ADD --chown=1000:1000 ./ .
RUN source activate xcube-gen && pip install redis
RUN source activate xcube-gen && pip install -e .

COPY --from=quay.io/bcdev/xcube-viewer:latest /usr/src/app/build ./viewer

EXPOSE 8000
EXPOSE 5050

CMD ["/bin/bash", "-c", "source activate xcube-gen && uwsgi --yaml /home/xcube/xcube_gen/resources/uwsgi.ini"]
