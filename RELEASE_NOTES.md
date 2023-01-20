# ORCIDLink releases

Each section corresponds to a GitHub release.

All changes between the most recent release and the present set of changes should be captured in the top section titled "Unreleased".

One line per change in the release. Each line is a markdown list item.

If the change is associated with a JIRA ticket, add the ticket number at the end of the change line surrounded by brackets.

## Unreleased

First release.

* Module created by kb-sdk init
* Works locally, iterating on getting it to run in CI
* migrated away from kb-sdk, removing all kb-sdk artifacts, as it will be deployed as a core service.
* have implemented testing with 100% coverage, GHA-hosted build and push to GHCR
* Migrate to mongodb
* convert config to toml (from yaml) [CE-161]
* convert template tech to jinja2 (from dockerize) [CE-161]
* add additional environment variables for ORCID urls [CE-161]