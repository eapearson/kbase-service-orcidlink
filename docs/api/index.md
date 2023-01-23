# ORCID Link Service


0.1.0
The *ORCID Link Service* provides an API to enable the creation of an interface for a KBase
 user to link their KBase account to their ORCID account.

Once connected, *ORCID Link* enables certain integrations, including:

- syncing your KBase profile from your ORCID profile
- creating and managing KBase public Narratives within your ORCID profile
## misc


Miscellaneous operations
#### GET /status


Get the current status of the service.

This endpoint returns the status of the service (by definition "ok" if
it is running!), the current time, and the start time.

It can be used as a healthcheck, for basic latency performance (as it makes no
upstream calls at all), or for time synchronization (as it returns the current time).


#### Input


*none*


#### Output


<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="8em"></th><th></th><th><img width="10em"></th><tr><th>Status Code</th><th>Description</th><th>Type</th></tr></thead><tbody><tr><td>200</td><td>Successfully returns the service status</td><td><a href="#StatusResponse">StatusResponse</a></td></tr></tbody></table>


#### GET /info


Returns basic information about the service and its runtime configuration.


#### Input


*none*


#### Output


<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="8em"></th><th></th><th><img width="10em"></th><tr><th>Status Code</th><th>Description</th><th>Type</th></tr></thead><tbody><tr><td>200</td><td>Successful Response</td><td><a href="#InfoResponse">InfoResponse</a></td></tr></tbody></table>


#### GET /docs


Provides a web interface to the auto-generated API docs.


#### Input


*none*


#### Output


<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="8em"></th><th></th><th><img width="10em"></th><tr><th>Status Code</th><th>Description</th><th>Type</th></tr></thead><tbody><tr><td>200</td><td>Successfully returned the api docs</td><td>text/html</td></tr></tbody></table>




## link


Access to and control over stored ORCID Link
#### GET /link


Return the link for the user associated with the KBase auth token passed in the "Authorization" header


#### Input


<table><thead><tr><th colspan="4"><img width="2000px"></th></tr><tr><th><img width="10em"></th><th></th><th><img width="10em"></th><th><img width="10em"></th><tr><th>Name</th><th>Description</th><th>Type</th><th>In</th></tr></thead><tbody><tr><td>authorization</td><td>KBase auth token</td><td>string</td><td>header</td></tr></tbody></table>


#### Output


<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="8em"></th><th></th><th><img width="10em"></th><tr><th>Status Code</th><th>Description</th><th>Type</th></tr></thead><tbody><tr><td>200</td><td>Returns the scrubbed link record for this user; contains no secrets</td><td><a href="#LinkRecordPublic">LinkRecordPublic</a></td></tr><tr><td>401</td><td>KBase auth token absent</td><td><a href="#ErrorResponse">ErrorResponse</a></td></tr><tr><td>403</td><td>KBase auth token invalid</td><td><a href="#ErrorResponse">ErrorResponse</a></td></tr><tr><td>422</td><td>Either input or output data does not comply with the API schema</td><td><a href="#ErrorResponse">ErrorResponse</a></td></tr><tr><td>404</td><td>Link not available for this user</td><td><a href="#ErrorResponse">ErrorResponse</a></td></tr></tbody></table>


#### DELETE /link


Removes the link for the user associated with the KBase auth token passed in the "Authorization" header


#### Input


<table><thead><tr><th colspan="4"><img width="2000px"></th></tr><tr><th><img width="10em"></th><th></th><th><img width="10em"></th><th><img width="10em"></th><tr><th>Name</th><th>Description</th><th>Type</th><th>In</th></tr></thead><tbody><tr><td>authorization</td><td>KBase auth token</td><td>string</td><td>header</td></tr></tbody></table>


#### Output


<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="8em"></th><th></th><th><img width="10em"></th><tr><th>Status Code</th><th>Description</th><th>Type</th></tr></thead><tbody><tr><td>204</td><td>Successfully deleted the link</td><td><i>none</i></td></tr><tr><td>401</td><td>KBase auth token absent</td><td><a href="#ErrorResponse">ErrorResponse</a></td></tr><tr><td>403</td><td>KBase auth token invalid</td><td><a href="#ErrorResponse">ErrorResponse</a></td></tr><tr><td>422</td><td>Either input or output data does not comply with the API schema</td><td><a href="#ErrorResponse">ErrorResponse</a></td></tr><tr><td>404</td><td>Link not available for this user</td><td><a href="#ErrorResponse">ErrorResponse</a></td></tr></tbody></table>


