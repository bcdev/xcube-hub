## Changes in v1.0.13.dev1

### New Features

- Added an operation /status which returns a status 
  set by the env vars XCUBEHUB_STATUS and XCUBE_HUB_STATUS_MESSAGE.
  Helps e.g. when an xchubehub instance shall be suspended.
- Added auth operators to manage users
- data-stores.json location is now configurable via environment variables.
- Set ingress websocket timeouts to 1 day
- Ensured that the grace period foe launching cate services is integer 
- Getting a job status does now raise an HTTP error when the job had failed.
- The ApiError and webapi-response returns now outputs and tracebacks when applicable

### Fixes

- Removed poll_job_status. Not used.
- The cate ingress is now patched not created
- Cate instances are now run in namespace cate allowing for NFS permanent 
  volumes in Kubernetes.
- Launch_cate is not returning the URL without https
- Set ingress timeouts to 1 day
- Ensured that the grace period foe launching cate services is integer 
- Improved testing for K8s functions

## Changes in v1.0.12

### New Features

- The launch of cate and xcube-gen-api handlers can now be configured

### Fixes

- Sets now correct xcube-gen-api version in Dockerfile's labels
- The error can now handle errors and tracebacks  

## Changes in v1.0.11

### Fixes

- When the xcube webapi is started the service waits ofr a grace period in order to avoid issues with the xcube-gen-ui.json
- A username validation function was added to avoid conflicts with kubernetes naming conventions

## Changes in v1.0.10

### Fixes

* Cate is spawned with JUPYTERHUB_SERVICE_PREFIX. Fixes CORS errors for accessing ws tiles
* xcube gen adds a grace sleep when the cate webapi is started. Fixes issues when starting the
    cate webapi from the webui

## Changes in v1.0.9

### New Features

* Supports now spawning of cate containers.
* Also supports Keycloak auth for cate

## Changes in v1.0.8

### New Features

* Supports now cciodp and cds data stores 
* can now handle callbacks using a KeyValue database (either redis or leveldb or inmemory)
* can now serve as a wsgi service
* Can now spawn an xcube webservice and a corresponding xcube viewer 

### Enhancements

* Includes now a poller for e.g. observing K8s processes
* Added a service mock to simplify service mocks
* An openapi yaml config file was added
* Authentication and authorization processes were strengthened

### Fixed

* handles  bucket url config from xcube-gen-ui


### Changes in v1.0.5 and v1.0.6

* Synced version with xcube-gen-ui

### Changes in v1.0.5

* Updated computation of processing units. Now also "cciodp" datastore is supported.

### Changes in v1.0.4

* Demo version for ESA SRR-F meeting. 

### Changes in v1.0.3

* Using environment variables AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
  to pass AWS credentials to object database. 

### Changes in v1.0.2

* Implemented dummy viewer operations
  * `POST /cubes/<user_id>/viewer`
  * `POST /mock/cubes/<user_id>/viewer`

### Changes in v1.0.1

* create user namespace if doesn't exist
* use dedicated AWS user credentials to manage bucket `eurodatacube` 
* use special scopes for `PUT /users/<user_id>/punits`
* job output/logs should be separate from job status as this quickly becomes much data 
  (e.g. xcube-sh may print warnings on every SH request).
  Therefore: `GET /jobs/<user_id>/<job_id>/logs` 
* job result dicts are still not consistent, key `job_id` vs. `job` 
  or not matching `{status:'ok', result: any}` pattern. 
* `service.py` and others: rename `user_name` into `user_id`
* fix: if we send invalid JSON requests we get error 400

```
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
    <title>400 Bad Request</title>
    <h1>Bad Request</h1>
    <p>The browser (or proxy) sent a request that this server could not understand.</p> 
```
