# Releasing

The `orcidlink` service is ordinarily deployed from an image tagged with a release version. This ensures deterministic deploys, as the image for a given release will always be the same. It also enables easy reversions to a previous release, in the case of errors introduced by a release.

The release process is composed of the following major tasks:


- create a JIRA ticket for the release
- create a new branch off of develop for the release
- prepare codebase for release:
  - finalize release notes
    - rename "Unreleased" section to the version
    - date the new release section
    - add a description to the new release section
    - create a new "Unreleased" section at the top
- commit and push up these changes
- create a PR to develop from this release branch
  - The PR description should summarize what is in the release
- run the manual workflow against the release branch
- run integration tests locally using the image built for the release branch
  - this is not yet implemented, but for now we can run the image locally, and use either direct poking like Restr in the browser, or some basic scripts (again, don't exist yet), and directly with kbase-ui
- when/if integration tests pass, request a PR review  
- when PR approved, merge it into develop
- immediately create a PR from develop to main
- get approval for this PR
- if all goes will with PR checks (no reason they shouldn't since there should be no diff), merge it into main
- run a final set of integration tests locally using the latest-rc image built after the merge into main
- create a release using the GitHub release tool; the version should follow semver 2.0, and the tag should be formatted like `v#.#.#`, e.g. `v1.2.3` for release "1.2.3"
- deploy on CI
- exercise the API on CI
- let devops know the release is ready for general release deployent