#### GET /link/is_linked


Determine if the user associated with the KBase auth token in the "Authorization" header has a
link to an ORCID account.


#### Input


<table><thead><tr><th colspan="4"><img width="2000px"></th></tr><tr><th><img width="10em"></th><th></th><th><img width="10em"></th><th><img width="10em"></th><tr><th>Name</th><th>Description</th><th>Type</th><th>In</th></tr></thead><tbody><tr><td>authorization</td><td>KBase auth token</td><td>string</td><td>header</td></tr></tbody></table>


#### Output


<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="8em"></th><th></th><th><img width="10em"></th><tr><th>Status Code</th><th>Description</th><th>Type</th></tr></thead><tbody><tr><td>200</td><td>Returns a boolean indicating whether the user account is linked to ORCID</td><td>boolean</td></tr><tr><td>401</td><td>KBase auth token absent</td><td><a href="#ErrorResponse">ErrorResponse</a></td></tr><tr><td>403</td><td>KBase auth token invalid</td><td><a href="#ErrorResponse">ErrorResponse</a></td></tr><tr><td>422</td><td>Either input or output data does not comply with the API schema</td><td><a href="#ErrorResponse">ErrorResponse</a></td></tr></tbody></table>




## linking-sessions


OAuth integration and internal support for creating ORCID Links
#### POST /linking-sessions


Create Linking Session

Creates a new "linking session"; resulting in a linking session created in the database, and the id for it
returned for usage in an interactive linking session.


#### Input


<table><thead><tr><th colspan="4"><img width="2000px"></th></tr><tr><th><img width="10em"></th><th></th><th><img width="10em"></th><th><img width="10em"></th><tr><th>Name</th><th>Description</th><th>Type</th><th>In</th></tr></thead><tbody><tr><td>authorization</td><td>KBase auth token</td><td>string</td><td>header</td></tr></tbody></table>


#### Output


<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="8em"></th><th></th><th><img width="10em"></th><tr><th>Status Code</th><th>Description</th><th>Type</th></tr></thead><tbody><tr><td>201</td><td>The linking session has been successfully created</td><td><a href="#CreateLinkingSessionResult">CreateLinkingSessionResult</a></td></tr><tr><td>401</td><td>KBase auth token absent</td><td><a href="#ErrorResponse">ErrorResponse</a></td></tr><tr><td>403</td><td>KBase auth token invalid</td><td><a href="#ErrorResponse">ErrorResponse</a></td></tr><tr><td>422</td><td>Either input or output data does not comply with the API schema</td><td><a href="#ErrorResponse">ErrorResponse</a></td></tr></tbody></table>


#### GET /linking-sessions/{session_id}


Get Linking Session

Returns the linking session record identified by the linking session id provided in
the url, as long as it is owned by the user associated with the provided
KBase auth token.

This endpoint is designed bo be used in the implementation of the
OAuth for whose purpose is to create an ORCID Link.


#### Input


<table><thead><tr><th colspan="4"><img width="2000px"></th></tr><tr><th><img width="10em"></th><th></th><th><img width="10em"></th><th><img width="10em"></th><tr><th>Name</th><th>Description</th><th>Type</th><th>In</th></tr></thead><tbody><tr><td>session_id</td><td>n/a</td><td>string</td><td>path</td></tr><tr><td>authorization</td><td>KBase auth token</td><td>string</td><td>header</td></tr></tbody></table>


#### Output


<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="8em"></th><th></th><th><img width="10em"></th><tr><th>Status Code</th><th>Description</th><th>Type</th></tr></thead><tbody><tr><td>200</td><td>Returns the current linking session, scrubbed of private info</td><td><div><i>Any Of</i></div><div><a href="#LinkingSessionComplete">LinkingSessionComplete</a></div><div><a href="#LinkingSessionStarted">LinkingSessionStarted</a></div><div><a href="#LinkingSessionInitial">LinkingSessionInitial</a></div></td></tr><tr><td>401</td><td>KBase auth token absent</td><td><a href="#ErrorResponse">ErrorResponse</a></td></tr><tr><td>403</td><td>Username does not match linking session</td><td><a href="#ErrorResponse">ErrorResponse</a></td></tr><tr><td>422</td><td>Either input or output data does not comply with the API schema</td><td><a href="#ErrorResponse">ErrorResponse</a></td></tr><tr><td>404</td><td>Linking session not found</td><td><a href="#ErrorResponse">ErrorResponse</a></td></tr></tbody></table>


