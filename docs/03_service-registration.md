# Service Registrations

BC provides services through the Eurodatacube project. The Hub handles the registration of services
for the geoDB as well xcube generation services. A service registration is represented as a user and
associated service ID and secret in combination of a role that corresponds to a service.

To give an example: A user buys a subscription for the geoDB. The Hub then:

- allocates a user with ID and Secret on his user_metadata
- Associates the user with the role geodb_user

When a user uses the ID/Secret credentials, the geodb client will send these to the Hub. The Hub serves as an oauth token
provider. The Hub sends a query to the Auth0 management API which returns a valid user or not. If valid, the 
Hub generates a token adding information about the subscription to a new token and returns it to the geoDB
client. Otherwise, in the case of an unauthorized client/id pair or if none is sent, the Hub return an HTTP 403 
unauthorized error. The geodbDB client uses this token to access the Postgrest RestAPI which checks the sugnature
of the token. It also uses teh claim `geodb_role` that has been added to the token by the Hub.

## Configs

- XCUBE_HUB_OAUTH_HS256_SECRET: Secret for checking teh signature of a token. Needs to be the same as in the Postgrest
  configuration. Used to encrypt the signature of the token. (Should actually better be an R256 token)
- XCUBE_HUB_OAUTH_USER_MANAGEMENT_CLIENT_ID: Client id for accessing the Auth0 management API
- XCUBE_HUB_OAUTH_USER_MANAGEMENT_CLIENT_SECRET: Client secret for accessing the Auth0 management API
- XCUBE_HUB_OAUTH_USER_MANAGEMENT_AUD: Audience for accessing the Auth0 management API
- XCUBE_HUB_OAUTH_DOMAIN: Domain for obtaining a management token 
