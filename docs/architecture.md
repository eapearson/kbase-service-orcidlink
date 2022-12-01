# Architecture

This is a KBase Dynamic Service, but does not follow the standard kb-sdk architecture or tooling.

## Why Diverge from kb-sdk?

The primary reasons to diverge from the KBase SDK are:
- The sdk is quite out of date in terms of Python support and base OS
- Advances in the Python http service ecosystem has brought forth fastapi, a library which brings:
  - good typing
  - automatic api documentation generation
  - easy REST api building