#### DELETE /linking-sessions/{session_id}


Delete Linking Session

Deletes the linking session record associated with the session id provided
in the url, as long as it is owned by the user associated with the provided
KBase auth token.

This endpoint is designed bo be used in the implementation of the
OAuth for whose purpose is to create an ORCID Link.


#### Input


<table><thead><tr><th colspan="4"><img width="2000px"></th></tr><tr><th><img width="10em"></th><th></th><th><img width="10em"></th><th><img width="10em"></th><tr><th>Name</th><th>Description</th><th>Type</th><th>In</th></tr></thead><tbody><tr><td>session_id</td><td>n/a</td><td>string</td><td>path</td></tr><tr><td>authorization</td><td>KBase auth token</td><td>string</td><td>header</td></tr></tbody></table>


#### Output


<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="8em"></th><th></th><th><img width="10em"></th><tr><th>Status Code</th><th>Description</th><th>Type</th></tr></thead><tbody><tr><td>204</td><td>Successfully deleted the session</td><td><i>none</i></td></tr><tr><td>401</td><td>KBase auth token absent</td><td><a href="#ErrorResponse">ErrorResponse</a></td></tr><tr><td>403</td><td>Username does not match linking session</td><td><a href="#ErrorResponse">ErrorResponse</a></td></tr><tr><td>422</td><td>Either input or output data does not comply with the API schema</td><td><a href="#ErrorResponse">ErrorResponse</a></td></tr><tr><td>404</td><td>Linking session not found</td><td><a href="#ErrorResponse">ErrorResponse</a></td></tr></tbody></table>


#### PUT /linking-sessions/{session_id}/finish


Finish Linking Session

The final stage of the interactive linking session; called when the user confirms the creation
of the link, after OAuth flow has finished.


#### Input


<table><thead><tr><th colspan="4"><img width="2000px"></th></tr><tr><th><img width="10em"></th><th></th><th><img width="10em"></th><th><img width="10em"></th><tr><th>Name</th><th>Description</th><th>Type</th><th>In</th></tr></thead><tbody><tr><td>session_id</td><td>n/a</td><td>string</td><td>path</td></tr><tr><td>authorization</td><td>KBase auth token</td><td>string</td><td>header</td></tr></tbody></table>


#### Output


<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="8em"></th><th></th><th><img width="10em"></th><tr><th>Status Code</th><th>Description</th><th>Type</th></tr></thead><tbody><tr><td>200</td><td>The linking session has been finished successfully</td><td><a href="#SimpleSuccess">SimpleSuccess</a></td></tr><tr><td>401</td><td>KBase auth token absent</td><td><a href="#ErrorResponse">ErrorResponse</a></td></tr><tr><td>403</td><td>Username does not match linking session</td><td><a href="#ErrorResponse">ErrorResponse</a></td></tr><tr><td>422</td><td>Either input or output data does not comply with the API schema</td><td><a href="#ErrorResponse">ErrorResponse</a></td></tr><tr><td>404</td><td>Linking session not found</td><td><a href="#ErrorResponse">ErrorResponse</a></td></tr></tbody></table>


#### GET /linking-sessions/{session_id}/oauth/start


Start Linking Session

This endpoint is designed to be used directly by the browser. It is the "start"
of the ORCID OAuth flow. If the provided session id is found and the associated
session record is still in the initial state, it will initiate the OAuth flow
by redirecting the browser to an endpoint at ORCID.

Starts a "linking session", an interactive OAuth flow the end result of which is an access_token stored at
KBase for future use by the user.


#### Input


