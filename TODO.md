### Very important Tasks

* use special scope for `DELETE /users/<user_id>/punits`
* fix: if we send invalid JSON requests we get error 400

```
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
    <title>400 Bad Request</title>
    <h1>Bad Request</h1>
    <p>The browser (or proxy) sent a request that this server could not understand.</p> 
```
  

### Less important tasks

* `service.py` and others: rename `user_name` into `user_id`
* add logging
* use WSDL server instead of flask

### Norman's questions

* what is the use of the `/user_namespace` ops?
* `service.py` has two root `/` ops, why?
* `service.py` has two error handlers, why?
* why have large `matplotlib-base` and `jupyterlab` packages in environment?
