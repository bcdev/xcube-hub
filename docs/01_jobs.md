# xcube-gen Jobs

The [xcube]() toolbox has the ability to run so-called cube generations. These can be started by using the 
xcube-hub RestfulAPI. This chapter describes how to configure the Hub to launch cube generations. For further
details please also refer to the 
[API definition](https://xcube-gen.brockmann-consult.de/api/v2/ui).

## Configs Passed to the Job Container

- GENERATOR_PROCESS_LIMIT: The generation processing limits in PU for users 
- GENERATOR_ROLE_ID: The generator auth0 authorization role
- GENERATOR_PROCESSING_ROLE_ID: The generator auth0 authorization role that allows processing using custom code
- SH_CLIENT_ID: Client ID for accessing the Sentinel Hub API
- SH_CLIENT_SECRET: Client Secret for accessing the Sentinel Hub API
- SH_INSTANCE_ID: Instance ID for accessing the Sentinel Hub API (Still used?)
- CDSAPI_URL: Client URL for accessing the CDS API
- CDSAPI_KEY: Client api key for accessing the CDS API
