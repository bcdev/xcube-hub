### Changes in v1.0.6

* Suports now cciodp and cds data stores
* Handles new bucket url config from xcube-gen-ui
* Can now handle callbacks using a KeyValue database (either redis or leveldb or inmemory)

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
