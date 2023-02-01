# Development

## Contributing

All development is orchestrated through the GitHub repo roughly following the *gitflow* git workflow.

Contributions should be made via a branch off of the develop branch. Such branches should normally be created in response to a KBase JIRA ticket, but can also be related to a GitHub issue. The contribution branch should be pushed directly to the kbase repo, certainly for staff; outside contributions will need to be from forks.

When the branch is ready for review, a PR is made from the contribution branch to the develop branch. The PR description template lists all of the requirements. When those requirements are met, and tests pass, a review should be requested.

Upon approval, a PR will be merged into the develop branch.

Periodically, or as needed, the state of the develop branch will be deployed to the CI environment, https://ci.kbase.us.

At some point in the future, when a release is called for, the develop branch will be merged into the master branch, a release created, and the resulting image deployed to the next environment, appdev, and ultimately production.

## A workflow

### Use & Develop

- deploy this service locally, backed by MongoDB
- run kbase-ui locally, configured to use this service locally
- deployed with reload-on-change 
- develop demo calls via RESTer in Firefox
- need some secrets to run against ORCID Sandbox.

## From Devops (Boris)

I believe the requirements are
- Dockerfile with entrypoint
- add GHA build actions
- Follow the develop->main PR flow in order to enable builds using GHA actions and deployment to CI
- Provide environmental configuration variables, so devops can customize them for each environment, and then your app
- Provide us with your desired URL and we will set it up

https://rancher.berkeley.kbase.us/env/1a803/apps/stacks/1st290/services/1s239031/containers uses the practices we want

Here is how collections uses env variables instead of dockerize
- https://github.com/kbase/collections/blob/main/scripts/entrypoint.sh#L5
- https://github.com/kbase/collections/blob/main/collections_config.toml.jinja


If you clone the collections service with the name you want, thats all we need in rancher, just an updated image name, env vars, and a URL