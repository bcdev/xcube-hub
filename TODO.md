### Very important Tasks

* Helge: fully implement `POST /cubes/<user_id>/viewer`
* Norman: implement dummy viewer operations, so the UI works
* Norman: allow `xcube serve` to use AWS credentials
* Helge: use `datastore_id` to decide whether to invoke `xcube sh gen`  or `xcube cci gen`
* Norman: subtract user processing units after successful cube generation

### Less important tasks

* use production WSGI server instead of flask dev server
* add logging
* indicate job progress as ratio of total
* rename env var `RUN_LOCAL` into `XCUBE_GEN_RUN_LOCAL`  
* let all handlers in `service.py` format the results according to `{status='ok', result=result}`
  or catch and then return `({status='error', error=error}, status_code)`. 
  Controllers should just return `result` if any, otherwise raise `api.ApiError`on error.

### Done v1.0.1

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

