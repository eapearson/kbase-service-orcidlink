# Build

Generally the build is conducted by a GitHub action workflow. All of the build steps may be conducted locally. In fact, one should exercise all build steps before a PR review, to minimize the build iterations at GitHub.

The end result of the build is a Docker image. The fundamental build is simply a docker build! However, a practical build also involves ensuring the build will work and the code is of high quality. To that end the build requires:

- validation with MyPy for proper type usage
- validation with tests to ensure proper operation
- validation with code quality tools to ensure well-formed and maintainable code
- if all these requirements are met, an image is created.

Evaluations builds will be conducted against Pull Requests, and product builds against GitHub releases.

A production build will also result in an image pushed to GHCR and tagged with the release version, as well as "release".

## Compilation

As a Python app, there is no separate compilation step.

## Testing

Prior to a build, all tests must pass 

## Code Quality

### MyPy

### Functional tests

## Image

## GHA 