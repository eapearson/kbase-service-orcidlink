# ORCIDLink releases

Each section corresponds to a GitHub release, other than the top "Unreleased" section which is for compiling changes between the most recent release and the next one.

All changes between the most recent release and the present set of changes should be captured in the top section titled "Unreleased".

One line per change in the release. Each line is a markdown list item.

If the change is associated with a JIRA ticket, add the ticket number at the end of the change line surrounded by brackets.

## Unreleased

DATE of release

SUMMARY of release

* Replace GHA workflow files with official KBase ones [CE-161]
* Update to Pyton 11.1 image to solve CVE-2022-40897 [CE-161]
* Patch poetry venv in Dockerfile to solve 2nd CVE-2022-40897 [CE-161]


## 0.2.0

February 2, 2023

On the path towards being a core service.

* Migrate to mongodb
* convert config to toml (from yaml) [CE-161]
* convert template tech to jinja2 (from dockerize) [CE-161]
* add additional environment variables for ORCID urls [CE-161]
* document workflows, improve pr template [CE-161]
* add static documentation generation, improve README [CE-162]
* Add git-info task & tool to capture git [CE-164]
* Type the ORCID API [CE-166]
* Add commit hooks (pre-commit, pre-push) [CE-171]

## 0.1.0

January 20, 2023

First release, prototype

* Module created by kb-sdk init
* Works locally, iterating on getting it to run in CI
* migrated away from kb-sdk, removing all kb-sdk artifacts, as it will be deployed as a core service.
* have implemented testing with 100% coverage, GHA-hosted build and push to GHCR