<table><thead><tr><th colspan="4"><img width="2000px"></th></tr><tr><th><img width="10em"></th><th></th><th><img width="10em"></th><th><img width="10em"></th><tr><th>Name</th><th>Description</th><th>Type</th><th>In</th></tr></thead><tbody><tr><td>session_id</td><td>n/a</td><td>string</td><td>path</td></tr><tr><td>return_link</td><td>A url to redirect to after the entire linking is complete; not to be confused with the ORCID OAuth flow's redirect_url</td><td>string</td><td>query</td></tr><tr><td>skip_prompt</td><td>Whether to prompt for confirmation of linking; setting</td><td>string</td><td>query</td></tr><tr><td>kbase_session</td><td>KBase auth token taken from a cookie</td><td>string</td><td>cookie</td></tr><tr><td>kbase_session_backup</td><td>KBase auth token taken from a cookie</td><td>string</td><td>cookie</td></tr></tbody></table>


#### Output


<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="8em"></th><th></th><th><img width="10em"></th><tr><th>Status Code</th><th>Description</th><th>Type</th></tr></thead><tbody><tr><td>302</td><td>Redirect to ORCID if a valid linking session</td><td><i>none</i></td></tr><tr><td>401</td><td>KBase auth token absent</td><td><a href="#ErrorResponse">ErrorResponse</a></td></tr><tr><td>403</td><td>KBase auth token invalid</td><td><a href="#ErrorResponse">ErrorResponse</a></td></tr><tr><td>422</td><td>Either input or output data does not comply with the API schema</td><td><a href="#ErrorResponse">ErrorResponse</a></td></tr><tr><td>404</td><td>Response when a linking session not found for the supplied session id</td><td><a href="#ErrorResponse">ErrorResponse</a></td></tr></tbody></table>


#### GET /linking-sessions/oauth/continue


Continue Linking Session

This endpoint implements the end point for the ORCID OAuth flow. That is, it
serves as the redirection target after the user has successfully completed
their interaction with ORCID, at which they may have logged in and provided
their consent to issuing the linking token to KBase.

Note that since this is an "interactive" endpoint, which does not have its own
user interface, rather redirects to kbase-ui when finished. This applies to
errors as well. Errors are displayed by redirecting the browser to an endpoint
in kbase-ui which is designed to expect the error values for display to be
in the url itself.


#### Input


<table><thead><tr><th colspan="4"><img width="2000px"></th></tr><tr><th><img width="10em"></th><th></th><th><img width="10em"></th><th><img width="10em"></th><tr><th>Name</th><th>Description</th><th>Type</th><th>In</th></tr></thead><tbody><tr><td>code</td><td>n/a</td><td>string</td><td>query</td></tr><tr><td>state</td><td>n/a</td><td>string</td><td>query</td></tr><tr><td>error</td><td>n/a</td><td>string</td><td>query</td></tr><tr><td>kbase_session</td><td>KBase auth token taken from a cookie</td><td>string</td><td>cookie</td></tr><tr><td>kbase_session_backup</td><td>KBase auth token taken from a cookie</td><td>string</td><td>cookie</td></tr></tbody></table>


#### Output


<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="8em"></th><th></th><th><img width="10em"></th><tr><th>Status Code</th><th>Description</th><th>Type</th></tr></thead><tbody><tr><td>302</td><td>Redirect to the continuation page; or error page</td><td><i>none</i></td></tr><tr><td>401</td><td>Linking requires authorization; same meaning as standard auth 401, but caught and issued in a different manner</td><td><i>none</i></td></tr><tr><td>403</td><td>KBase auth token invalid</td><td><a href="#ErrorResponse">ErrorResponse</a></td></tr><tr><td>422</td><td>Either input or output data does not comply with the API schema</td><td><a href="#ErrorResponse">ErrorResponse</a></td></tr></tbody></table>




## orcid


Direct access to ORCID via ORCID Link
#### GET /orcid/profile


Get the ORCID profile for the user associated with the current auth token.

Returns a 404 Not Found if the user is not linked


#### Input


<table><thead><tr><th colspan="4"><img width="2000px"></th></tr><tr><th><img width="10em"></th><th></th><th><img width="10em"></th><th><img width="10em"></th><tr><th>Name</th><th>Description</th><th>Type</th><th>In</th></tr></thead><tbody><tr><td>authorization</td><td>KBase auth token</td><td>string</td><td>header</td></tr></tbody></table>


#### Output


