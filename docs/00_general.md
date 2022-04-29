# General xcube hub Configs

Some configs are used to aid the development of the Hub. 

## geoDB Configs Used in the Hub

- WERKZEUG_RUN_MAIN: Set to one if pycharm debugger is on
- XCUBE_HUB_DEBUG: If the pycharm debugger shall be launched
- CUBE_HUB_CFG_SECRET: Secrets that host environment variables for teh Hub
- XCUBE_HUB_RUN_LOCAL: Whether a local K8s config shall be used or whether the Hub is running within a K8s cluster and 
  a service account is used.
- XCUBE_HUB_DOCKER_PULL_POLICY: Docker pull policy for jobs and deployments
- XCUBE_HUB_CACHE_PROVIDER: Cache provider (inmemory or redis) 
- XCUBE_HUB_REDIS_HOST: Redis service host name if redis is used
- XCUBE_HUB_CODE_ROOT_DIR: The location of the cubegens custom code configurations
- XCUBE_HUB_RESULT_ROOT_DIR: The location of the cubegens results
