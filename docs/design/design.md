# Design of ORCIDLink

This is a KBase core service that does not follow the kb-sdk architecture or tooling.

> In case there are remnants of kb-sdk tooling or language, this is due to the service having started out life as a dynamic service for prototyping.

## Why Diverge from kb-sdk?

There are several reasons to diverge from the KBase SDK:
- The sdk is quite out of date in terms of Python support and base OS
- Advances in the Python http service ecosystem has brought forth improvements beyond what the kb-sdk provides:
  - type hinting
  - Pydantic data type classes
  - FastAPI, providing:
    - automatic api documentation generation
    - easy REST api building
  
In addition, this service would need to support more than one browser-interactive endpoint to support three-legged OAuth integration with ORCID. Although it is certain feasible to support both JSON-RPC, as is required for a strictly kb-sdk service, as well as REST-like or browser-interactive endpoints, it would make the codebase more complex and difficult to understand.

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

## Configuration

Several features require information from the service configuration in order to function. As with all KBase services, this service has a configuration template which is used to generate a configuration file in the context of certain configuration variables.

Overall, however, the following attributes are important for the nature of this service:

- configuration depends on a set of environment variables
- configuration is required for all api calls to external services
- configuration is required for usage of the storage mechanism (database)

### Environment Variables

The configuration template (`etc/config.toml.jinja`) requires a set of environment variables in order to render to a resulting configuration file.

See [the configuration doc](../operation/configuration.md) for details. 

### External Services

This service contacts the following external services:
- KBase authentication (auth2)
- ORCID API
- ORCID OAuth

Each of these services has its own unique API technique (although all are http-based), types of error handling, and error responses.

Service code should be designed to recognize the fact of an error, unpack the error information, and raise an internal exception object which provides an error as defined by this service, but which captures some or all of the original error information.

Generally the service does not attempt to determine the cause of the external error, but rather capture the error information so that it may be reported back to the user, logged, etc.

In some cases we do need to interpret the nature of the error. 

### Storage Model

The service requires some way of storing data persistently - a temporary linking session and a permanent link record. 

The service was originally developed with a simple file-based storage model, to reduce the number of dependencies and to be able to directly observe the data as it was being populated. However, the mature service uses mongodb, and for a time both mechanisms were supported. In fact, for a time a mock mongo client (`mongomock`) was utilized, we there were three available storage mechanisms. Thus, the `storage model` is actually a shell which returns the desired storage model.
 
Although it is not anticipated that a different storage mechanism will be utilized, the abili
