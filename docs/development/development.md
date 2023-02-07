# Development

## Getting Started

1.  install git hooks

Git hooks are a convenience, but not a requirement. Currently, there is a pre-commit and pre-push hook. The pre-commit runs the same code checks as the GHA workflows do, and the pre-push runs the tests.

```shell
git config --local core.hooksPath .githooks/
```

2. A convenience...

As all development tasks are automated with `Taskfile`. Rather than invoke it with `./Taskfile task`, you can create an alias and invoke it as `run task`:

```shell
alias run="${PWD}/Taskfile"
```

3. run code checks and tests

It is a good idea to start any development session by running the code checks and tests. This ensures you are starting in a clean, well-functioning state.

```shell
run mypy
run black
run test
```

## Running server locally 

> TODO

## Running server locally with kbase-ui

> TODO 

## Contributing

All development is orchestrated through the GitHub repo roughly following the *gitflow* git workflow.

Contributions should be made via a branch off of the develop branch. Such branches should normally be created in response to a KBase JIRA ticket, but can also be related to a GitHub issue. The contribution branch should be pushed directly to the kbase repo, certainly for staff; outside contributions will need to be from forks.

When the branch is ready for review, a PR is made from the contribution branch to the develop branch. The PR description template lists all of the requirements. When those requirements are met, and tests pass, a review should be requested.

Upon approval, the PR will be merged into the develop branch.

Periodically, or as needed, the state of the develop branch will be deployed to the CI environment, https://ci.kbase.us.

At some point in the future, when a release is called for, the develop branch will be merged into the master branch, a release created, and the resulting image deployed to the next environment, appdev, and ultimately production.

## GitHub Action Workflows

When changes are made to the repo at GitHub, GitHub Actions (GHA) may be invoked to perform tests, an image build, and a push of the resulting image to GitHub Container Registry (GHCR).

It is useful to understand exactly when the GHA workflows are triggered and what they do, because you should monitor the results to ensure that everything that should have happened, has indeed occurred.

| branch | triggering condition | test | build | push | image tag |
|--------|----------------------|------|-------|------|---|
| develop | pr activity <sup>1</sup> | ✓ | ✓ | | |
| develop | pr merged | ✓ | ✓ | ✓ | develop |
| main | pr activity | ✓ | ✓ | | |
| main | pr merged | ✓ | ✓ | ✓ | latest-rc, pr-_#_ <sup>2</sup> |
| main | release | ✓ | ✓ | ✓ | latest, _#.#.#_ <sup>3</sup>|
| any | manual | ✓ | ✓ | ✓ | br-_branch_ <sup>4</sup>|

<sup>1</sup> activity defined as "opened", "reopened", "synchronize"   
<sup>2</sup> where _#_ is the pull request number  
<sup>3</sup> where _#.#.#_ is the semver 2 formatted version  
<sup>4</sup> where _branch_ is the branch name upon which the manual workflow was run

## A workflow

### Use & Develop

- deploy this service locally, backed by MongoDB
- run kbase-ui locally, configured to use this service locally
- deployed with reload-on-change 
- develop demo calls via RESTer in Firefox
- need some secrets to run against ORCID Sandbox.