<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="8em"></th><th></th><th><img width="10em"></th><tr><th>Status Code</th><th>Description</th><th>Type</th></tr></thead><tbody><tr><td>200</td><td>Successful Response</td><td><a href="#ORCIDProfile">ORCIDProfile</a></td></tr><tr><td>404</td><td>User not linked or ORCID profile not available.</td><td><i>none</i></td></tr><tr><td>401</td><td>KBase auth token absent</td><td><a href="#ErrorResponse">ErrorResponse</a></td></tr><tr><td>403</td><td>KBase auth token invalid</td><td><a href="#ErrorResponse">ErrorResponse</a></td></tr><tr><td>422</td><td>Either input or output data does not comply with the API schema</td><td><a href="#ErrorResponse">ErrorResponse</a></td></tr></tbody></table>




## works


Add, remove, update 'works' records for a user's ORCID Account
#### GET /works/{put_code}


Fetch the work record, identified by `put_code`, for the user associated with the KBase auth token provided in the `Authorization` header


#### Input


<table><thead><tr><th colspan="4"><img width="2000px"></th></tr><tr><th><img width="10em"></th><th></th><th><img width="10em"></th><th><img width="10em"></th><tr><th>Name</th><th>Description</th><th>Type</th><th>In</th></tr></thead><tbody><tr><td>put_code</td><td>The ORCID `put code` for the work record to fetch</td><td>integer</td><td>path</td></tr><tr><td>authorization</td><td>Kbase auth token</td><td>string</td><td>header</td></tr></tbody></table>


#### Output


<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="8em"></th><th></th><th><img width="10em"></th><tr><th>Status Code</th><th>Description</th><th>Type</th></tr></thead><tbody><tr><td>200</td><td>Successful Response</td><td><a href="#ORCIDWork">ORCIDWork</a></td></tr><tr><td>404</td><td>Link not available for this user</td><td><i>none</i></td></tr><tr><td>401</td><td>Token missing or invalid</td><td><i>none</i></td></tr><tr><td>422</td><td>Either input or output data does not comply with the API schema</td><td><a href="#ErrorResponse">ErrorResponse</a></td></tr></tbody></table>


#### DELETE /works/{put_code}


n/a


#### Input


<table><thead><tr><th colspan="4"><img width="2000px"></th></tr><tr><th><img width="10em"></th><th></th><th><img width="10em"></th><th><img width="10em"></th><tr><th>Name</th><th>Description</th><th>Type</th><th>In</th></tr></thead><tbody><tr><td>put_code</td><td>n/a</td><td>integer</td><td>path</td></tr><tr><td>authorization</td><td>Kbase auth token</td><td>string</td><td>header</td></tr></tbody></table>


#### Output


<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="8em"></th><th></th><th><img width="10em"></th><tr><th>Status Code</th><th>Description</th><th>Type</th></tr></thead><tbody><tr><td>200</td><td>Successful Response</td><td><a href="#SimpleSuccess">SimpleSuccess</a></td></tr><tr><td>404</td><td>Not found</td><td><i>none</i></td></tr><tr><td>422</td><td>Validation Error</td><td><a href="#HTTPValidationError">HTTPValidationError</a></td></tr></tbody></table>


#### GET /works


Fetch all of the "work" records from a user's ORCID account if their KBase account is linked.


#### Input


<table><thead><tr><th colspan="4"><img width="2000px"></th></tr><tr><th><img width="10em"></th><th></th><th><img width="10em"></th><th><img width="10em"></th><tr><th>Name</th><th>Description</th><th>Type</th><th>In</th></tr></thead><tbody><tr><td>authorization</td><td>Kbase auth token</td><td>string</td><td>header</td></tr></tbody></table>


#### Output


<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="8em"></th><th></th><th><img width="10em"></th><tr><th>Status Code</th><th>Description</th><th>Type</th></tr></thead><tbody><tr><td>200</td><td>Successful Response</td><td>array</td></tr><tr><td>404</td><td>Link not available for this user</td><td><i>none</i></td></tr><tr><td>401</td><td>Token missing or invalid</td><td><i>none</i></td></tr><tr><td>422</td><td>Either input or output data does not comply with the API schema</td><td><a href="#ErrorResponse">ErrorResponse</a></td></tr></tbody></table>


#### PUT /works


Update a work record; the `work_update` contains the `put code`.


#### Input


<table><thead><tr><th colspan="4"><img width="2000px"></th></tr><tr><th><img width="10em"></th><th></th><th><img width="10em"></th><th><img width="10em"></th><tr><th>Name</th><th>Description</th><th>Type</th><th>In</th></tr></thead><tbody><tr><td>authorization</td><td>Kbase auth token</td><td>string</td><td>header</td></tr></tbody></table>


