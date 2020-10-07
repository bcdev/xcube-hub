FROM continuumio/miniconda3:4.8.2

ARG XCUBE_VIEWER_VERSION=0.4.2
ARG XCUBE_USER_NAME=xcube
ENV XCUBE_GEN_API_VERSION=1.0.12
ENV XCUBE_API_UWSGI_INI_PATH="/home/${XCUBE_USER_NAME}/xcube_gen/resources/uwsgi.yaml"

LABEL maintainer="helge.dzierzon@brockmann-consult.de"
LABEL name="xcube hub service"
LABEL xcube_version=${XCUBE_BASE_VERSION}
LABEL xcube_gen_api_version=${XCUBE_GEN_API_VERSION}

USER root
SHELL ["/bin/bash", "-c"]
RUN useradd -u 1000 -g 100 -ms /bin/bash ${XCUBE_USER_NAME}
RUN chown -R ${XCUBE_USER_NAME}.users /opt/conda

RUN source activate base && conda update -n base conda && conda init
RUN source activate base && conda install -y -c conda-forge mamba
RUN echo "conda activate cate-env" >> ~/.bashrc

RUN apt-get -y update && apt-get -y install curl unzip build-essential iputils-ping vim
RUN mkdir /var/log/uwsgi && chown 1000.users /var/log/uwsgi

USER ${XCUBE_USER_NAME}

RUN conda install -c conda-forge -n base mamba

WORKDIR /home/${XCUBE_USER_NAME}
ADD --chown=1000:100 environment.yml environment.yml

RUN mamba env create

ADD --chown=1000:100 ./ .
RUN source activate xcube-gen && pip install redis
RUN source activate xcube-gen && pip install .

COPY --from=quay.io/bcdev/xcube-viewer:0.4.2 /usr/src/app/build /home/${XCUBE_USER_NAME}/viewer


EXPOSE 8000
EXPOSE 5050

#CMD ["/bin/bash", "-c", "source activate xcube-gen && xcube-genserv start -p 8000 -a 0.0.0.0"]
CMD ["/bin/bash", "-c", "source activate xcube-gen && uwsgi --static-index /viewer/index.html --yaml ${XCUBE_API_UWSGI_INI_PATH}"]
