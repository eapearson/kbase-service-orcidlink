# Configuration

Configuration of the service is through environment variables. All configuration loading and validation is located in the module `orcidlink.lib.config`. 

The `ServiceConfig` class loads all expected environment variables and raises errors if any or missing or invalid. This class itself is loaded by the `main` service entry point module, simply to force any errors to occur as the service is starting, not during operation.

All service code accesses configuration via the `orcidlink.runtime.config` function. This function will create the configuration object the first time it is run, and will use the previously created object after this.

There is no accomodation for dynamic reconfiguration, although this would not be difficult.

## Supported Environment Variables

All environment variables utilized are required. Several have defaults, however, which means that in practice the environment variables do not need to be provided. Still, it is best practice to provide values for all environment variables.

| Name           | Type | Default | Description | Example |
|----------------|------|---------|---|---|
| KBASE_ENDPOINT | str  |  n/a      |The base url for service calls in the current deployment environment. Note that it includes the "services" path and always ends with a "/". | https://ci.kbase.us/services/
| SERVICE_TIMEOUT | int | 600 | The duration, in seconds, after which a request to a network api is considered to have timed out. Such connections will be cancelled after the timeout and raise an error | |
| TOKEN_CACHE_LIFETIME | int | 600 | The duration, in seconds, for which KBase auth token state will be cached. Caching token state saves many calls to the auth service to validate a token. | |
| TOKEN_CACHE_MAX_ITEMS | int | 1000 | The maximum number of token state objects to retain in the cache; when the limit is reached, the least recently used items are removed to make space for new ones | | 
| MONGO_HOST | str | n/a | The host name for the mongo database server | http://mongodb |
| MONGO_PORT | int | 27017 | The port for the mongo database server | 27017 |
| MONGO_DATABASE | str | orcidlink | The name of the mongo database associated with the orcidlink service | orcidlink |
| MONGO_USERNAME | str | n/a | The username for the mongo database used by the orcidlink service | orcidlink_user |
| MONGO_PASSWORD | str | n/a | The password associated with the MONGO_USERNAME | secret_password |
| ORCID_API_BASE_URL | str | n/a | The base url to use for calls to the ORCID API | https://api.sandbox.orcid.org/v3.0 |
| ORCID_OAUTH_BASE_URL | str | n/a | The base url to use for calls to the ORCID OAuth API | https://sandbox.orcid.org/oauth |
| ORCID_SITE_BASE_URL | str | n/a | The base url to use for Links to the ORCID site | https://sandbox.orcid.org |
| ORCID_CLIENT_ID | str | n/a | The "client id" assigned by ORCID to  KBase for using with ORCID APIs | |
| ORCID_CLIENT_SECRET | str | n/a | The "client secret" assigned by ORCID to KBase for using with ORCID APIs | |

