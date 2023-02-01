# Deployment

## Overview

## For Devops

### GHA Build and Push Requirements

Several GHA workflows will push an image to GHCR, requiring GHCR credentials in the following GitHub secrets:

- `GCHR_USERNAME`
- `GHCR_TOKEN`

### Deployment Requirements

Deploying the service image requires the following environment variables be provided (they are documented in a section below):

- `KBASE_ENDPOINT`
- `ORCID_API_BASE_URL`
- `ORCID_OAUTH_BASE_URL`
- `ORCID_CLIENT_ID`
- `ORCID_CLIENT_SECRET`
- `MONGO_HOST`
- `MONGO_PORT`
- `MONGO_DATABASE`
- `MONGO_USERNAME`
- `MONGO_PASSWORD`

Of these, the only one's which will not be known to KBase devops are the ORCID values. The URLs are documented below, and instructions for obtaining the client id and secret in the next section.

### Additional ORCID Requirements

The client id and client secret should be obtained from ORCID by way of a donor account:

https://info.orcid.org/documentation/integration-guide/registering-a-public-api-client/

While obtaining the the client id and secret, a "redirect url" will need to be provided. That redirect url should be to the `/linking-sessions/continue` endpoint in the ORCID Link service.

- In CI: https://ci.kbase.us/services/orcidlink/linking-sessions/continue
- In Prod: https://kbase.us/services/orcidlink/linking-sessions/continue

Note that the CI should use the ORCID sandbox (the appropriate link is in the ORCID URL above.)

If other environments need to be configured, an redirect url for that environment may be added at any time.

## Service URL

The ORCID Link service should be available with a service path suffix of `orcidlink`. The URL in the CI environment, for example, should be `https://ci.kbase.us/services/orcidlink`

## GitHub Actions

This service uses GitHub Actions (GHA) to provide workflows for testing, image building, and image hosting. 

| event                     | file                              | test | build | push | tag               |
|---------------------------|-----------------------------------|------|-------|------|-------------------|
 | pr to develop             | `pull-request-develop.yml`        | ✓    | ✓     |      |                   |
 | pr to develop merged      | `pull-request-develop-merged.yml` | ✓    | ✓     | ✓    | develop           |
 | pr develop to main        | `pull-request-main.yml`           | ✓    | ✓     | ✓    |                   |
 | pr develop to main merged | `pull-request-main-merged.yml`    | ✓    | ✓     | ✓    | latest-rc         |
 | release against main      | `release-main.yml`                | ✓    | ✓     | ✓    | v#.#.#<br/>latest |
 | manual                    | `manual.yml`                      | ✓    | ✓     | ✓    | ref-*branch*      |

Each event is captured by an individual workflow file. Each workflow file captures the event, and calls reusable workflow files to conduct the actual work.

As described in a section below, all test and build work is invoked via the `Taskfile`. Each task is identified by a simple name below, which corresponds to a function in the Taskfile.

The following reusable workflow files are utilized

| file                                | description                                                                                |
|-------------------------------------|--------------------------------------------------------------------------------------------|
| `reusable_test.yml`                 | runs the following tasks: `mypy`, `black`, `check-openapi`, `test`                         |
| `reusable_build.yml`                | runs the task `git-info` and builds the image from `Dockerfile`                            |
| `reusable_build-push.yml`           | runs the task `git-info`, builds the image from `Dockerfile`, and pushes the image to GHCR |
| `reusable_validate-release-tag.yml` | ensures that the release tag is a properly formed semver tag                               |

## Image repository

Images are stored at GitHub Container Repository (GHCR), which has the host name `ghcr.io`. Image references are thus `ghcr.io/ACCOUNT/IMAGE:TAG`

E.g.

```text
ghcr.io/kbase/kbase-service-orcidlink:v1.2.3
```

Pushing the image to GHCR is conducted by the `reusable_build-push.yml` workflow. This workflow requires the following secrets:

- `GHCR_USERNAME`
- `GHCR_TOKEN`

The `GHCR_TOKEN` requires at least "write packages" scope, which in turn will include "repo".

For development in a personal repo, one may use one's GitHub username and a PAT with "write packages" scope.
 
## Image name

This service roughly follows the KBase conventions for image naming. The base name for the image should be `kbase/kbase-service-orcidlink`, which matches the repo name. I use repo names that are unambiguous when standing on their own. 

The tag should be one of:

- `develop` for the image created when a PR is merged into develop; this image should normally be used for the KBase deployment environment CI, and possibly narrative-dev. It should be redeployed as soon as possible after it is created. 
- `latest-rc` for the image created when develop is merged to main; this image may be used for pre-release evaluation in the KBase deployment environments CI, next, or narrative-dev.
- `v#.#.#` for the image created when a release is created against main; `#.#.#` should follow semver 2.0 conventions; `v` is the recommended prefix for release tags which are followed by a semver.
- `release` is also for an image created for a release, in addition to the version-tag described above.
- `"ref-branch"` - the "manual" workflow will create an image with a tag consisting of the branch name, in lower case, prefixed by "ref-". The prefix helps disambiguate manual builds from ordinary ones.

For example, the image for a release "1.2.3" that should be deployed is

```text
kbase/kbase-service-orcidlink:v1.2.3
```

## Service Dependencies

- KBase auth service
- ORCID API
- ORCID OAuth
- mongodb - version ??

During the development phase, we are using the ORCID Sandbox, a service provided by ORCID which mimics the production ORCID environment but keeps all data separate. 

## Environment Variables required by Service

This service requires the following environment variables:

| Name                 | Secret? | Prod                       | CI                                 | Test      | notes              |
|----------------------|---------|----------------------------|------------------------------------|:----------|--------------------|
| KBASE_ENDPOINT       |         | https://kbase.us/services/ | https://ci.kbase.us/services/      | see ci    |                    |
| ORCID_API_BASE_URL   |         | https://api.orcid.org/v3.0 | https://api.sandbox.orcid.org/v3.0 | see ci    |                    |
| ORCID_OAUTH_BASE_URL |         | https://orcid.org/oauth    | https://sandbox.orcid.org/oauth    | see ci    |                    |
| ORCID_CLIENT_ID      | ✓       |                            |                                    |           | obtain from ORCID  |
| ORCID_CLIENT_SECRET  | ✓       |                            |                                    |           | obtain from ORCID  |
| MONGO_HOST           |         |                            |                                    | mongo     |                    |
| MONGO_PORT           |         |                            |                                    | 27017     |                    |
| MONGO_DATABASE       |         |                            |                                    | orcidlink |                    |
| MONGO_USERNAME       | ✓       |                            |                                    | dev       |                    |
| MONGO_PASSWORD       | ✓       |                            |                                    | d3v       |                    |

Four the the environment variables marked "secret" should never be revealed as plain text. Where indicated, the given values should be used. They are provided here to document their stable values, but the canonical value should be provided by the configuration database.

Note that a different set of values for ORCID URLs, client id and client secret should be used for CI and production (and similar environments). This is because any testing of new functionality in CI should be conducted against the ORCID sandbox test environment. THe sandbox test environment uses a different set of accounts, and uses a different set of client id + secret used for ORCID Link service access to the api.

This may seem like a lot of environment variables, but they are composed of three groups:
- KBase
- ORCID API and OAuth
- MONGO Database

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
