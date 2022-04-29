# cate WebAPIs

The hub can also create webapis as Kubernetes deployments. This is used to launch per-user cate as well as 
xcube server instances. The cate server is used in combination of the [cate-app](https://github.com/CCI-Tools/cate-app) 
as provided by the [Cate SaaS](https://cate.climate.esa.int/).


### Cate container configs

- CATE_IMG: (str) The docker image used for the cate server
- CATE_TAG: (str) The version tag of the docker image used for the cate server
- CATE_HASH: (str) The digest of the docker image used for the cate server. Is used instead of tag if not None 
             (default None)
- CATE_COMMAND: (str) The command used to launch the cate server within a container 
                (default: "cate-webapi-start -v -b -p 4000 -a 0.0.0.0 -s 86400 -r /home/xcube/workspace")

- CATE_MEM_LIMIT: (str) Memory limit for a cate server instance (default '16Gi')
- CATE_MEM_REQUEST: (str) Memory request for a cate server instance (default '2Gi')
- CATE_WEBAPI_URI: (str) The webapi URI for the cate server
- CATE_MAX_WEBAPIS: (int) Maximum number of possible webapis (default: 50)
- CATE_LAUNCH_GRACE: (int) Number of seconds the service waits until it returns to user (default: 2)
- WORKSPACE_NAMESPACE: (str) The K8s namespace the server is running in (default cate)

## Configs passed into the cate container

- CATE_DEBUG: (bool) Whether cate should run in debug mode 
- CATE_STORES_CONFIG_PATH: (str) The path to the stores config (default "/etc/xcube-hub/stores.yaml")
- CATE_USER_ROOT: (str) The user workspace root of the user that runs the cate server within a container 
                  (default "/home/xcube/workspace")
- JUPYTERHUB_SERVICE_PREFIX: (str) Cate service prefix 

## Configs Passed into the xcube Server Container

- XCUBE_WEBAPI_BASE_URI: The base url the xcube webapi can be accessed
- XCUBE_VIEWER_BASE_URI: The base url the associated xcube viewer can be accessed

