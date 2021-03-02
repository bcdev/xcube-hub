## Changes in v2.0.0.dev0

### New Features

- The hub uses now an openapi flask stub to simplify server configuration
- The OpenApi definition has been overhauled to follow best practices in defining path patterns
- xcube-hub can now issue HS256 tokens via client credentials using an `/oauth/token` handler
- The `/datastores` handler has been replaced by a cubegens info handler   
- The `/cubegens/info` handler provides now much smaller data-pools information for better performance
- Changed the CI from travis to appveyor
- Progress Information is now returned by the `GET /cubegens/{cubegen_id}` handler
- `/callbacks` handlers have been reduced to allow PUT only
- The main function has been moved to `__main__.py` to simplify launching the hub inside docker containers
- The Docker command has been simplified by using the python executable directly
- The authorization flow allows not to use both xcube-hub as well as auth0 issued tokens
- Added an Auth class that handles the creation of
  authorization class instances as singletons to handle different authorization issuers
- Ensured that controllers that need the user_id and/or email will
  get it passed using the token_info function parameter.
- The token_info is now set during the token verification process
- The HttpRequest response for the route `/cubegens/{cubegen_id}` includes now progress information
- put_callback now receives the user's email address to be used in setting the punits for a user
- Changed `worked` to `progress` for Callbacks in openapi rest definition
- The output data_id is now only set to teh `job_id` if the `data_id` is not given
- The `/cubegens/info` process has changed it now receives any necessary data for teh punits calculation from
  xcube gen2 via a xcube gen2 job

## Changes in v1.0.14
### New Features
- okteto uses now a xhubehub-base image
- The default cache provider is now inmemory
- Changed parameter user_id to user_namespace in create_if_not_exist
- get_datastores accepts now yaml files
- wsgi will start a debug service if XCUBE_HUB_DEBUG is set to 1
- sizeandcost accepts now a None enddate. Defaults to now()
- Added an okteto service patch to allow external K8s services accessing the hub
- Added a setup.sh to setup dependencies in okteto

### Fixes

- The location of data-pools.yaml is changed to /etc/xcube
- use jobs are now spawned in the xcube-gen namespace instead of a namespace for each user
- The user_info in auth0 is now accepting checking whether the userinfo from teh kv store is string
- The redis kv store converts bytes to string in the method 'get'
- Fixed user_info error which was causing the  hub to frequently accessing the auth0 user_info api. That caused 429 errors from teh auth0 api. 


## Changes in v1.0.13

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
