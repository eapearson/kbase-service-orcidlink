# ORCID API

## Errors

We only care about a few types of errors. Any other errors are considered usage errors;
that is, errors in the service.

The errors we care about handling and communicating to the user are:

- the user's access_token is no longer valid
- the user's ORCID account has been deleted

### Invalid Token

Within the constraints of the ORCID Link service, This can occur when an ORCID
access_token has become invalid due to:

- the user removing KBase authorization from the trusted parties page
- the access token expiring (but they have a 20 year lifespan, so this is unlikely)
- the access token invalidated administratively at ORCID (this is probably quite
  rare; but is mentioned in the ORCID docs as a possibility)

As described below, these cases can be teased out of an ORCID API error response

### ORCID Account Deleted

This case is probably quite rare, but is certainly possible. There are two ways this can
occur:

- the user "deactivates" their ORCID account manually, via the ORCID UI
- the user combines accounts, leaving the linked one deactivated.

### Authorization Errors

Note that the ORCID API uses "Bearer" tokens. This means that we do not need to present
the client id or client secret to ORCID. Those credentials are only used for the ORCID OAuth API.

All of the errors we care about concern authorization. So let us explore all of the
potential use cases:

#### Bad Token

If we supply what is simply an invalid or badly formed token, something that is not and
never was a valid token, we get a 401 response with this content:

```json
{
    "error": "invalid_token",
    "error_description": "Invalid access token: foo"
}
```

e.g. with this request:

```text
curl https://api.sandbox.orcid.org/v3.0/0009-0006-1955-0944/record \
    -H 'Accept: application/vnd.orcid+json' \
    -H 'Authorization: Bearer foo'
```

#### Accessing another ORCID account with a valid access token

This would be an example of a service error, as it should never be the case that an
access token is applied to an api call to another orcid id.

Below is the error response, carried by a 401 return code.

Note a couple of interesting facts:

- the response code is 401; this is incorrect as presenting a valid token for something
  it cannot access should be a "403 Forbidden" error, as the resource will never be
  accessible with the given token.

- the form of the error is different than above; this is an annoying fact of the ORCID
  API - it has two different error formats.

```json
{
    "response-code": 401,
    "developer-message": "401 Unauthorized: The client application is not authorized for this ORCID record. Full validation error: Access token is for a different record",
    "user-message": "The client application is not authorized.",
    "error-code": 9017,
    "more-info": "https://members.orcid.org/api/resources/troubleshooting"
}
```


#### Accessing one's own account with a revoked token

This can be replicated in the context of ORCID Link by 
- creating a link
- obtaining access_code from the database
- accessing the user's profile:
    ```text
    curl https://api.sandbox.orcid.org/v3.0/0009-0006-1955-0944/record \
        -H 'Accept: application/vnd.orcid+json' \
        -H 'Authorization: Bearer foo'
    ```
- using the ORCID Link api, remove the link
- run the curl command above.
- the result below should be returned

A revoked token behaves just as for a simply invalid token, there is no way to
distinguish them. 

```json
{
    "error": "invalid_token",
    "error_description": "Invalid access token: 61372956-e143-45b3-bbad-ffc1b329f0e5"
}
```


#### Accessing one's own account with with a non-revoked token, but KBase authorization removed

In this case, the user has not directly revoked the ORCID Link, but has rather removed
KBase authorization via the ORCID UI via the "Trusted Parties" page. The ORCID Link
remains in place, with the access tokens intact. 

When we attempt to use the ORCID API with the user's access token, we get the same
response as for a bad or revoked token.


```json
{
    "error": "invalid_token",
    "error_description": "Invalid access token: 9757240f-4d65-4c88-ae47-752d1e720a91"
}
```
