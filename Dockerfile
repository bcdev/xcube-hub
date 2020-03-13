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

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"; \
    unzip awscliv2.zip; \
    ./aws/install; \
    aws --version

RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/`curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt`/bin/linux/amd64/kubectl; \
    chmod +x ./kubectl; \
    mv ./kubectl /usr/local/bin/kubectl; \
    kubectl version --client

USER ${XCUBE_USER_NAME}

RUN git clone https://github.com/dcs4cop/xcube /home/${XCUBE_USER_NAME}/xcube

WORKDIR /home/${XCUBE_USER_NAME}/xcube
RUN conda env create
RUN source activate xcube && python setup.py install


ADD --chown=1000:1000 environment.yml environment.yml
RUN conda env update -n xcube

ADD --chown=1000:1000 ./ .
RUN source activate xcube && python setup.py install

EXPOSE 8000

CMD ["/bin/bash", "-c", "source activate xcube && xcube genserv start --debug --port 8000 --address 0.0.0.0"]