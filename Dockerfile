ARG XCUBE_HUB_DOCKER_BASE_VERSION=latest

FROM quay.io/bcdev/xcubehub-base:${XCUBE_HUB_DOCKER_BASE_VERSION}

ARG XCUBE_VIEWER_VERSION=0.4.2
ARG XCUBE_USER_NAME=xcube
ENV XCUBE_HUB_DOCKER_BASE_VERSION=latest
ENV XCUBE_HUB_VERSION=1.0.14.dev1
ENV XCUBE_API_UWSGI_INI_PATH="/home/${XCUBE_USER_NAME}/xcube_hub/resources/uwsgi.yaml"

LABEL maintainer="helge.dzierzon@brockmann-consult.de"
LABEL name="xcube hub service"
LABEL xcubehub_base_version=${XCUBE_HUB_DOCKER_BASE_VERSION}
LABEL xcubehub_version=${XCUBE_HUB_VERSION}

USER ${XCUBE_USER_NAME}

ADD --chown=1000:100 ./ .
RUN source activate xcube-hub && pip install redis
RUN source activate xcube-hub && pip install .

COPY --from=quay.io/bcdev/xcube-viewer:0.4.2 /usr/src/app/build /home/${XCUBE_USER_NAME}/viewer

EXPOSE 8000
EXPOSE 5050

# CMD ["/bin/bash", "-c", "source activate xcube-hub && xcube-hub start -p 8000 -a 0.0.0.0"]
CMD ["/bin/bash", "-c", "source activate xcube-hub && uwsgi --static-index /viewer/index.html --yaml ${XCUBE_API_UWSGI_INI_PATH}"]
