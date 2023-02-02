# Core Service Requirements

## Codebase structure

- top level Dockerfile that can build the service image without assistance
- document all environment variables used for the config template
  - prefer to be in `/docs` directory
- use an `entrypoint.sh` `bash` script as the image `entrypoint`
- use `jinja` template to generate `toml` config file from environment variables at run time
  - yes this implies that the template is processed from the entrypoint script
- required files:
  - `README.me`
  - `LICENSE.md`
  - `RELEASE_NOTES.md`
  - `.github`
    - `workflows/*`
    - `CODEOWNERS`
    - `pull_request_template.md`
  - `Dockerfile`
  - `scripts`
    - `entrypoint.sh`

## Github

### "gitflow"

The repo workflow should roughly follow "gitflow". There are two permanent branches, "main" and "develop".

All changes start as branches off of develop. Let's call those "change branches", aka, "feature branches", but they may be for any purpose.

Change branch activity triggers no GHA workflows.

When ready to incorporate into codebase, create PR against develop. PR activity triggers GHA workflows for test and build.

When approved, merging the PR into develop triggers GHA test, build, and push of an image named "develop".

When preparing a release, PR from develop to main, triggering test, build. 

When approved, merging the PR into main triggers GHA test, build, and push of an image named "latest-rc".

To create a release, use the GitHub release tool with a branch name reflecting the release version as "v#.#.#", where "#.#.#" is semver 2. A release triggers GHA test, build, and push of an image named "latst" and "v#.#.#".

### manual build

There must be a GHA manual workflow for test, build, push of any branch.

## Communicate to devops

When ready to deploy in CI for the first time, please communicate to devops the following minimal information:

- repo name (must be in kbase org)
- desired service path
  - lower case
  - i.e. the myservice in  https://ci.kbase.us/services/myservice
- environment variables for config template
  - can be pointer to documentation in codebase
- if require *mongodb* access:
  - name of database

## Development (Python)

my thoughts, not expressed by devops

- 100% code coverage
- `mypy`, `black` compliance
- header doc for every module
- smallish `README.md `with links into `docs` for details
- document
  - how to develop
  - contribution guidelines
  - deployment overview
  - service dependencies
- prefer
  - docker-based workflow for all procedures (test, build, etc.)