#### Output


<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="8em"></th><th></th><th><img width="10em"></th><tr><th>Status Code</th><th>Description</th><th>Type</th></tr></thead><tbody><tr><td>200</td><td>Successful Response</td><td><a href="#ORCIDWork">ORCIDWork</a></td></tr><tr><td>404</td><td>Link not available for this user</td><td><i>none</i></td></tr><tr><td>401</td><td>Token missing or invalid</td><td><i>none</i></td></tr><tr><td>422</td><td>Either input or output data does not comply with the API schema</td><td><a href="#ErrorResponse">ErrorResponse</a></td></tr></tbody></table>


#### POST /works


n/a


#### Input


<table><thead><tr><th colspan="4"><img width="2000px"></th></tr><tr><th><img width="10em"></th><th></th><th><img width="10em"></th><th><img width="10em"></th><tr><th>Name</th><th>Description</th><th>Type</th><th>In</th></tr></thead><tbody><tr><td>authorization</td><td>n/a</td><td>string</td><td>header</td></tr></tbody></table>


#### Output


<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="8em"></th><th></th><th><img width="10em"></th><tr><th>Status Code</th><th>Description</th><th>Type</th></tr></thead><tbody><tr><td>200</td><td>Successful Response</td><td><a href="#ORCIDWork">ORCIDWork</a></td></tr><tr><td>404</td><td>Not found</td><td><i>none</i></td></tr><tr><td>422</td><td>Validation Error</td><td><a href="#HTTPValidationError">HTTPValidationError</a></td></tr></tbody></table>




##### Auth2Service


<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th></th><th><img width="15em"></th><th><img width="5em"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>url</td><td>string</td><td>✓</td></tr><tr><td>tokenCacheLifetime</td><td>integer</td><td>✓</td></tr><tr><td>tokenCacheMaxSize</td><td>integer</td><td>✓</td></tr></tbody></table>


##### Config


<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th></th><th><img width="15em"></th><th><img width="5em"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>services</td><td><a href="#Services">Services</a></td><td>✓</td></tr><tr><td>ui</td><td><a href="#UIConfig">UIConfig</a></td><td>✓</td></tr><tr><td>orcid</td><td><a href="#ORCIDConfig">ORCIDConfig</a></td><td>✓</td></tr><tr><td>mongo</td><td><a href="#MongoConfig">MongoConfig</a></td><td>✓</td></tr><tr><td>module</td><td><a href="#ModuleConfig">ModuleConfig</a></td><td>✓</td></tr></tbody></table>


##### CreateLinkingSessionResult


<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th></th><th><img width="15em"></th><th><img width="5em"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>session_id</td><td>string</td><td>✓</td></tr></tbody></table>


##### ErrorResponse


<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th></th><th><img width="15em"></th><th><img width="5em"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>code</td><td>string</td><td>✓</td></tr><tr><td>title</td><td>string</td><td>✓</td></tr><tr><td>message</td><td>string</td><td>✓</td></tr><tr><td>data</td><td>n/a</td><td></td></tr></tbody></table>


##### ExternalId


<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th></th><th><img width="15em"></th><th><img width="5em"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>type</td><td>string</td><td>✓</td></tr><tr><td>value</td><td>string</td><td>✓</td></tr><tr><td>url</td><td>string</td><td>✓</td></tr><tr><td>relationship</td><td>string</td><td>✓</td></tr></tbody></table>


##### HTTPValidationError


<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th></th><th><img width="15em"></th><th><img width="5em"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>detail</td><td>array</td><td></td></tr></tbody></table>


##### InfoResponse


<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th></th><th><img width="15em"></th><th><img width="5em"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>kbase_sdk_config</td><td><a href="#KBaseSDKConfig">KBaseSDKConfig</a></td><td>✓</td></tr><tr><td>config</td><td><a href="#Config">Config</a></td><td>✓</td></tr></tbody></table>


##### KBaseSDKConfig


