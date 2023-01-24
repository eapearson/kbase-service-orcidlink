# Deployment

## Overview

## Canonical URL

The ORCID Link service should be available with a service path suffix of `orcidlink`. The URL in the CI environment, for example, should be `https://ci.kbase.us/services/orcidlink`

## GitHub Actions

This service uses GitHub Actions (GHA) to provide workflows for testing, image building, and image hosting. 

| event                       | test | build | push | tag               |
|-----------------------------|------|-------|------|-------------------|
 | pr to develop activity      | ✓    | ✓     |      |                   |
 | pr to develop merged        | ✓    | ✓     | ✓    | develop           |
 | pr develop -> main activity | ✓    | ✓     | ✓    |                   |
 | pr develop -> main merged   | ✓    | ✓     | ✓    | latest-rc         |
 | release against main        | ✓    | ✓     | ✓    | v#.#.#            |
 | manual                      | ✓    | ✓     | ✓    | ref-<branch name> |
 
## Image repository

Images are stored at GitHub Container Repository (GHCR), which has the host name `ghcr.io`. Image references are thus `ghcr.io/ACCOUNT/IMAGE:TAG`

E.g.

```text
ghcr.io/kbase/kbase-service-orcidlink:v1.2.3
```
 
## Image name

This service roughly follows the KBase conventions for image naming. The base name for the image should be `kbase/kbase-service-orcidlink`, which matches the repo name. I use repo names that are unambiguous when standing on their own. 

The tag should be one of:

- `develop` for the image created when a PR is merged into develop; this image should normally be used for the KBase deployment environment CI, and possibly narrative-dev. It should be redeployed as soon as possible after it is created. 
- `latest-rc` for the image created when develop is merged to main; this image may be used for pre-release evaluation in the KBase deployment environments CI, next, or narrative-dev.
- `v#.#.#` for the image created when a release is created against main; `#.#.#` should follow semver 2.0 conventions; `v` is the recommended prefix for release tags which are followed by a semver.
- `release` is also for an image created for a release, in addition to the version-tag described above.
- `"ref-<branch>"` - the "manual" workflow will create an image with a tag consisting of the branch name prefixed by "ref-". The prefix helps disambiguate manual builds from ordinary ones.

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

## Environment Variables

This service requires the following environment variables:

| Name                 | Secret? | Test Value                         |
|----------------------|---------|------------------------------------|
| KBASE_ENDPOINT       |         | https://ci.kbase.us/services/      |
| ORCID_API_BASE_URL   |         | https://api.sandbox.orcid.org/v3.0 |
| ORCID_OAUTH_BASE_URL |         | https://sandbox.orcid.org/oauth    |
| ORCID_CLIENT_ID      | ✓       | request from ORCID                 |
| ORCID_CLIENT_SECRET  | ✓       | request from ORCID                 |
| MONGO_HOST           |         | mongo                              |
| MONGO_PORT           |         | 27017                              |
| MONGO_DATABASE       |         | orcidlink                          |
| MONGO_USERNAME       | ✓       | dev                                |
| MONGO_PASSWORD       | ✓       | d3v                                |


This may seem like a lot of environment variables, but they are composed of three groups:
- KBase
- ORCID
- MONGO

### `KBASE_ENDPOINT`

The standard KBase endpoint url, e.g. `https://ci.kbase.us/services/`. It is used to form endpoints for KBase services. The ORCIDLink service currently only uses the KBase auth service to look up user-provided Login tokens.

### ORCID

#### `ORCID_API_BASE_URL` 

Base URL for all API requests to ORCID. For example `https://api.sandbox.orcid.org/v3.0`

#### `ORCID_OUATH_BASE_URL`

Base URL for all OAUTH interaction with ORCID, including server-server and client-server. For example, `https://sandbox.orcid.org/oauth`.

#### `ORCID_CLIENT_ID`

All OAuth interactions require usage of a "client id" and "client secret" assigned to KBase. The "client id" is not secret - that is, it is considered a permanent identifier for KBase; exposing it does not compromise security.

#### `ORCID_CLIENT_SECRET`

A secret key required for authentication against the ORCID OAuth endpoint. As opposed to the "client id", the "client secret" must never be exposed. We may expect that it will be replaced from time to time, either due to exposure or due to expiration.

### `MONGO`

This service uses MongoDB to for persistence. Specifically it stores the link between a user's KBase account and ORCID account, and it also temporarily stores linking sessions as a user is creating an ORCID Link.

#### `MONGO_HOST`

The hostname at which the MongoDB server is located. For testing this is `mongo`, for deployment it should be the hostname of the shared MongoDB server instance.

#### `MONGO_PORT`

The port at which the MongoDB server operates on the above host. The default port is `27017`, which is used for the testing environment, but for security purposes the deployment port may  be different. 

#### `MONGO_DATABASE`

The name of the database used for the ORCIDLink service. The testing environment, and probably the deployment as well, uses the service module name in lower case - `orcidlink`.

### `MONGO_USERNAME`

The "username" used for authenticating against the MongoDB server and ORCIDLink database. In testing, it is `dev`.

#### `MONGO_PASSWORD`

The "password" used for authenticating against the MongoDB server and orcidlink database. The testing tools use `d3v`.
