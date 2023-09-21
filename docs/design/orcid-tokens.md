# ORCID Tokens

ORCID tokens are assigned during the final "token exchange" phase of the 3-legged oauth flow process. Specifically, the following structure is returned from ORCID:

```python
class ORCIDAuth(ServiceBaseModel):
    access_token: str 
    token_type: str 
    refresh_token: str 
    expires_in: int 
    scope: str 
    name: str
    orcid: str
```

Three tokens are provided, of which we use two:

- `access_token` is the primary token we use for interacting with the ORCID API on behalf of a user. This token will expire after 20 years, although other events may cause it to become invalid before then. 
	- OAUTH 2.0 Spec: https://oauth.net/2/access-tokens/

- `refresh_token` serve the sole purpose of obtaining additional tokens (access, refresh) from the ORCID API. The lifetime of a refresh token is intentionally not published
	- OAUTH 2.0 Spec - https://oauth.net/2/refresh-tokens/

- `id_token` is a Java Web Token (JWT) meant to convey that the user controlling the OAUTH session has been identified (authenticated); we don't use this in ORCID Link
	- OAUTH 2.0 Spec - https://oauth.net/id-tokens-vs-access-tokens/)
	
	
Although the `access_token` has a 20 year lifespan, there are conditions under which it may become invalidated at any time. This is where the `refresh_token` steps in. If the `access_token` is found to be invalid, the `refresh_token` may be used to obtain a new one, without intervention from the user. That is, unlike the initial OAUTH process to obtain the set of tokens which does require the user to be in control, getting a new access token from a refresh token does not. This allows the ORCID Link process to manage various token scenarios automatically.

Let's review those scenarios:

## Token Invalidation Scenarios

Generally there are two types of scenarios:

- access token becomes invalid, and a new one may be obtained with the refresh token
- access token becomes invalid, refresh token is invalid, and the user must engage in the OAUTH flow to obtain a new set of tokens


In the first scenario, the ORCID Link service can intervene without the user even being aware of it. In the second, the the ORCID Link ui must lead the user through the ORCID OAuth flow to obtain a new set of tokens - they must re-link to ORCID.

### `access_token` expires at end of lifetime as specified by ORCID

If a token should live to the ripe age of 20 years, it will be cease to function. When this occurs or is imminent, the ORCID Link service may obtain a new, fresh set of tokens through the ORCID OAuth api by providing the refresh token.

The expiration date is known to the ORCID Link service, because it is provided along with the tokens in the `expires_in` field. Thus the ORCID Link service may have an opportunity to detect that the access token will expire soon, and intervene to obtain a new one before this occurs.

The ORCID Link service could also ignore this date (see below why we may want to do this), and simply attempt to obtain a new set of tokens if the access token is found to be invalid. We need to handle this situation in any case, as the access token may be invalidated for other reasons.

### `access_token` is considered expired by the KBase ORCID Link service

It is advised that (ref ____) by ORCID that we limit the lifespan of access tokens. That is, that we apply a lifetime to access tokens that is shorter than that assigned by ORCID, which is currently 20 years.

We treat our limit as sacred as that imposed by ORCID itself. In fact, by choosing a shorter token lifetime than that of ORCID, the ORCID limit is essentially non-functional, other than to inform us that our lifetime must be shorter than it.

At present, we do NOT have our own limit, but we will soon implement this. The time limit should be shorter than the ORCID 20 year limit, but long enough that refresh calls are not too frequent. It is common for OAuth providers to employ various techniques for determining if a token has been stolen and is being mis-used by the thief. One of these is frequent or unusual patterns of refresh token usage. So we don't want to employ, for example, a one-time-usage policy in which a new access token is obtained after one is used.

A reasonable time limit might be 2 weeks, which has the aesthetically pleasing attribute of matching our own auth (bearer) tokens.


### `access_token` has become administratively invalidated by ORCID

As mentioned above, there are conditions under which ORCID may revoke tokens administratively. Such conditions include:

- theft of tokens from ORCID
- theft of tokens from KBase
- unusual activity with an access or refresh token
- some system corruption which leads to loss of token records at ORCID

When a token has been invalidated, the ORCID Link service will not discover this fact until it attempts to use the token. (See below for conditions under which this may occur. ) When discovered, the ORCID Link service will attempt to obtain a new set of tokens via the OAuth Refresh Flow. This interaction is a simple server-server call from the KBase ORCID Link service to the ORCID OAuth service.


### User removes access for KBase

A user may remove access for KBase through their ORCID Account interface. The ORCID interface allows a user to view all 3rd parties approved for accessing their account in some manner. Such parties are referred to as "Trusted Parties".

A user may remove any Trusted Party at any time. Doing so invalidates all tokens issued to that Trusted Party. 

