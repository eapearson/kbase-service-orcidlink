# Architecture

This is a KBase Dynamic Service, but does not follow the standard kb-sdk architecture or tooling.

## Why Diverge from kb-sdk?

The primary reasons to diverge from the KBase SDK are:
- The sdk is quite out of date in terms of Python support and base OS
- Advances in the Python http service ecosystem has brought forth fastapi, a library which brings:
  - good typing
  - automatic api documentation generation
  - easy REST api building

## FastAPI

### Using types

FastAPI has optional strong typing based partly on Pydantic. This conflicts with one of the major benefits of using Python for a service like this - simplicity. On of the aspects of simplicity is lack of static typing.

Still, Pydantic typing, which is based on native Python typing, can be applied incrementally and partially. If one were to apply full typing across a codebase, it could be argued that one should just use a statically typed language!

So, I've chosen a layered approach to Python / FastAPI / Pydantic typing. As a project, the typing should be applied where it will provide the most benefits first, and then proceed through the codebase layers applying it where it is beneficial. There is probably a limit to the this, where the cost exceeds the benefit.

The most benefit is at the API boundary, the parameters and results; and here the most benefit is in the parameters. The parameters are provided from outside the system, so strict typing provides both clarity in documentation and automatic validation and "cleansing" of data entering the system. This typing is nearly forced upon us by FastAPI, although there are ways to skirt it.

When adding typing there are even still more layers. Pydantic typing applied by FastAPI ensures that data adheres to the general data types and container structures. However, it also supports validation, so numeric rangers, string formats, enumeration ranges, and more!, may be applied to ensure data is even more compliant.

For API methods, the return values can also be typed. This is beneficial in the same way inputs are, but it could be said that the validity of return values should be more trusted, as it is programmatically determined.

Another way of stating this could be that external data is untrusted, internal data should be trusted.

Still, given that one of the purposes of using Python is to create a lower barrier of entry for developer participation, having a gatekeeper for api output serves the same preventative purpose as unit testing ... it makes it harder to emit data that violates the intended kind, whether intentional or not.

