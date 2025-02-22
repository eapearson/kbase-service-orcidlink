# Deployment

## Overview

- Test, build and image push via GitHub Actions
- Image stored at GitHub Container Registry (GHCR) and named using KBase conventions
- Service dependends upon KBase auth, KBase mongodb, and ORCID API and OAuth
- Service configuration by a single `toml` file generated by Python `jinja2` from a template and environment variables at start-up time
- GitHub secrets required at build time for GHCR push, environment variables required at service start time to populate configuration
- The service path element should be `orcidlink`, resulting in an endpoint url like `https://ci.kbase.us/services/orcidlink`.
- Automation with `Taskfile`, all build and test code run within a docker container using the service image.

## Test, build, and push with GitHub Actions

This service uses GitHub Actions (GHA) to provide workflows for testing, image building, and image hosting.

It uses the KBase top level workflows `manual-build.yml`, `pr_build.yml`, and `release-main.py`, which in turn use reusable workflows.

See [the docs](https://github.com/kbase/.github/) for details about these workflows.

In addition to the above, the repo has a workflow `test.yml` which runs the code checks and tests for all workflow trigger conditions.

## Image

### GHCR

Images are stored at GitHub Container Repository (GHCR), which has the host name `ghcr.io`. Image references are thus `ghcr.io/ACCOUNT/IMAGE:TAG`

E.g.

```text
ghcr.io/kbase/kbase-service-orcidlink:1.2.3
```

Pushing the image to GHCR is conducted by the `reusable_build-push.yml`
workflow. This workflow requires the following secrets:

- `GHCR_USERNAME`
- `GHCR_TOKEN`

The `GHCR_TOKEN` requires at least "write packages" scope, which in turn will include "repo".

If you are experimenting with GHA workflows and the like, you can fork the repo
and supply these yourself, using a developer token for the `GHCR_TOKEN`, and
your username for the `GHCR_USERNAME`.

### Image name

This service generally follows the KBase conventions for image naming. The base
name for the image should be `kbase/kbase-service-orcidlink`, which matches the
repo name. I use repo names that are unambiguous when standing on their own.

The tag will be one of:

- `develop` for the image created when a PR is merged into develop; this image
  should normally be used for the KBase deployment environment CI, and possibly
  narrative-dev. It should be redeployed as soon as possible after it is
  created.
- `latest-rc` for the image created when develop is merged to main; this image
  may be used for pre-release evaluation in the KBase deployment environments
  CI, next, or narrative-dev.
- `#.#.#` for the image created when a release is created against main; `#.#.#`
  should follow semver 2.0 conventions.
- `release` is also for an image created for a release, in addition to the
  version-tag described above.
- `"ref-branch"` - the *manual* workflow will create an image with a tag
  consisting of the branch name, in lower case, prefixed by `ref-`. The prefix
  helps disambiguate manual builds from ordinary ones.

For example, the image for a release "1.2.3" that should be labeled as:

```text
kbase/kbase-service-orcidlink:1.2.3
```

## Service Dependencies

- KBase auth service
- ORCID API
- ORCID OAuth
- mongodb - version 7.0.9

### Auth Service

The auth service is configured only by the ubiquitous `KBASE_ENDPOINT`
environment variable. That is, the service base url, e.g.
`https://ci.kbase.us/services/` is taken from configuration, and the actual
endpoint path is embedded in the client.

### ORCID

#### ORCID API and OAuth

The service relies upon two ORCID services, API and OAuth. The OAuth service is utilized by the initial linking process and link revocation, and the API is used for accessing a user's ORCID profile.

The base endpoints are stored in the environment variables `ORCID_API_BASE_URL`
and `ORCID_OAUTH_BASE_URL`. Actual endpoints are created from these bases, based
on the documented URL structures. In other words, although the base URLs are
configurable, any changes in the URL structure would need to be resolved within
code.

All contact with ORCID API and OAuth service requires a client id and secret, to authenticate the interaction and to identify KBase as the authenticated partner service. These values are placed into the environment variables `ORCID_CLIENT_ID` and `ORCID_CLIENT_SECRET`. These should obviously be kept as secrets.

#### ORCID Credentials

ORCID supports two styles of API access - Public and Member. Because we are providing ORCID integration on behalf of other users, we use the Member level API. Unlike Public API credentials which any ORCID member can obtain and manage via the web interface, Member API credentials require direct contact between KBase and ORCID staff. Initial contact is through a [form](https://info.orcid.org/register-a-client-application-production-member-api/), and thereafter communication will be by email. Member API credentials are only available to ORCID partner organizations such as KBase.

We already have such a relationship to support auth. It is not clear whether we should obtain a new set of credentials for ORCID Link or should re-use the existing ones. If the latter, we would just need to contact ORCID and request the additional redirect endpoints be configured.

In any case, the credential configuration requires a so-called "redirect uri", a component of the 3-legged OAuth flow utilized by ORCID. This redirect uri is an endpoint within KBase to which to redirect the user's browser during the OAuth flow, after they have granted KBase permission to act on their behalf.

![orcid-creds-form-return-uri](./orcid-creds-form-return-uri.png)

The endpoint is within the ORCID Link service itself, a requirement of 3-legged OAuth flow. This endpoint is at the service path `linking-sessions/continue`, as it a component of the `linking-sessions` set of services. The actual redirect uri must be fully qualified. Thus in CI the endpoint is

`https://ci.kbase.us/services/orcidlink/linking-sessions/continue`

A redirect uri will need to be specified for each KBase deployment environment that the ORCID credentials will support.

Note that in production, since this is a service endpoint and not a ui endpoint, the uri would be:

`https://kbase.us/services/orcidlink/linking-sessions/continue`

> In the screenshot above, note that in bullet point 3 "fully where possible" means that the url should specify the full path. The configured return uri is used by ORCID OAuth to compare to the request uri specified in the OAuth request itself - if they match, ORCID OAuth will perform the redirect, if not, it will display an error message. The match is made by prefix, so one may use a return uri which simply matches the prefix of the eventual redirect. E.g. we could use `https://ci.kbase.us/services/orcidlink`, which would work with any specific endpoint within the `orcidlink` service, giving us the flexibility to change the endpoint at any time, as long as it has the same prefix. However, their note indicates that it is more secure, from their point of view at least, to have the uri match completely.

During the development phase, we are using the ORCID Sandbox, a service provided by ORCID which mimics the production ORCID environment but keeps all data separate.

See also:

- <https://info.orcid.org/register-a-client-application-production-member-api/>

- <https://info.orcid.org/documentation/integration-guide/registering-a-public-api-client/>

### Mongo DB

The service requires a mongo database to store linking sessions and links themselves. Environment variables are provided for configuring database access.

We try to develop with the same version of mongodb as is used in our production environment. This is simply set in the docker compose configuration files utilized by development workflows.

## Environment Variables

As with most services, environment variables are utilized by the ORCID Link
service directly. They are required for database access, ORCID api access, and
general configuration against KBase deployment environments.

Although environment variables [are documented in
detail](./environment-variables.md), so we'll just summarize them here.

| Variable               | Description                                                                             |
|------------------------|-----------------------------------------------------------------------------------------|
| `KBASE_ENDPOINT`       | Traditional KBase service base url                                                      |
| `SERVICE_DIRECTORY`    | Directory within the image in which the service files are located                       |
| `MONGO_DATABASE`       | Name of the mongo database allocated for orcidlink                                      |
| `MONGO_HOST`           | Host name on which the mongo database is running                                        |
| `MONGO_PORT`           | Port on which the mongo database is running on the host give above                      |
| `MONGO_USERNAME`       | Name of the mongo database defined above                                                |
| `MONGO_PASSWORD`       | Password for the mongo db user named above                                              |
| `ORCID_API_BASE_URL`   | Base URL for ORCID API requests                                                         |
| `ORCID_OAUTH_BASE_URL` | Base URL for ORCID OAuth requests                                                       |
| `ORCID_SITE_BASE_URL`  | Base URL for user access to ORCID                                                       |
| `ORCID_CLIENT_ID`      | Identifier provided by ORCID for API access                                             |
| `ORCID_CLIENT_SECRET`  | Token issued by ORCID which, paired with id above to provide credentials for API access |

### Example

Here is an example configuration for CI Rancher from 4/16/2024:

| Variable               | Value                           |
|------------------------|---------------------------------|
| `KBASE_ENDPOINT`       | `https://ci.kbase.us/services/` |
| `SERVICE_DIRECTORY`    | `/kb/module`                    |
| `MONGO_DATABASE`       | `orcidlink`                     |
| `MONGO_HOST`           | `ci-mongo`                      |
| `MONGO_PORT`           | `27017`                         |
| `MONGO_USERNAME`       | `orcidlink`                     |
| `MONGO_PASSWORD`       | *secret*                        |
| `ORCID_API_BASE_URL`   | `https://api.orcid.org/v3.0`    |
| `ORCID_CLIENT_ID`      | `APP-3GFL8Y9RMZNT3V02`          |
| `ORCID_CLIENT_SECRET`  | *secret*                        |
| `ORCID_OAUTH_BASE_URL` | `https://orcid.org/oauth`       |
| `ORCID_SITE_BASE_URL`  | `https://orcid.org`             |

### Deployment

Service deployment requires that the following environment variables be provided (they are documented in a section below):

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

| Name                 | Secret? | Prod                         | CI                                   | Test      | notes             |
|----------------------|---------|------------------------------|--------------------------------------|:----------|-------------------|
| KBASE_ENDPOINT       |         | <https://kbase.us/services/> | <https://ci.kbase.us/services/>      | see ci    |                   |
| ORCID_API_BASE_URL   |         | <https://api.orcid.org/v3.0> | <https://api.sandbox.orcid.org/v3.0> | see ci    |                   |
| ORCID_OAUTH_BASE_URL |         | <https://orcid.org/oauth>    | <https://sandbox.orcid.org/oauth>    | see ci    |                   |
| ORCID_CLIENT_ID      | ✓       |                              |                                      |           | obtain from ORCID |
| ORCID_CLIENT_SECRET  | ✓       |                              |                                      |           | obtain from ORCID |
| MONGO_HOST           |         |                              |                                      | mongo     |                   |
| MONGO_PORT           |         |                              |                                      | 27017     |                   |
| MONGO_DATABASE       |         |                              |                                      | orcidlink |                   |
| MONGO_USERNAME       | ✓       |                              |                                      | dev       |                   |
| MONGO_PASSWORD       | ✓       |                              |                                      | d3v       |                   |

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

## Service URL

The ORCID Link service should be available with a service path suffix of `orcidlink`. The URL in the CI environment, for example, should be `<https://ci.kbase.us/services/orcidlink>

## Automation

All test and build processes, both in GHA workflows and in local development, is invoked via the `Taskfile`. Each task is identified by a simple name below, which corresponds to a function in the Taskfile.

The taskfile was inspired by the [Taskfile project](https://github.com/adriancooney/Taskfile), which describes a simple system for using a shell script as a single point of entry for automating project tasks.

This resonated with me as our usage of `Makefile` and make for automation is just not quite the right tool for the task. `make` has a different mechanism for managing environment variables and subtasks, which can be worked around but is an additional, unnecessary complication.