<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th></th><th><img width="15em"></th><th><img width="5em"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>module-name</td><td>string</td><td>✓</td></tr><tr><td>module-description</td><td>string</td><td>✓</td></tr><tr><td>service-language</td><td>string</td><td>✓</td></tr><tr><td>module-version</td><td>string</td><td>✓</td></tr><tr><td>owners</td><td>array</td><td>✓</td></tr><tr><td>service-config</td><td><a href="#KBaseServiceConfig">KBaseServiceConfig</a></td><td>✓</td></tr></tbody></table>


##### KBaseServiceConfig


<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th></th><th><img width="15em"></th><th><img width="5em"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>dynamic-service</td><td>boolean</td><td>✓</td></tr></tbody></table>


##### LinkRecordPublic


<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th></th><th><img width="15em"></th><th><img width="5em"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>username</td><td>string</td><td>✓</td></tr><tr><td>created_at</td><td>integer</td><td>✓</td></tr><tr><td>expires_at</td><td>integer</td><td>✓</td></tr><tr><td>orcid_auth</td><td><a href="#ORCIDAuthPublic">ORCIDAuthPublic</a></td><td>✓</td></tr></tbody></table>


##### LinkingSessionComplete


<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th></th><th><img width="15em"></th><th><img width="5em"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>session_id</td><td>string</td><td>✓</td></tr><tr><td>username</td><td>string</td><td>✓</td></tr><tr><td>created_at</td><td>integer</td><td>✓</td></tr><tr><td>expires_at</td><td>integer</td><td>✓</td></tr><tr><td>return_link</td><td>string</td><td>✓</td></tr><tr><td>skip_prompt</td><td>string</td><td>✓</td></tr><tr><td>orcid_auth</td><td><a href="#ORCIDAuth">ORCIDAuth</a></td><td>✓</td></tr></tbody></table>


##### LinkingSessionInitial


<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th></th><th><img width="15em"></th><th><img width="5em"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>session_id</td><td>string</td><td>✓</td></tr><tr><td>username</td><td>string</td><td>✓</td></tr><tr><td>created_at</td><td>integer</td><td>✓</td></tr><tr><td>expires_at</td><td>integer</td><td>✓</td></tr></tbody></table>


##### LinkingSessionStarted


<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th></th><th><img width="15em"></th><th><img width="5em"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>session_id</td><td>string</td><td>✓</td></tr><tr><td>username</td><td>string</td><td>✓</td></tr><tr><td>created_at</td><td>integer</td><td>✓</td></tr><tr><td>expires_at</td><td>integer</td><td>✓</td></tr><tr><td>return_link</td><td>string</td><td>✓</td></tr><tr><td>skip_prompt</td><td>string</td><td>✓</td></tr></tbody></table>


##### ModuleConfig


<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th></th><th><img width="15em"></th><th><img width="5em"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>serviceRequestTimeout</td><td>integer</td><td>✓</td></tr></tbody></table>


##### MongoConfig


<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th></th><th><img width="15em"></th><th><img width="5em"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>host</td><td>string</td><td>✓</td></tr><tr><td>port</td><td>integer</td><td>✓</td></tr><tr><td>database</td><td>string</td><td>✓</td></tr><tr><td>username</td><td>string</td><td>✓</td></tr><tr><td>password</td><td>string</td><td>✓</td></tr></tbody></table>


##### NewWork


<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th></th><th><img width="15em"></th><th><img width="5em"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>title</td><td>string</td><td>✓</td></tr><tr><td>journal</td><td>string</td><td>✓</td></tr><tr><td>date</td><td>string</td><td>✓</td></tr><tr><td>workType</td><td>string</td><td>✓</td></tr><tr><td>url</td><td>string</td><td>✓</td></tr><tr><td>externalIds</td><td>array</td><td>✓</td></tr></tbody></table>


##### ORCIDAffiliation


<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th></th><th><img width="15em"></th><th><img width="5em"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>name</td><td>string</td><td>✓</td></tr><tr><td>role</td><td>string</td><td>✓</td></tr><tr><td>startYear</td><td>string</td><td>✓</td></tr><tr><td>endYear</td><td>string</td><td></td></tr></tbody></table>


##### ORCIDAuth


<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th></th><th><img width="15em"></th><th><img width="5em"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>access_token</td><td>string</td><td>✓</td></tr><tr><td>token_type</td><td>string</td><td>✓</td></tr><tr><td>refresh_token</td><td>string</td><td>✓</td></tr><tr><td>expires_in</td><td>integer</td><td>✓</td></tr><tr><td>scope</td><td>string</td><td>✓</td></tr><tr><td>name</td><td>string</td><td>✓</td></tr><tr><td>orcid</td><td>string</td><td>✓</td></tr><tr><td>id_token</td><td>string</td><td>✓</td></tr></tbody></table>


