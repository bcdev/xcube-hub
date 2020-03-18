ARG XCUBE_DOCKER_BASE_VERSION=0.3.0

FROM quay.io/bcdev/xcube-python-base:${XCUBE_DOCKER_BASE_VERSION}

ARG XCUBE_VERSION=0.4.0.dev0
ARG XCUBE_USER_NAME=xcube
ARG XCUBE_GEN_BRANCH=dzelge_xxx_k8s

LABEL maintainer="helge.dzierzon@brockmann-consult.de"
LABEL name="xcube python dependencies"
LABEL xcube_version=${XCUBE_VERSION}
LABEL xcube_gen_branch=${XCUBE_GEN_BRANCH}

USER root
RUN apt-get -y update && apt-get -y install curl unzip

USER ${XCUBE_USER_NAME}

RUN git clone https://github.com/dcs4cop/xcube /home/${XCUBE_USER_NAME}/xcube

WORKDIR /home/${XCUBE_USER_NAME}/xcube
RUN conda env create
RUN source activate xcube && python setup.py develop


WORKDIR /home/${XCUBE_USER_NAME}
ADD --chown=1000:1000 environment.yml environment.yml
RUN conda env update -n xcube
RUN source activate xcube && pip install pydevd-pycharm

ADD --chown=1000:1000 ./ .
RUN source activate xcube && python setup.py develop

#RUN aws sts get-caller-identity
#RUN aws eks update-kubeconfig --region eu-central-1 --name dcfs-xcube-gen-cluster


EXPOSE 8000

CMD ["/bin/bash", "-c", "source activate xcube && xcube genserv start --debug --port 8000 --address 0.0.0.0"]