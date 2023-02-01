# ORCID Link  _(kbase-service-orcidlink)_

A KBase core REST service whose primary purpose is to link KBase accounts to ORCID accounts.

ORCID Link also provides relates services, such as fetching the profile for a linked account, and managing the "works" for a linked account

The service is implemented in Python, using the FastAPI library.

Please see the [design doc](docs/design.md) for further information.

## Security

This service will only run with a specific set of [environment variables](docs/deployment.md#environment-variables), some of which contain private keys which are essential for communication with ORCID Services. See [the deploymet doc](docs/deployment.md) for details.

## Background

Many users of KBase also are [ORCID (Open Researcher and Contributor ID)](https://orcid.org) users as well. There are many opportunities for synergy between KBase and ORCID with respect to their users. Examples include:

- **profile synchronization**: An ORCID account is designed to serve as a canonical profile; as such, a KBase profile is not only redundant, but may be in conflict; KBase can use a user's associated ORCID profile to synchronize with or replace the KBase profile.
- **automated publication**: KBase is a platform supporting publication of analysis documents termed "Narratives", as well as the publication of openly accessible data. A KBase user who publishes Narratives and data and obtains a [DOI](https://doi.org), may use KBase tools to automatically populate and manage the "works" section of their profile.

By linking a KBase account to an ORCID account, tools described above can be implemented, to the benefit of KBase users.

## Installation

This service is not directly installable as such. It is a REST-based web service and must be built and run within a compatible deployment environment.

I suppose "installation" consists of building a Docker image and hosting it somewhere. In practice, this is conducted at GitHub, with a build conducted via [GitHub Actions](docs/deployment.md#github-actions) and hosted at the GitHub Container Repository (GHCR). 


## Usage

There are different scenarios under which it may be run and utilized. Each is described in separate sections:

- [development](docs/development.md)
- [deployment](docs/deployment.md)

Deployment support is described, but deployment practices and mechanics are out of scope of this document and service.

Running as a local service is not only feasible but the normal model for development.

## Usage

```shell
ORCID_SANDBOX_CLIENT_ID=<client id> ORCID_SANDBOX_CLIENT_SECRET=<client secret> docker compose up
```

It currently works with the ORCID sandbox, so the credentials used above must be obtained from an ORCID sandbox account.

## API

The [API docs](docs/api/index.md) are generated automatically, and are [available in the codebase](docs/api/index.md) as well as from a live instance of the service at the `/docs` endpoint. 

## Contributing

For supported and recommended development practices see [development](docs/development.md).

All development is orchestrated through the GitHub repo roughly following the *gitflow* git workflow.

Contributions should be made via a branch off of the develop branch. Such branches should normally be created in response to a KBase JIRA ticket, but can also be related to a GitHub issue. The contribution branch should be pushed directly to the kbase repo, certainly for staff; outside contributions will need to be from forks.

When the branch is ready for review, a PR is made from the contribution branch to the develop branch. The PR description template lists all of the requirements. When those requirements are met, and tests pass, a review should be requested.

Upon approval, a PR will be merged into the develop branch.

Periodically, or as needed, the state of the develop branch will be deployed to the CI environment, https://ci.kbase.us.

At some point in the future, when a release is called for, the develop branch will be merged into the master branch, a release created, and the resulting image deployed to the next environment, appdev, and ultimately production.

## License

See license in [LICENSE.md](LICENSE.md)