##### ORCIDAuthPublic


<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th></th><th><img width="15em"></th><th><img width="5em"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>name</td><td>string</td><td>✓</td></tr><tr><td>scope</td><td>string</td><td>✓</td></tr><tr><td>expires_in</td><td>integer</td><td>✓</td></tr><tr><td>orcid</td><td>string</td><td>✓</td></tr></tbody></table>


##### ORCIDConfig


<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th></th><th><img width="15em"></th><th><img width="5em"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>oauthBaseURL</td><td>string</td><td>✓</td></tr><tr><td>apiBaseURL</td><td>string</td><td>✓</td></tr><tr><td>clientId</td><td>string</td><td>✓</td></tr><tr><td>clientSecret</td><td>string</td><td>✓</td></tr></tbody></table>


##### ORCIDLinkService


<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th></th><th><img width="15em"></th><th><img width="5em"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>url</td><td>string</td><td>✓</td></tr></tbody></table>


##### ORCIDProfile


<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th></th><th><img width="15em"></th><th><img width="5em"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>orcidId</td><td>string</td><td>✓</td></tr><tr><td>firstName</td><td>string</td><td>✓</td></tr><tr><td>lastName</td><td>string</td><td>✓</td></tr><tr><td>bio</td><td>string</td><td>✓</td></tr><tr><td>affiliations</td><td>array</td><td>✓</td></tr><tr><td>works</td><td>array</td><td>✓</td></tr><tr><td>emailAddresses</td><td>array</td><td>✓</td></tr></tbody></table>


##### ORCIDWork


<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th></th><th><img width="15em"></th><th><img width="5em"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>putCode</td><td>string</td><td>✓</td></tr><tr><td>createdAt</td><td>integer</td><td>✓</td></tr><tr><td>updatedAt</td><td>integer</td><td>✓</td></tr><tr><td>source</td><td>string</td><td>✓</td></tr><tr><td>title</td><td>string</td><td>✓</td></tr><tr><td>journal</td><td>string</td><td></td></tr><tr><td>date</td><td>string</td><td>✓</td></tr><tr><td>workType</td><td>string</td><td>✓</td></tr><tr><td>url</td><td>string</td><td>✓</td></tr><tr><td>externalIds</td><td>array</td><td>✓</td></tr></tbody></table>


##### Services


<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th></th><th><img width="15em"></th><th><img width="5em"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>Auth2</td><td><a href="#Auth2Service">Auth2Service</a></td><td>✓</td></tr><tr><td>ORCIDLink</td><td><a href="#ORCIDLinkService">ORCIDLinkService</a></td><td>✓</td></tr></tbody></table>


##### SimpleSuccess


<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th></th><th><img width="15em"></th><th><img width="5em"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>ok</td><td>boolean</td><td>✓</td></tr></tbody></table>


##### StatusResponse


<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th></th><th><img width="15em"></th><th><img width="5em"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>status</td><td>string</td><td>✓</td></tr><tr><td>time</td><td>integer</td><td>✓</td></tr><tr><td>start_time</td><td>integer</td><td>✓</td></tr></tbody></table>


##### UIConfig


<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th></th><th><img width="15em"></th><th><img width="5em"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>origin</td><td>string</td><td>✓</td></tr></tbody></table>


##### ValidationError


<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th></th><th><img width="15em"></th><th><img width="5em"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>loc</td><td>array</td><td>✓</td></tr><tr><td>msg</td><td>string</td><td>✓</td></tr><tr><td>type</td><td>string</td><td>✓</td></tr></tbody></table>


##### WorkUpdate


<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th></th><th><img width="15em"></th><th><img width="5em"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>putCode</td><td>integer</td><td>✓</td></tr><tr><td>title</td><td>string</td><td></td></tr><tr><td>journal</td><td>string</td><td></td></tr><tr><td>date</td><td>string</td><td></td></tr><tr><td>workType</td><td>string</td><td></td></tr><tr><td>url</td><td>string</td><td></td></tr><tr><td>externalIds</td><td>array</td><td></td></tr></tbody></table>


-fin-