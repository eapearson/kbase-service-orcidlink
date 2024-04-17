# Environment Variables

THe ORCID Link service utilizes the following environment variables

- `KBASE_ENDPOINT`

- services
  - `KBASE_SERVICE_AUTH`
  - `KBASE_SERVICE_ORCID_LINK`

- orcid related
  - `ORCID_API_BASE_URL`
  - `ORCID_OAUTH_BASE_URL`
  - `ORCID_CLIENT_ID`
  - `ORCID_CLIENT_SECRET`

- mongo db related
  - `MONGO_HOST`
  - `MONGO_PORT`
  - `MONGO_DATABASE`
  - `MONGO_USERNAME`
  - `MONGO_PASSWORD`

Some of these are required - they must be supplied as environment variables or the service will fail to start. Others have sensible defaults and need only be supplied if the defaults need to be overriden.

### Additional ORCID Requirements

The `ORCID_CLIENT_ID` and `ORCID_CLIENT_SECRET` should be obtained from ORCID by way of a donor account:

<https://info.orcid.org/documentation/integration-guide/registering-a-public-api-client/>

KBase should already have a donor ORCID account used to maintain the same credentials for the auth service.

While obtaining the the client id and secret, a "redirect url" will need to be provided. That redirect url should be to the `/linking-sessions/continue` endpoint in the ORCID Link service.

- In CI: <https://ci.kbase.us/services/orcidlink/linking-sessions/continue>
- In Prod (does not exist yet): <https://kbase.us/services/orcidlink/linking-sessions/continue>

Note that the CI should use the *ORCID sandbox* (the appropriate link is to be found in the page at the ORCID URL cited  above.)

If other environments need to be configured, an redirect url for that environment may be added to the ORCID developer tools at any time.

## Environment Variables required by Service Configuration

This service requires the following environment variables:

| Name                 | Secret? | Prod                       | CI                                 | Test      | notes              |
|----------------------|---------|----------------------------|------------------------------------|:----------|--------------------|
| KBASE_ENDPOINT       |         | <https://kbase.us/services/> | <https://ci.kbase.us/services/>      | see ci    |                    |
| ORCID_API_BASE_URL   |         | <https://api.orcid.org/v3.0> | <https://api.sandbox.orcid.org/v3.0> | see ci    |                    |
| ORCID_OAUTH_BASE_URL |         | <https://orcid.org/oauth>    | <https://sandbox.orcid.org/oauth>    | see ci    |                    |
| ORCID_CLIENT_ID      | ✓       |                            |                                    |           | obtain from ORCID  |
| ORCID_CLIENT_SECRET  | ✓       |                            |                                    |           | obtain from ORCID  |
| MONGO_HOST           |         |                            |                                    | mongo     |                    |
| MONGO_PORT           |         |                            |                                    | 27017     |                    |
| MONGO_DATABASE       |         |                            |                                    | orcidlink |                    |
| MONGO_USERNAME       | ✓       |                            |                                    | dev       |                    |
| MONGO_PASSWORD       | ✓       |                            |                                    | d3v       |                    |

Four of the environment variables marked "secret" should never be revealed as plain text. Where indicated, the given values should be used. They are provided here to document their current, stable values, but the canonical value should be provided by the configuration database.

Note that a different set of values for ORCID URLs, client id and client secret should be used for development, but local and in CI, and production (and similar environments). Testing of new functionality in CI should be conducted against the ORCID sandbox test environment. When not testing new functionality (or at least new functionality which could mess up a user's account) it may be acceptable to use the production ORCID APIs.

dThe sandbox test environment uses a different set of accounts, and uses a different set of client id + secret used for ORCID Link service access to the api.

The environment variables are organized into three groups, as reflected by their name prefixes:

- `KBASE_` - KBase endpoint
- `ORCID_` - ORCID API and OAuth location and credentials
- `MONGO_` - MONGO Database location and credentials

### KBase

#### `KBASE_ENDPOINT`

The standard KBase endpoint url, e.g. `https://ci.kbase.us/services/`. It is used to form endpoints for KBase services. The ORCIDLink service currently only uses the KBase auth service to look up user-provided Login tokens.

### ORCID API and OAuth

#### `ORCID_API_BASE_URL`

Base URL for all API requests to ORCID. For example `https://api.sandbox.orcid.org/v3.0`

#### `ORCID_OUATH_BASE_URL`

Base URL for all OAUTH interaction with ORCID, including server-server and client-server. For example, `https://sandbox.orcid.org/oauth`.

#### `ORCID_CLIENT_ID`

All OAuth interactions require usage of a "client id" and "client secret" assigned to KBase. The "client id" is not secret - that is, it is considered a permanent identifier for KBase; exposing it does not compromise security.

#### `ORCID_CLIENT_SECRET`

A secret key required for authentication against the ORCID OAuth endpoint. As opposed to the "client id", the "client secret" must never be exposed. We may expect that it will be replaced from time to time, either due to exposure or due to expiration.

### MONGO Database

This service uses MongoDB to for persistence. Specifically it stores the link between a user's KBase account and ORCID account, and it also temporarily stores linking sessions as a user is creating an ORCID Link.

#### `MONGO_HOST`

The hostname at which the MongoDB server is located. For testing this is `mongo`, for deployment it should be the hostname of the shared MongoDB server instance.

#### `MONGO_PORT`

The port at which the MongoDB server operates on the above host. The default port is `27017`, which is used for the testing environment, but for security purposes the deployment port may  be different.

#### `MONGO_DATABASE`

The name of the database used for the ORCIDLink service. The testing environment, and probably the deployment as well, uses the service module name in lower case - `orcidlink`.

#### `MONGO_USERNAME`

The "username" used for authenticating against the MongoDB server and ORCIDLink database. In testing, it is `dev`.

#### `MONGO_PASSWORD`

The "password" used for authenticating against the MongoDB server and orcidlink database. The testing tools use `d3v`.
