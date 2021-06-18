[![Build status](https://ci.appveyor.com/api/projects/status/l77x6qbx0hslwqfd/branch/master?svg=true)](https://ci.appveyor.com/project/bcdev/xcube-geodb/branch/master)
[![GH actions Build status](https://github.com/bcdev/xcube-hub/actions/workflows/test.yml/badge.svg)](https://github.com/bcdev/xcube-hub/actions/workflows/test.yml/badge.svg)
[![codecov](https://codecov.io/gh/bcdev/xcube-hub/branch/master/graph/badge.svg)](https://codecov.io/gh/bcdev/xcube-hub)

# OpenAPI generated server
## Overview

This server was generated by the [OpenAPI Generator](https://openapi-generator.tech) project. By using the
[OpenAPI-Spec](https://openapis.org) from a remote server, you can easily generate a server stub.  This
is an example of building a OpenAPI-enabled Flask server.

This example uses the [Connexion](https://github.com/zalando/connexion) library on top of Flask.

## Requirements
Python 3.5.2+

## Usage
To run the server, please execute the following from the root directory:

```
pip3 install -r requirements.txt
python3 -m openapi_server
```

and open your browser to here:

```
http://localhost:8080/api/v2/ui/
```

Your OpenAPI definition lives here:

```
http://localhost:8080/api/v2/openapi.json
```

To launch the integration tests, use tox:
```
sudo pip install tox
tox
```

## Running with Docker

To run the server on a Docker container, please execute the following from the root directory:

```bash
# building the image
docker build -t openapi_server .

# starting up a container
docker run -p 8080:8080 openapi_server
```