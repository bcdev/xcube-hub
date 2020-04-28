### Very important Tasks

* Helge: fully implement `POST /cubes/<user_id>/viewer`
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

