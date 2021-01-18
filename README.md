[![Docker Repository on Quay](https://quay.io/repository/bcdev/xcube-hub/status "Docker Repository on Quay")](https://quay.io/repository/bcdev/xcube-hub)

## Setup

```bash
cd xcube-gen
conda env create
conda activate xcube-gen
python setup.py develop
```
    
### Test:

    $ pytest

## Tools

Check xcube CLI extension added by `xcube_gen` plugin:

    $ xcube --help
    
`genserv` should now be in the list.    

Start the service: 

    $ xcube-genserv start
    
    
## Environment Configurations

### Global

- LAUNCH_XCUBE_GEN: `<"1", ["0"]>` 
- LAUNCH_CATE: `<"1", ["0"]>` 
- LAUNCH_GEODB: `<"1", ["0"]>` 
- OIDC_CLIENT_SECRETS_FILE: Path to the OIDC secrets configuration
- AWS_ACCESS_KEY_ID: default AWS access key
- AWS_SECRET_ACCESS_KEY: default AWS access secret
- XCUBE_HUB_CHART_VERSION: chart version used for deploying the hub
- XCUBE_HUB_MOCK_SERVICES. whether services are mocked
- XCUBE_HUB_RUN_LOCAL: whether the hub is run locally  



### cate

- CATE_LAUNCH_GRACE: Grace time when cate is launched `[3]` 
- CATE_IMG: cate webapi docker image
- CATE_VERSION: version of cate
- CATE_USER_ROOT: User root cate should use when running
- CATE_COMMAND: command to be used in the docker container
- CATE_OBS_NAME: name of the object store volume `["mnt-goofys"]`
- CATE_ENV_ACTIVATE_COMMAND: The command to be used when activating the conda environment `["source activate cate-env"]`
- CATE_WEBAPI_URI: The URI where the cate webapi will be accesses 
- CATE_WEBAPI_NAMESPACE: The K8s namespace used for the webapi `["cate-userspace"]`
- CATE_WORKSPACE_CLAIM_NAME: Name of the K8s PVC used for user scratch spaces `["workspace-pvc"]`
- CATE_WEBAPI_NAMESPACE: Namespace teh cate-webapi resides in 


### xcube-gen

- XCUBE_DOCKER_IMG: Docker image of xcube to be used
- XCUBE_GEN_API_CALLBACK_URL: URL to be used for callback calls
- SH_CLIENT_ID: SH client id
- SH_CLIENT_SECRET: SH client secret
- SH_INSTANCE_ID: SH instance id
- XCUBE_DOCKER_WEBAPI_IMG
- XCUBE_GEN_DOCKER_PULL_POLICY: The pull policy `["Always"]`
- XCUBE_GEN_CACHE_PROVIDER: The cache provider `<"inmemory", "redis", ["leveldb"]>`
- XCUBE_GEN_REDIS_HOST: Host address for redis if used
- XCUBE_WEBAPI_URI: 
- XCUBE_VIEWER_PATH: The path to the viewer instance `["/api/v1/viewer"]`
- XCUBE_GEN_API_CALLBACK_URL: URL for callbacks
- XCUBE_GEN_DATASTORE_CONFIG_PATH: Path to the datastore configs `["/mnt/data-stores/data-stores.json"]` 
- K8S_NAMESPACE: Namespace xcube-hub resides in