When attempting to access ORCID using affected tokens, the tokens will simply appear as invalid, and the a token refresh will be attempted.

### Refresh Process

So, each process above refers to engaging in the refresh process whenever it is needed?

What is the refresh process?

- KBase ORCID Link service calls the ORCID OAuth api with the appropriate parameters
- If the call is successful, KBase ORCID Link service stores the resulting tokens and related data, replacing the existing token set. (Internally we refer to this as the ORCID Auth data)
- The new access token will be thenceforth used.

This process may be a sub-component of a call from ORCID Link to the ORCID API, in which the response from the ORCID API indicates that the token is invalid (should be a 401 HTTP response code).

### Any of the above scenarios, but the `refresh_token` is also invalid

Another outcome of the Refresh process is that the refresh call itself fails! This may occur if the refresh token itself has become invalid. And this may occur for the usual reasons - the lifetime has expired, it has been administratively revoked due to security concerns, or the user has removed KBase as a trusted party.

It is notable that the refresh_token's lifetime is not known. It may be longer than the access token (20 years at time of writing). But as it is unknown, it may be expected when it is least expected - at any time.

## ORCID Link Refresh Processes to handle all this stuff

A design issue within the ORCID Link service is _when_ and _how_ to trigger the refresh process. 

Before we get to that, we should point out the underlying support for refreshing.

### ORCID OAuth API

First of all, we need to implement support for the ORCID OAuth API call to conduct a token refresh. This is a implemented in `src/orcidlink/lib/service_clients/orcid_api.py`. It is a `POST` request to the ORCID OAuth api endpoint, as described here:

https://github.com/ORCID/ORCID-Source/blob/main/orcid-api-web/tutorial/refresh_tokens.md

The request is `application/x-www-form-urlencoded` (for some reason) and accepts the following parameters:

> TODO

This call is the foundation of the refresh token exchange.

### KBase ORCID Link API

The refresh token process is invoked in two fundamental manners: directly and indirectly.

Direct invocation is available via the management interface and the user interface.

The management api call is designed to be used by the management interface in the case a manager/administrator of the service needs to immediately refresh a token, or by a maintenance script which is tasked with keeping tokens refreshed.

The user api interface is designed to be used within another user process, and not directly invoked by a user. There is nothing policy-wise wrong with a user refreshing their tokens, but exposing this may cause a user to inadvertently disable their ability to create tokens or even the ability of ORCID Link to interact with ORCID. One of the security measures taken by ORCID is to detect unusual patterns of access or refreshing. One of these patterns may be frequency. So if a user decides to refresh their token multiple times in rapid succession (or some other pattern like, say, every day), ORCID may detect this and determine that either the user's tokens and/or KBase's client credentials have been compromised. In the prior case, a user's account may be disabled (?? check w/ORCID on the impact), and in the latter, the ORCID Link client credentials may become disabled.

So, the user api is designed for indirect usage. Indirect usage means that during another process, such as fetching a user's ORCID profile for display, if the ORCID API returns an error indicating the access token is invalid, the process will attempt to refresh the tokens before proceeding. If the refresh succeeds, the process continues normally, and the user is unaware that something "special" occurred. (And if the refresh fails, they are shown an error message.)

### Maintenance

It may seem that we can rely upon indirect refreshing, as described above, with the escape hatch of an administrative refresh option.

However, there are reasons we may wish to curate user ORCID Links.

The ORCID Link is also used to expose the user's ORCID id on their user profile, if their user profile indicates this is so. When creating an ORCID Link, the user is given the option of opting out of showing their ORCID Id in their user profile. If the user does not opt out, the ORCID Id in their link will be displayed in an html link context - creating an html link to their public ORCID profile.

However, what if the user has revoked KBase's ability to access their ORCID account, but has not yet removed their ORCID Link?

For the user's interaction with KBase, the ORCID link will encounter an error (and attempt a refresh, which will also fail), and any interaction with their ORCID account will fail.

But what if the user intended to disable all KBase access to their ORCID information? We can't expect the user to understand the internals of the system, and that the KBase ORCID Link service and ORCID's services are decoupled.

A background maintenance task could help take care of this.

Imaging a task which runs periodically whose job is to inspect ORCID Link records and determine if they are still valid.

Such a task could ensure that every link's access token is valid, and if not, attempt a refresh, and if that fails, remove the link and send the user a message.

Or it could mark the link record as invalid so that the orcid id display will be disabled. The next time that user visits the ORCID Link UI, it would inform them that their link has become invalidated, and that their only choice is to remove the link, and then create a new one of they so choose.


## Ref

- [ORCID Documentation on Refresh TOkens](https://github.com/ORCID/ORCID-Source/blob/main/orcid-api-web/tutorial/refresh_tokens.md)

