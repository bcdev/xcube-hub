### Very important Tasks

* create user namespace if doesn't exist
* use dedicated AWS user credentials to manage bucket `eurodatacube` 
* use `datastore_id` to decide whether to invoke `xcube sh gen`  or `xcube cci gen`
* use special scopes for `PUT /users/<user_id>/punits`
* job output/logs should be separate from job status as this quickly becomes much data 
  (e.g. xcube-sh may print warnings on every SH request).
  Therefore: `GET /jobs/<user_id>/<job_id>/logs` 
* job result dicts are still not consistent, key `job_id` vs. `job` 
  or not matching `{status:'ok', result: any}` pattern. 

### Less important tasks

* rename env var `RUN_LOCAL` into `XCUBE_GENSERV_RUN_LOCAL`
* fix: if we send invalid JSON requests we get error 400

```
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
    <title>400 Bad Request</title>
    <h1>Bad Request</h1>
    <p>The browser (or proxy) sent a request that this server could not understand.</p> 
```
  
* indicate job progress
* `service.py` and others: rename `user_name` into `user_id`
* let all handlers in `service.py` format the results according to `{status='ok', result=result}`
  or catch and then return `({status='error', error=error}, status_code)`. 
  Controllers should just return `result` if any, otherwise raise `api.ApiError`on error.
* add logging
* use production WSGI server instead of flask dev server


### Norman's questions

* what is the use of the `/user_namespace` ops?
We need to create a K8s namespace for each user. These ops do that.
* `service.py` has two error handlers, why?
One is for ApiErrors and the other for flask errors that kick through as html.
* why have large `matplotlib-base` and `jupyterlab` packages in environment?
Not suer about matplotlib. But Jupyterlab can go away.
