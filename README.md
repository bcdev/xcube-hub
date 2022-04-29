[![xcube-hub workflow](https://github.com/bcdev/xcube-hub/actions/workflows/xcube-hub_workflow.yaml/badge.svg)](https://github.com/bcdev/xcube-hub/actions/workflows/xcube-hub_workflow.yaml)
[![codecov](https://codecov.io/gh/bcdev/xcube-hub/branch/master/graph/badge.svg)](https://codecov.io/gh/bcdev/xcube-hub)

# xcube-hub

This document describes the software xcube hub. The aim of the hub is to provide a Restful API that allows
to manage spawning [xcube](https://github.com/dcs4cop/xcube) jobs, and xcube and 
[cate](https://github.com/CCI-Tools/cate) services in a Kubernetes cluster.   

The hub, unfortunalety, received two other hmhmhms. The api can therefore register [EDC](https://eurodatacube.com/) user 
and can provide ID tokens for EDC users when using the [geoDB](https://xcube-geodb.readthedocs.io/) and
[xcube generator services](https://eurodatacube.com/marketplace/notebooks/curated/EDC_xcube_generator_service.ipynb).

Please also refer to the docs directory in this repo.  

## Overview

The xcube-hub server has been developed using the following technologies:

- The [Connexion](https://github.com/zalando/connexion) library on top of 
  [Flask](https://flask.palletsprojects.com/en/2.1.x/)
- [OpenAPI Generator](https://openapi-generator.tech) using the [OpenAPI-Spec](https://openapis.org)
- [Python Kubernetes API](https://github.com/kubernetes-client/python)
- conda

A documentation of the OpenApi definition can be found at the 
[xcube-hub URL](https://xcube-gen.brockmann-consult.de/api/v2/ui/).

## Main Requirements

xcube-hub has been tested using the listed main dependency versions. Older versions might work, but no guerantees
can be given:

- Python 3.5.2+
- Flask 2.0.3
- Flask cors 3.0.10
- Flask oidc 1.4.0
- connexion 2.12.0
- python-kubernetes 23.3.0

You can get a full list of dependencies and run the following commands as versions may vary in a freshly created
conda environment:

```bash
conda env create
conda activate xcube-hub
conda list
```

## Usage

To get the server's usage, please execute the following from the root directory in a command shell:

```bash
conda env create
conda activate xcube-hub
xcube-hub start --help
```

### Some Remarks

The xcube-hub server relies for launching cate and xcube processes on a connection to a Kubernetes cluster. When starting
you might get the following error:

```
kubernetes.config.config_exception.ConfigException: Service host/port is not set.
Error: Service host/port is not set.
```

This means that the server has not been configured to run with a local Kubernetes configuration. The solution is to
ensure that you can access a Kubernetes cluster with at least admin rights on a namespace the hub is launching 
Kubernetes resources into. You will also have to set the environment variable `XCUBE_HUB_RUN_LOCAL=1`.
Please refer to the config section for more configs.

Another error that can happen is basically the reverse case of the above. You attempt to run the hub from within a Kubernetes
cluster and with XCUBE_HUB_RUN_LOCAL set to one. It will complain about a missing local Kubernetes config. Set teh env
var `XCUBE_HUB_RUN_LOCAL=0`.

## Running with Docker

The hub is meant to run in a docker container. You can test this by building a docker container and run it:  

```bash
# building the image
docker build -t xcube-hub:latest .

# starting up a container
docker run -p 8080:8080 xcube-hub
```

You can access the container on [localhost](http://localhost:8080/api/v2)

