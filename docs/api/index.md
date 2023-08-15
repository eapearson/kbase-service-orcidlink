<a name="header_orcid-link-service"></a>
# ORCID Link Service
<table><tr><td>version: 0.1.0</td></tr></table>


The *ORCID Link Service* provides an API to enable the linking of a KBase
 user account to an ORCID account. This "link" consists of a [Link Record](#user-content-header_type_linkrecord) which 
 contains a KBase username, ORCID id, ORCID access token, and a few other fields. This link record allows
 KBase to create tools and services which utilize the ORCID api to view or modify
 certain aspects of a users ORCID profile.

Once connected, *ORCID Link* enables certain integrations, including:

- syncing your KBase profile from your ORCID profile
- creating and managing KBase public Narratives within your ORCID profile
<a name="header_terms-of-service"></a>
## Terms of Service
<a href="https://www.kbase.us/about/terms-and-conditions-v2/">https://www.kbase.us/about/terms-and-conditions-v2/</a>
<a name="header_contact"></a>
## Contact
KBase, Lawrence Berkeley National Laboratory, DOE  
<a href="https://www.kbase.us/">https://www.kbase.us/</a>  
engage@kbase.us
<a name="header_license"></a>
## License
The MIT License
<a href="https://github.com/kbase/kb_sdk/blob/develop/LICENSE.md">https://github.com/kbase/kb_sdk/blob/develop/LICENSE.md</a>
## Usage

This document is primarily generated from the `openapi` interface generated 
by <a href="https://fastapi.tiangolo.com">FastAPI</a>.

The [Endpoints](#user-content-header_endpoints) section documents all REST endpoints, including the 
expected responses, input parameters and output JSON and type definitions.

The [Types](#user-content-header_types) section defines all of the Pydantic models used in the codebase, 
most of which are in service of the input and output types mentioned above.

### Issues

- Due to limitations of GitHub's markdown support, tables have two empty rows at the start of the header. This is due to the fact that GitHub does not allow any table formatting instructions, so we need to use the first two rows to establish the table and column widths. 

## Table of Contents    

- [Endpoints](#user-content-header_endpoints)
    - [misc](#user-content-header_misc)
    - [link](#user-content-header_link)
    - [linking-sessions](#user-content-header_linking-sessions)
    - [orcid](#user-content-header_orcid)
    - [works](#user-content-header_works)
- [Types](#user-content-header_types)
- [Glossary](#user-content-header_glossary)


<a name="header_endpoints"></a>
## Endpoints
<a name="header_misc"></a>
### misc
Miscellaneous operations
<a name="header_get-/status"></a>
#### GET /status
Get Service Status

This endpoint returns the current status of the service. The status code itself
is always "ok", by definition. Other information includes the current time, and the start time.

It can be used as a healthcheck, for basic latency measurement (as it makes no
i/o or other high-latency calls), or for time synchronization (as it returns the current time).


<a name="header_input"></a>
#### Input
*none*


<a name="header_output"></a>
#### Output
<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="150px"></th><th><img width="1000px"></th><th><img width="150px"></th><tr><th>Status Code</th><th>Description</th><th>Type</th></tr></thead><tbody><tr><td>200</td><td>Successfully returns the service status</td><td><a href="#user-content-header_type_statusresponse">StatusResponse</a></td></tr></tbody></table>


---
<a name="header_get-/info"></a>
#### GET /info
Get Service Information

Returns basic information about the service and its configuration.


<a name="header_input"></a>
#### Input
*none*


<a name="header_output"></a>
#### Output
<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="150px"></th><th><img width="1000px"></th><th><img width="150px"></th><tr><th>Status Code</th><th>Description</th><th>Type</th></tr></thead><tbody><tr><td>200</td><td>Successful Response</td><td><a href="#user-content-header_type_inforesponse">InfoResponse</a></td></tr></tbody></table>


---
<a name="header_get-/error-info/{error_code}"></a>
#### GET /error-info/{error_code}
Returns information about a given error.

Useful for presenting standardized error information in interfaces.


<a name="header_input"></a>
#### Input
<table><thead><tr><th colspan="4"><img width="2000px"></th></tr><tr><th><img width="150px"></th><th><img width="1000px"></th><th><img width="150px"></th><th><img width="150px"></th><tr><th>Name</th><th>Description</th><th>Type</th><th>In</th></tr></thead><tbody><tr><td>error_code</td><td>The orcid id</td><td>integer</td><td>path</td></tr></tbody></table>


<a name="header_output"></a>
#### Output
<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="150px"></th><th><img width="1000px"></th><th><img width="150px"></th><tr><th>Status Code</th><th>Description</th><th>Type</th></tr></thead><tbody><tr><td>200</td><td>Successful Response</td><td><a href="#user-content-header_type_errorinforesponse">ErrorInfoResponse</a></td></tr><tr><td>422</td><td>Validation Error</td><td><a href="#user-content-header_type_httpvalidationerror">HTTPValidationError</a></td></tr></tbody></table>


---
<a name="header_get-/docs"></a>
#### GET /docs
Get API Documentation

Provides a web interface to the auto-generated API docs.


<a name="header_input"></a>
#### Input
*none*


<a name="header_output"></a>
#### Output
<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="150px"></th><th><img width="1000px"></th><th><img width="150px"></th><tr><th>Status Code</th><th>Description</th><th>Type</th></tr></thead><tbody><tr><td>200</td><td>Successfully returned the api docs</td><td>text/html</td></tr><tr><td>404</td><td>Not Found</td><td><i>none</i></td></tr></tbody></table>


---


<a name="header_link"></a>
### link
Access to and control over stored ORCID Links
<a name="header_get-/link"></a>
#### GET /link
Get ORCID Link

Return the link for the user associated with the KBase auth token passed in
the "Authorization" header


<a name="header_input"></a>
#### Input
<table><thead><tr><th colspan="4"><img width="2000px"></th></tr><tr><th><img width="150px"></th><th><img width="1000px"></th><th><img width="150px"></th><th><img width="150px"></th><tr><th>Name</th><th>Description</th><th>Type</th><th>In</th></tr></thead><tbody><tr><td>authorization</td><td>KBase auth token</td><td>n/a</td><td>header</td></tr></tbody></table>


<a name="header_output"></a>
#### Output
<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="150px"></th><th><img width="1000px"></th><th><img width="150px"></th><tr><th>Status Code</th><th>Description</th><th>Type</th></tr></thead><tbody><tr><td>200</td><td>Returns the <a href='#user-content-glossary_term_public-link-record'>Public link record</a> for this user; contains no secrets</td><td><a href="#user-content-header_type_linkrecordpublic">LinkRecordPublic</a></td></tr><tr><td>401</td><td>KBase auth token absent or invalid</td><td><a href="#user-content-header_type_errorresponse">ErrorResponse</a></td></tr><tr><td>404</td><td>Link not available for this user</td><td><a href="#user-content-header_type_errorresponse">ErrorResponse</a></td></tr><tr><td>422</td><td>Input or output data does not comply with the API schema</td><td><a href="#user-content-header_type_errorresponse">ErrorResponse</a></td></tr></tbody></table>


---
<a name="header_delete-/link"></a>
#### DELETE /link
Delete ORCID Link

Removes the link for the user associated with the KBase auth token passed in the "Authorization" header


<a name="header_input"></a>
#### Input
<table><thead><tr><th colspan="4"><img width="2000px"></th></tr><tr><th><img width="150px"></th><th><img width="1000px"></th><th><img width="150px"></th><th><img width="150px"></th><tr><th>Name</th><th>Description</th><th>Type</th><th>In</th></tr></thead><tbody><tr><td>authorization</td><td>KBase auth token</td><td>n/a</td><td>header</td></tr></tbody></table>


<a name="header_output"></a>
#### Output
<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="150px"></th><th><img width="1000px"></th><th><img width="150px"></th><tr><th>Status Code</th><th>Description</th><th>Type</th></tr></thead><tbody><tr><td>204</td><td>Successfully deleted the link</td><td><i>none</i></td></tr><tr><td>401</td><td>KBase auth token absent or invalid</td><td><a href="#user-content-header_type_errorresponse">ErrorResponse</a></td></tr><tr><td>404</td><td>Link not available for this user</td><td><a href="#user-content-header_type_errorresponse">ErrorResponse</a></td></tr><tr><td>422</td><td>Input or output data does not comply with the API schema</td><td><a href="#user-content-header_type_errorresponse">ErrorResponse</a></td></tr></tbody></table>


---
<a name="header_get-/link/for_orcid/{orcid_id}"></a>
#### GET /link/for_orcid/{orcid_id}
Get ORCID Link for a given ORCID Id

Return the link for the given orcid id, as long as the user associated with the KBase auth
token passed in the "Authorization" header is also the


<a name="header_input"></a>
#### Input
<table><thead><tr><th colspan="4"><img width="2000px"></th></tr><tr><th><img width="150px"></th><th><img width="1000px"></th><th><img width="150px"></th><th><img width="150px"></th><tr><th>Name</th><th>Description</th><th>Type</th><th>In</th></tr></thead><tbody><tr><td>orcid_id</td><td>The orcid id</td><td>string</td><td>path</td></tr><tr><td>authorization</td><td>KBase auth token</td><td>n/a</td><td>header</td></tr></tbody></table>


<a name="header_output"></a>
#### Output
<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="150px"></th><th><img width="1000px"></th><th><img width="150px"></th><tr><th>Status Code</th><th>Description</th><th>Type</th></tr></thead><tbody><tr><td>200</td><td>Returns the <a href='#user-content-glossary_term_public-link-record'>Public link record</a> for this user; contains no secrets</td><td><a href="#user-content-header_type_linkrecordpublic">LinkRecordPublic</a></td></tr><tr><td>401</td><td>KBase auth token absent or invalid</td><td><a href="#user-content-header_type_errorresponse">ErrorResponse</a></td></tr><tr><td>404</td><td>Link not available for this user</td><td><a href="#user-content-header_type_errorresponse">ErrorResponse</a></td></tr><tr><td>422</td><td>Input or output data does not comply with the API schema</td><td><a href="#user-content-header_type_errorresponse">ErrorResponse</a></td></tr></tbody></table>


---
<a name="header_get-/link/is_linked"></a>
#### GET /link/is_linked
Get whether Is Linked

Determine if the user associated with the KBase auth token in the "Authorization" header has a
link to an ORCID account.


<a name="header_input"></a>
#### Input
<table><thead><tr><th colspan="4"><img width="2000px"></th></tr><tr><th><img width="150px"></th><th><img width="1000px"></th><th><img width="150px"></th><th><img width="150px"></th><tr><th>Name</th><th>Description</th><th>Type</th><th>In</th></tr></thead><tbody><tr><td>authorization</td><td>KBase auth token</td><td>n/a</td><td>header</td></tr></tbody></table>


<a name="header_output"></a>
#### Output
<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="150px"></th><th><img width="1000px"></th><th><img width="150px"></th><tr><th>Status Code</th><th>Description</th><th>Type</th></tr></thead><tbody><tr><td>200</td><td>Returns a boolean indicating whether the user account is linked to ORCID</td><td>boolean</td></tr><tr><td>401</td><td>KBase auth token absent or invalid</td><td><a href="#user-content-header_type_errorresponse">ErrorResponse</a></td></tr><tr><td>422</td><td>Input or output data does not comply with the API schema</td><td><a href="#user-content-header_type_errorresponse">ErrorResponse</a></td></tr></tbody></table>


---
<a name="header_get-/link/is_orcid_linked/{orcid_id}"></a>
#### GET /link/is_orcid_linked/{orcid_id}
Get whether Is Linked

Determine if the user associated with the KBase auth token in the "Authorization" header has a
link to an ORCID account.


<a name="header_input"></a>
#### Input
<table><thead><tr><th colspan="4"><img width="2000px"></th></tr><tr><th><img width="150px"></th><th><img width="1000px"></th><th><img width="150px"></th><th><img width="150px"></th><tr><th>Name</th><th>Description</th><th>Type</th><th>In</th></tr></thead><tbody><tr><td>orcid_id</td><td>The orcid id</td><td>string</td><td>path</td></tr><tr><td>authorization</td><td>KBase auth token</td><td>n/a</td><td>header</td></tr></tbody></table>


<a name="header_output"></a>
#### Output
<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="150px"></th><th><img width="1000px"></th><th><img width="150px"></th><tr><th>Status Code</th><th>Description</th><th>Type</th></tr></thead><tbody><tr><td>200</td><td>Returns a boolean indicating whether the orcid id linked to a KBase account</td><td>boolean</td></tr><tr><td>401</td><td>KBase auth token absent or invalid</td><td><a href="#user-content-header_type_errorresponse">ErrorResponse</a></td></tr><tr><td>422</td><td>Input or output data does not comply with the API schema</td><td><a href="#user-content-header_type_errorresponse">ErrorResponse</a></td></tr></tbody></table>


---
<a name="header_get-/link/share/{username}"></a>
#### GET /link/share/{username}
Get whether Is Linked

Determine if the user associated with the KBase auth token in the "Authorization" header has a
link to an ORCID account.


<a name="header_input"></a>
#### Input
<table><thead><tr><th colspan="4"><img width="2000px"></th></tr><tr><th><img width="150px"></th><th><img width="1000px"></th><th><img width="150px"></th><th><img width="150px"></th><tr><th>Name</th><th>Description</th><th>Type</th><th>In</th></tr></thead><tbody><tr><td>username</td><td>The username</td><td>string</td><td>path</td></tr><tr><td>authorization</td><td>KBase auth token</td><td>n/a</td><td>header</td></tr></tbody></table>


<a name="header_output"></a>
#### Output
<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="150px"></th><th><img width="1000px"></th><th><img width="150px"></th><tr><th>Status Code</th><th>Description</th><th>Type</th></tr></thead><tbody><tr><td>200</td><td>Returns the shared portion of an ORCID Link record</td><td><a href="#user-content-header_type_linkingrecordshared">LinkingRecordShared</a></td></tr><tr><td>401</td><td>KBase auth token absent or invalid</td><td><a href="#user-content-header_type_errorresponse">ErrorResponse</a></td></tr><tr><td>422</td><td>Input or output data does not comply with the API schema</td><td><a href="#user-content-header_type_errorresponse">ErrorResponse</a></td></tr></tbody></table>


---


<a name="header_linking-sessions"></a>
### linking-sessions
OAuth integration and internal support for creating ORCID Links.

The common path element is `/linking-sessions`.

Some of the endpoints are "browser interactive", meaning that the links are followed 
directly by the browser, rather than being used within Javascript code.
<a name="header_post-/linking-sessions"></a>
#### POST /linking-sessions
Create Linking Session

Creates a new "linking session"; resulting in a linking session created in the database,
and the id for it returned for usage in an interactive linking session.


<a name="header_input"></a>
#### Input
<table><thead><tr><th colspan="4"><img width="2000px"></th></tr><tr><th><img width="150px"></th><th><img width="1000px"></th><th><img width="150px"></th><th><img width="150px"></th><tr><th>Name</th><th>Description</th><th>Type</th><th>In</th></tr></thead><tbody><tr><td>authorization</td><td>KBase auth token</td><td>n/a</td><td>header</td></tr></tbody></table>


<a name="header_output"></a>
#### Output
<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="150px"></th><th><img width="1000px"></th><th><img width="150px"></th><tr><th>Status Code</th><th>Description</th><th>Type</th></tr></thead><tbody><tr><td>201</td><td>The linking session has been successfully created</td><td><a href="#user-content-header_type_createlinkingsessionresult">CreateLinkingSessionResult</a></td></tr><tr><td>401</td><td>KBase auth token absent or invalid</td><td><a href="#user-content-header_type_errorresponse">ErrorResponse</a></td></tr><tr><td>422</td><td>Input or output data does not comply with the API schema</td><td><a href="#user-content-header_type_errorresponse">ErrorResponse</a></td></tr></tbody></table>


---
<a name="header_get-/linking-sessions/{session_id}"></a>
#### GET /linking-sessions/{session_id}
Get Linking Session

Returns the linking session record identified by the given linking session id,
as long as it is owned by the user associated with the given KBase auth token.

Note that the


<a name="header_input"></a>
#### Input
<table><thead><tr><th colspan="4"><img width="2000px"></th></tr><tr><th><img width="150px"></th><th><img width="1000px"></th><th><img width="150px"></th><th><img width="150px"></th><tr><th>Name</th><th>Description</th><th>Type</th><th>In</th></tr></thead><tbody><tr><td>session_id</td><td>The linking session id</td><td>string</td><td>path</td></tr><tr><td>authorization</td><td>KBase auth token</td><td>string</td><td>header</td></tr></tbody></table>


<a name="header_output"></a>
#### Output
<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="150px"></th><th><img width="1000px"></th><th><img width="150px"></th><tr><th>Status Code</th><th>Description</th><th>Type</th></tr></thead><tbody><tr><td>200</td><td>Returns the linking session</td><td><a href="#user-content-header_type_linkingsessioncompletepublic">LinkingSessionCompletePublic</a></td></tr><tr><td>401</td><td>KBase auth token absent or invalid</td><td><a href="#user-content-header_type_errorresponse">ErrorResponse</a></td></tr><tr><td>403</td><td>User does not own linking session</td><td><a href="#user-content-header_type_errorresponse">ErrorResponse</a></td></tr><tr><td>404</td><td>Linking session not found</td><td><a href="#user-content-header_type_errorresponse">ErrorResponse</a></td></tr><tr><td>422</td><td>Input or output data does not comply with the API schema</td><td><a href="#user-content-header_type_errorresponse">ErrorResponse</a></td></tr></tbody></table>


---
<a name="header_delete-/linking-sessions/{session_id}"></a>
#### DELETE /linking-sessions/{session_id}
Delete Linking Session

Deletes the linking session record associated with the session id provided
in the url, as long as it is owned by the user associated with the provided
KBase auth token.


<a name="header_input"></a>
#### Input
<table><thead><tr><th colspan="4"><img width="2000px"></th></tr><tr><th><img width="150px"></th><th><img width="1000px"></th><th><img width="150px"></th><th><img width="150px"></th><tr><th>Name</th><th>Description</th><th>Type</th><th>In</th></tr></thead><tbody><tr><td>session_id</td><td>The linking session id</td><td>string</td><td>path</td></tr><tr><td>authorization</td><td>KBase auth token</td><td>n/a</td><td>header</td></tr></tbody></table>


<a name="header_output"></a>
#### Output
<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="150px"></th><th><img width="1000px"></th><th><img width="150px"></th><tr><th>Status Code</th><th>Description</th><th>Type</th></tr></thead><tbody><tr><td>204</td><td>Successfully deleted the session</td><td><i>none</i></td></tr><tr><td>401</td><td>KBase auth token absent or invalid</td><td><a href="#user-content-header_type_errorresponse">ErrorResponse</a></td></tr><tr><td>403</td><td>Username does not match linking session</td><td><a href="#user-content-header_type_errorresponse">ErrorResponse</a></td></tr><tr><td>404</td><td>Linking session not found</td><td><a href="#user-content-header_type_errorresponse">ErrorResponse</a></td></tr><tr><td>422</td><td>Input or output data does not comply with the API schema</td><td><a href="#user-content-header_type_errorresponse">ErrorResponse</a></td></tr></tbody></table>


---
<a name="header_put-/linking-sessions/{session_id}/finish"></a>
#### PUT /linking-sessions/{session_id}/finish
Finish Linking Session

The final stage of the interactive linking session; called when the user confirms the creation
of the link, after OAuth flow has finished.


<a name="header_input"></a>
#### Input
<table><thead><tr><th colspan="4"><img width="2000px"></th></tr><tr><th><img width="150px"></th><th><img width="1000px"></th><th><img width="150px"></th><th><img width="150px"></th><tr><th>Name</th><th>Description</th><th>Type</th><th>In</th></tr></thead><tbody><tr><td>session_id</td><td>The linking session id</td><td>string</td><td>path</td></tr><tr><td>authorization</td><td>KBase auth token</td><td>n/a</td><td>header</td></tr></tbody></table>


<a name="header_output"></a>
#### Output
<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="150px"></th><th><img width="1000px"></th><th><img width="150px"></th><tr><th>Status Code</th><th>Description</th><th>Type</th></tr></thead><tbody><tr><td>200</td><td>The linking session has been finished successfully</td><td><a href="#user-content-header_type_simplesuccess">SimpleSuccess</a></td></tr><tr><td>401</td><td>KBase auth token absent or invalid</td><td><a href="#user-content-header_type_errorresponse">ErrorResponse</a></td></tr><tr><td>403</td><td>Username does not match linking session</td><td><a href="#user-content-header_type_errorresponse">ErrorResponse</a></td></tr><tr><td>404</td><td>Linking session not found</td><td><a href="#user-content-header_type_errorresponse">ErrorResponse</a></td></tr><tr><td>422</td><td>Input or output data does not comply with the API schema</td><td><a href="#user-content-header_type_errorresponse">ErrorResponse</a></td></tr></tbody></table>


---
<a name="header_get-/linking-sessions/{session_id}/oauth/start"></a>
#### GET /linking-sessions/{session_id}/oauth/start
Start Linking Session

This endpoint is designed to be used directly by the browser. It is the "start"
of the ORCID OAuth flow. If the provided session id is found and the associated
session record is still in the initial state, it will initiate the OAuth flow
by redirecting the browser to an endpoint at ORCID.

Starts a "linking session", an interactive OAuth flow the end result of which is an access_token stored at
KBase for future use by the user.


<a name="header_input"></a>
#### Input
<table><thead><tr><th colspan="4"><img width="2000px"></th></tr><tr><th><img width="150px"></th><th><img width="1000px"></th><th><img width="150px"></th><th><img width="150px"></th><tr><th>Name</th><th>Description</th><th>Type</th><th>In</th></tr></thead><tbody><tr><td>session_id</td><td>The linking session id</td><td>string</td><td>path</td></tr><tr><td>return_link</td><td>A url to redirect to after the entire linking is complete; not to be confused with the ORCID OAuth flow's redirect_url</td><td>n/a</td><td>query</td></tr><tr><td>skip_prompt</td><td>Whether to prompt for confirmation of linking</td><td>boolean</td><td>query</td></tr><tr><td>ui_options</td><td>Opaque string of ui options</td><td>string</td><td>query</td></tr><tr><td>kbase_session</td><td>KBase auth token taken from a cookie named 'kbase_session'</td><td>string</td><td>cookie</td></tr><tr><td>kbase_session_backup</td><td>KBase auth token taken from a cookie named 'kbase_session_backup. Required in the KBase production environment since the prod ui and services operate on different hosts; the primary cookie, kbase_session, is host-based so cannot be read by a prod service.</td><td>string</td><td>cookie</td></tr></tbody></table>


<a name="header_output"></a>
#### Output
<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="150px"></th><th><img width="1000px"></th><th><img width="150px"></th><tr><th>Status Code</th><th>Description</th><th>Type</th></tr></thead><tbody><tr><td>302</td><td>Redirect to ORCID if a valid linking session</td><td><i>none</i></td></tr><tr><td>401</td><td>KBase auth token absent or invalid</td><td><a href="#user-content-header_type_errorresponse">ErrorResponse</a></td></tr><tr><td>404</td><td>Response when a linking session not found for the supplied session id</td><td><a href="#user-content-header_type_errorresponse">ErrorResponse</a></td></tr><tr><td>422</td><td>Input or output data does not comply with the API schema</td><td><a href="#user-content-header_type_errorresponse">ErrorResponse</a></td></tr></tbody></table>


---
<a name="header_get-/linking-sessions/oauth/continue"></a>
#### GET /linking-sessions/oauth/continue
Continue Linking Session

This endpoint implements the handoff from from the ORCID authorization step in
the ORCID OAuth flow. That is, it
serves as the redirection target after the user has successfully completed
their interaction with ORCID, at which they may have logged in and provided
their consent to issuing the linking token to KBase.

Note that this is an interstitional endpoint, which does not have its own
user interface. Rather, it redirects to kbase-ui when finished. If an error is encountered,
it redirects to an error viewing endpoint in kbase-ui.


<a name="header_input"></a>
#### Input
<table><thead><tr><th colspan="4"><img width="2000px"></th></tr><tr><th><img width="150px"></th><th><img width="1000px"></th><th><img width="150px"></th><th><img width="150px"></th><tr><th>Name</th><th>Description</th><th>Type</th><th>In</th></tr></thead><tbody><tr><td>code</td><td>For a success case, contains an OAuth exchange code parameter</td><td>n/a</td><td>query</td></tr><tr><td>state</td><td>For a success case, contains an OAuth state parameter</td><td>n/a</td><td>query</td></tr><tr><td>error</td><td>For an error case, contains an error code parameter</td><td>n/a</td><td>query</td></tr><tr><td>kbase_session</td><td>KBase auth token taken from a cookie named 'kbase_session'</td><td>string</td><td>cookie</td></tr><tr><td>kbase_session_backup</td><td>KBase auth token taken from a cookie named 'kbase_session_backup. Required in the KBase production environment since the prod ui and services operate on different hosts; the primary cookie, kbase_session, is host-based so cannot be read by a prod service.</td><td>string</td><td>cookie</td></tr></tbody></table>


<a name="header_output"></a>
#### Output
<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="150px"></th><th><img width="1000px"></th><th><img width="150px"></th><tr><th>Status Code</th><th>Description</th><th>Type</th></tr></thead><tbody><tr><td>302</td><td>Redirect to the continuation page; or error page</td><td><i>none</i></td></tr><tr><td>401</td><td>Linking requires authorization; same meaning as standard auth 401, but caught and issued in a different manner</td><td><i>none</i></td></tr><tr><td>422</td><td>Input or output data does not comply with the API schema</td><td><a href="#user-content-header_type_errorresponse">ErrorResponse</a></td></tr></tbody></table>


---


<a name="header_orcid"></a>
### orcid
Direct access to ORCID via ORCID Link
<a name="header_get-/orcid/profile"></a>
#### GET /orcid/profile
Get the ORCID profile for the user associated with the current auth token.

Since ORCID Link is not a general purpose ORCID api, we may not fully
represent the profile as ORCID does, but modify it for purpose.
E.g. ORCID work records have a lot of optional fields which we
actually require. This is reflected in the typing. So we can't really
provide all work records in the profile, just those created by
KBase.

Returns a 404 Not Found if the user is not linked


<a name="header_input"></a>
#### Input
<table><thead><tr><th colspan="4"><img width="2000px"></th></tr><tr><th><img width="150px"></th><th><img width="1000px"></th><th><img width="150px"></th><th><img width="150px"></th><tr><th>Name</th><th>Description</th><th>Type</th><th>In</th></tr></thead><tbody><tr><td>authorization</td><td>KBase auth token</td><td>n/a</td><td>header</td></tr></tbody></table>


<a name="header_output"></a>
#### Output
<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="150px"></th><th><img width="1000px"></th><th><img width="150px"></th><tr><th>Status Code</th><th>Description</th><th>Type</th></tr></thead><tbody><tr><td>200</td><td>Successful Response</td><td><a href="#user-content-header_type_orcidprofile">ORCIDProfile</a></td></tr><tr><td>401</td><td>KBase auth token absent or invalid</td><td><a href="#user-content-header_type_errorresponse">ErrorResponse</a></td></tr><tr><td>404</td><td>User not linked or ORCID profile not available.</td><td><i>none</i></td></tr><tr><td>422</td><td>Input or output data does not comply with the API schema</td><td><a href="#user-content-header_type_errorresponse">ErrorResponse</a></td></tr></tbody></table>


---


<a name="header_works"></a>
### works
Add, remove, update 'works' records for a user's ORCID Account
<a name="header_get-/orcid/works/{put_code}"></a>
#### GET /orcid/works/{put_code}
Fetch the work record, identified by `put_code`, for the user associated with the KBase auth token provided in the `Authorization` header


<a name="header_input"></a>
#### Input
<table><thead><tr><th colspan="4"><img width="2000px"></th></tr><tr><th><img width="150px"></th><th><img width="1000px"></th><th><img width="150px"></th><th><img width="150px"></th><tr><th>Name</th><th>Description</th><th>Type</th><th>In</th></tr></thead><tbody><tr><td>put_code</td><td>The ORCID `put code` for the work record to fetch</td><td>integer</td><td>path</td></tr><tr><td>authorization</td><td>KBase auth token</td><td>n/a</td><td>header</td></tr></tbody></table>


<a name="header_output"></a>
#### Output
<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="150px"></th><th><img width="1000px"></th><th><img width="150px"></th><tr><th>Status Code</th><th>Description</th><th>Type</th></tr></thead><tbody><tr><td>200</td><td>Successful Response</td><td><a href="#user-content-header_type_workoutput">WorkOutput</a></td></tr><tr><td>401</td><td>KBase auth token absent or invalid</td><td><a href="#user-content-header_type_errorresponse">ErrorResponse</a></td></tr><tr><td>404</td><td>Link not available for this user</td><td><i>none</i></td></tr><tr><td>422</td><td>Input or output data does not comply with the API schema</td><td><a href="#user-content-header_type_errorresponse">ErrorResponse</a></td></tr></tbody></table>


---
<a name="header_delete-/orcid/works/{put_code}"></a>
#### DELETE /orcid/works/{put_code}
n/a


<a name="header_input"></a>
#### Input
<table><thead><tr><th colspan="4"><img width="2000px"></th></tr><tr><th><img width="150px"></th><th><img width="1000px"></th><th><img width="150px"></th><th><img width="150px"></th><tr><th>Name</th><th>Description</th><th>Type</th><th>In</th></tr></thead><tbody><tr><td>put_code</td><td>n/a</td><td>integer</td><td>path</td></tr><tr><td>authorization</td><td>KBase auth token</td><td>n/a</td><td>header</td></tr></tbody></table>


<a name="header_output"></a>
#### Output
<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="150px"></th><th><img width="1000px"></th><th><img width="150px"></th><tr><th>Status Code</th><th>Description</th><th>Type</th></tr></thead><tbody><tr><td>204</td><td>Work record successfully deleted</td><td><i>none</i></td></tr><tr><td>401</td><td>KBase auth token absent or invalid</td><td><a href="#user-content-header_type_errorresponse">ErrorResponse</a></td></tr><tr><td>404</td><td>Not found</td><td><i>none</i></td></tr><tr><td>422</td><td>Input or output data does not comply with the API schema</td><td><a href="#user-content-header_type_errorresponse">ErrorResponse</a></td></tr></tbody></table>


---
<a name="header_get-/orcid/works"></a>
#### GET /orcid/works
Fetch all of the "work" records from a user's ORCID account if their KBase account is linked.


<a name="header_input"></a>
#### Input
<table><thead><tr><th colspan="4"><img width="2000px"></th></tr><tr><th><img width="150px"></th><th><img width="1000px"></th><th><img width="150px"></th><th><img width="150px"></th><tr><th>Name</th><th>Description</th><th>Type</th><th>In</th></tr></thead><tbody><tr><td>authorization</td><td>KBase auth token</td><td>n/a</td><td>header</td></tr></tbody></table>


<a name="header_output"></a>
#### Output
<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="150px"></th><th><img width="1000px"></th><th><img width="150px"></th><tr><th>Status Code</th><th>Description</th><th>Type</th></tr></thead><tbody><tr><td>200</td><td>Successful Response</td><td>array</td></tr><tr><td>401</td><td>KBase auth token absent or invalid</td><td><a href="#user-content-header_type_errorresponse">ErrorResponse</a></td></tr><tr><td>404</td><td>Link not available for this user</td><td><i>none</i></td></tr><tr><td>422</td><td>Input or output data does not comply with the API schema</td><td><a href="#user-content-header_type_errorresponse">ErrorResponse</a></td></tr></tbody></table>


---
<a name="header_put-/orcid/works"></a>
#### PUT /orcid/works
Update a work record; the `work_update` contains the `put code`.


<a name="header_input"></a>
#### Input
<table><thead><tr><th colspan="4"><img width="2000px"></th></tr><tr><th><img width="150px"></th><th><img width="1000px"></th><th><img width="150px"></th><th><img width="150px"></th><tr><th>Name</th><th>Description</th><th>Type</th><th>In</th></tr></thead><tbody><tr><td>authorization</td><td>KBase auth token</td><td>n/a</td><td>header</td></tr></tbody></table>


<a name="header_output"></a>
#### Output
<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="150px"></th><th><img width="1000px"></th><th><img width="150px"></th><tr><th>Status Code</th><th>Description</th><th>Type</th></tr></thead><tbody><tr><td>200</td><td>Successful Response</td><td><a href="#user-content-header_type_workinput">WorkInput</a></td></tr><tr><td>401</td><td>KBase auth token absent or invalid</td><td><a href="#user-content-header_type_errorresponse">ErrorResponse</a></td></tr><tr><td>404</td><td>Link not available for this user</td><td><i>none</i></td></tr><tr><td>422</td><td>Input or output data does not comply with the API schema</td><td><a href="#user-content-header_type_errorresponse">ErrorResponse</a></td></tr></tbody></table>


---
<a name="header_post-/orcid/works"></a>
#### POST /orcid/works
n/a


<a name="header_input"></a>
#### Input
<table><thead><tr><th colspan="4"><img width="2000px"></th></tr><tr><th><img width="150px"></th><th><img width="1000px"></th><th><img width="150px"></th><th><img width="150px"></th><tr><th>Name</th><th>Description</th><th>Type</th><th>In</th></tr></thead><tbody><tr><td>authorization</td><td>KBase auth token</td><td>n/a</td><td>header</td></tr></tbody></table>


<a name="header_output"></a>
#### Output
<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="150px"></th><th><img width="1000px"></th><th><img width="150px"></th><tr><th>Status Code</th><th>Description</th><th>Type</th></tr></thead><tbody><tr><td>200</td><td>Work record successfully created</td><td><a href="#user-content-header_type_workinput">WorkInput</a></td></tr><tr><td>401</td><td>KBase auth token absent or invalid</td><td><a href="#user-content-header_type_errorresponse">ErrorResponse</a></td></tr><tr><td>404</td><td>Not found</td><td><i>none</i></td></tr><tr><td>422</td><td>Input or output data does not comply with the API schema</td><td><a href="#user-content-header_type_errorresponse">ErrorResponse</a></td></tr></tbody></table>


---


<a name="header_types"></a>
## Types
This section presents all types defined via FastAPI (Pydantic). They are ordered
alphabetically, which is fine for looking them up, but not for their relationships.

> TODO: a better presentation of related types

<a name="header_type_citationtype"></a>
##### CitationType

<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="1000px"></th><th><img width="200px"></th><th><img width="75px"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody></tbody></table>



<a name="header_type_contributorrole"></a>
##### ContributorRole

<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="1000px"></th><th><img width="200px"></th><th><img width="75px"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>role</td><td><div><i>All Of</i></div><div><a href="#user-content-header_type_contributorrolevalue">ContributorRoleValue</a></div></td><td>✓</td></tr></tbody></table>



<a name="header_type_contributorrolevalue"></a>
##### ContributorRoleValue

<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="1000px"></th><th><img width="200px"></th><th><img width="75px"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody></tbody></table>



<a name="header_type_createlinkingsessionresult"></a>
##### CreateLinkingSessionResult

<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="1000px"></th><th><img width="200px"></th><th><img width="75px"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>session_id</td><td>string</td><td>✓</td></tr></tbody></table>



<a name="header_type_errorcode2"></a>
##### ErrorCode2

<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="1000px"></th><th><img width="200px"></th><th><img width="75px"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>code</td><td>integer</td><td>✓</td></tr><tr><td>title</td><td>string</td><td>✓</td></tr><tr><td>description</td><td>string</td><td>✓</td></tr><tr><td>status_code</td><td>integer</td><td>✓</td></tr></tbody></table>



<a name="header_type_errorinforesponse"></a>
##### ErrorInfoResponse

<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="1000px"></th><th><img width="200px"></th><th><img width="75px"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>error_info</td><td><a href="#user-content-header_type_errorcode2">ErrorCode2</a></td><td>✓</td></tr></tbody></table>



<a name="header_type_errorresponse"></a>
##### ErrorResponse

    A generic error object used for all error responses.

    See [the error docs](docs/errors.md) for more information.
    
<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="1000px"></th><th><img width="200px"></th><th><img width="75px"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>code</td><td>integer</td><td>✓</td></tr><tr><td>title</td><td>string</td><td>✓</td></tr><tr><td>message</td><td>string</td><td>✓</td></tr><tr><td>data</td><td><div><i>Any Of</i></div><div><a href="#user-content-header_type_servicebasemodel">ServiceBaseModel</a></div><div>null</div></td><td></td></tr></tbody></table>



<a name="header_type_externalid"></a>
##### ExternalId

    See: https://github.com/ORCID/orcid-model/blob/e7a9c0c0060f843b2534e6100b30cab713c8aef5/src/main/resources/common_3.0/common-3.0.xsd#L1025
    
<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="1000px"></th><th><img width="200px"></th><th><img width="75px"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>type</td><td><div><i>All Of</i></div><div><a href="#user-content-header_type_externalidtype">ExternalIdType</a></div></td><td>✓</td></tr><tr><td>value</td><td>string</td><td>✓</td></tr><tr><td>url</td><td>string</td><td>✓</td></tr><tr><td>relationship</td><td><div><i>All Of</i></div><div><a href="#user-content-header_type_relationshiptype">RelationshipType</a></div></td><td>✓</td></tr></tbody></table>



<a name="header_type_externalidtype"></a>
##### ExternalIdType

<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="1000px"></th><th><img width="200px"></th><th><img width="75px"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody></tbody></table>



<a name="header_type_gitinfo"></a>
##### GitInfo

<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="1000px"></th><th><img width="200px"></th><th><img width="75px"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>commit_hash</td><td>string</td><td>✓</td></tr><tr><td>commit_hash_abbreviated</td><td>string</td><td>✓</td></tr><tr><td>author_name</td><td>string</td><td>✓</td></tr><tr><td>author_date</td><td>integer</td><td>✓</td></tr><tr><td>committer_name</td><td>string</td><td>✓</td></tr><tr><td>committer_date</td><td>integer</td><td>✓</td></tr><tr><td>url</td><td>string</td><td>✓</td></tr><tr><td>branch</td><td>string</td><td>✓</td></tr><tr><td>tag</td><td><div><i>Any Of</i></div><div>string</div><div>null</div></td><td>✓</td></tr></tbody></table>



<a name="header_type_httpvalidationerror"></a>
##### HTTPValidationError

<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="1000px"></th><th><img width="200px"></th><th><img width="75px"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>detail</td><td>array</td><td></td></tr></tbody></table>



<a name="header_type_inforesponse"></a>
##### InfoResponse

<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="1000px"></th><th><img width="200px"></th><th><img width="75px"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>service-description</td><td><a href="#user-content-header_type_servicedescription">ServiceDescription</a></td><td>✓</td></tr><tr><td>git-info</td><td><a href="#user-content-header_type_gitinfo">GitInfo</a></td><td>✓</td></tr></tbody></table>



<a name="header_type_linkrecordpublic"></a>
##### LinkRecordPublic

<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="1000px"></th><th><img width="200px"></th><th><img width="75px"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>username</td><td>string</td><td>✓</td></tr><tr><td>created_at</td><td>integer</td><td>✓</td></tr><tr><td>expires_at</td><td>integer</td><td>✓</td></tr><tr><td>orcid_auth</td><td><a href="#user-content-header_type_orcidauthpublic">ORCIDAuthPublic</a></td><td>✓</td></tr></tbody></table>



<a name="header_type_linkrecordpublicnonowner"></a>
##### LinkRecordPublicNonOwner

<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="1000px"></th><th><img width="200px"></th><th><img width="75px"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>username</td><td>string</td><td>✓</td></tr><tr><td>orcid_auth</td><td><a href="#user-content-header_type_orcidauthpublicnonowner">ORCIDAuthPublicNonOwner</a></td><td>✓</td></tr></tbody></table>



<a name="header_type_linkingrecordshared"></a>
##### LinkingRecordShared

<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="1000px"></th><th><img width="200px"></th><th><img width="75px"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>orcidId</td><td>string</td><td>✓</td></tr></tbody></table>



<a name="header_type_linkingsessioncompletepublic"></a>
##### LinkingSessionCompletePublic

<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="1000px"></th><th><img width="200px"></th><th><img width="75px"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>session_id</td><td>string</td><td>✓</td></tr><tr><td>username</td><td>string</td><td>✓</td></tr><tr><td>created_at</td><td>integer</td><td>✓</td></tr><tr><td>expires_at</td><td>integer</td><td>✓</td></tr><tr><td>return_link</td><td><div><i>Any Of</i></div><div>string</div><div>null</div></td><td>✓</td></tr><tr><td>skip_prompt</td><td>boolean</td><td>✓</td></tr><tr><td>ui_options</td><td>string</td><td>✓</td></tr><tr><td>orcid_auth</td><td><a href="#user-content-header_type_orcidauthpublic">ORCIDAuthPublic</a></td><td>✓</td></tr></tbody></table>



<a name="header_type_newwork"></a>
##### NewWork

    Represents a work record that is going to be added to ORCID.
    
<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="1000px"></th><th><img width="200px"></th><th><img width="75px"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>title</td><td>string</td><td>✓</td></tr><tr><td>date</td><td>string</td><td>✓</td></tr><tr><td>workType</td><td><div><i>All Of</i></div><div><a href="#user-content-header_type_worktype">WorkType</a></div></td><td>✓</td></tr><tr><td>url</td><td>string</td><td>✓</td></tr><tr><td>doi</td><td>string</td><td>✓</td></tr><tr><td>externalIds</td><td>array</td><td>✓</td></tr><tr><td>journal</td><td>string</td><td>✓</td></tr><tr><td>shortDescription</td><td>string</td><td>✓</td></tr><tr><td>citation</td><td><div><i>All Of</i></div><div><a href="#user-content-header_type_orcidcitation">ORCIDCitation</a></div></td><td>✓</td></tr><tr><td>selfContributor</td><td><div><i>All Of</i></div><div><a href="#user-content-header_type_orcidcontributorselfinput">ORCIDContributorSelfInput</a></div></td><td>✓</td></tr><tr><td>otherContributors</td><td>array</td><td>✓</td></tr></tbody></table>



<a name="header_type_orcidaffiliation"></a>
##### ORCIDAffiliation

<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="1000px"></th><th><img width="200px"></th><th><img width="75px"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>name</td><td>string</td><td>✓</td></tr><tr><td>role</td><td>string</td><td>✓</td></tr><tr><td>startYear</td><td>string</td><td>✓</td></tr><tr><td>endYear</td><td><div><i>Any Of</i></div><div>string</div><div>null</div></td><td>✓</td></tr></tbody></table>



<a name="header_type_orcidauthpublic"></a>
##### ORCIDAuthPublic

<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="1000px"></th><th><img width="200px"></th><th><img width="75px"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>name</td><td>string</td><td>✓</td></tr><tr><td>scope</td><td>string</td><td>✓</td></tr><tr><td>expires_in</td><td>integer</td><td>✓</td></tr><tr><td>orcid</td><td>string</td><td>✓</td></tr></tbody></table>



<a name="header_type_orcidauthpublicnonowner"></a>
##### ORCIDAuthPublicNonOwner

<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="1000px"></th><th><img width="200px"></th><th><img width="75px"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>name</td><td>string</td><td>✓</td></tr><tr><td>orcid</td><td>string</td><td>✓</td></tr></tbody></table>



<a name="header_type_orcidcitation"></a>
##### ORCIDCitation

<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="1000px"></th><th><img width="200px"></th><th><img width="75px"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>type</td><td><div><i>All Of</i></div><div><a href="#user-content-header_type_citationtype">CitationType</a></div></td><td>✓</td></tr><tr><td>value</td><td>string</td><td>✓</td></tr></tbody></table>



<a name="header_type_orcidcontributorinput"></a>
##### ORCIDContributorInput

    Note that the orcidId is not required for the "regular" contributor.
    The "self contributor" described below, does, require it.
    
<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="1000px"></th><th><img width="200px"></th><th><img width="75px"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>orcidId</td><td><div><i>Any Of</i></div><div>string</div><div>null</div></td><td></td></tr><tr><td>name</td><td>string</td><td>✓</td></tr><tr><td>roles</td><td>array</td><td>✓</td></tr></tbody></table>



<a name="header_type_orcidcontributoroutput"></a>
##### ORCIDContributorOutput

    Note that the orcidId is not required for the "regular" contributor.
    The "self contributor" described below, does, require it.
    
<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="1000px"></th><th><img width="200px"></th><th><img width="75px"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>orcidId</td><td><div><i>Any Of</i></div><div>string</div><div>null</div></td><td>✓</td></tr><tr><td>name</td><td>string</td><td>✓</td></tr><tr><td>roles</td><td>array</td><td>✓</td></tr></tbody></table>



<a name="header_type_orcidcontributorselfinput"></a>
##### ORCIDContributorSelfInput

<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="1000px"></th><th><img width="200px"></th><th><img width="75px"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>orcidId</td><td>string</td><td>✓</td></tr><tr><td>name</td><td>string</td><td>✓</td></tr><tr><td>roles</td><td>array</td><td>✓</td></tr></tbody></table>



<a name="header_type_orcidcontributorselfoutput"></a>
##### ORCIDContributorSelfOutput

<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="1000px"></th><th><img width="200px"></th><th><img width="75px"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>orcidId</td><td>string</td><td>✓</td></tr><tr><td>name</td><td>string</td><td>✓</td></tr><tr><td>roles</td><td>array</td><td>✓</td></tr></tbody></table>



<a name="header_type_orcidprofile"></a>
##### ORCIDProfile

<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="1000px"></th><th><img width="200px"></th><th><img width="75px"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>orcidId</td><td>string</td><td>✓</td></tr><tr><td>firstName</td><td>string</td><td>✓</td></tr><tr><td>lastName</td><td>string</td><td>✓</td></tr><tr><td>creditName</td><td><div><i>Any Of</i></div><div>string</div><div>null</div></td><td>✓</td></tr><tr><td>bio</td><td><div><i>Any Of</i></div><div>string</div><div>null</div></td><td>✓</td></tr><tr><td>distinctions</td><td>array</td><td>✓</td></tr><tr><td>education</td><td>array</td><td>✓</td></tr><tr><td>employment</td><td>array</td><td>✓</td></tr><tr><td>emailAddresses</td><td>array</td><td>✓</td></tr></tbody></table>



<a name="header_type_orcidworkgroupinput"></a>
##### ORCIDWorkGroupInput

<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="1000px"></th><th><img width="200px"></th><th><img width="75px"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>updatedAt</td><td>integer</td><td>✓</td></tr><tr><td>externalIds</td><td>array</td><td>✓</td></tr><tr><td>works</td><td>array</td><td>✓</td></tr></tbody></table>



<a name="header_type_orcidworkgroupoutput"></a>
##### ORCIDWorkGroupOutput

<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="1000px"></th><th><img width="200px"></th><th><img width="75px"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>updatedAt</td><td>integer</td><td>✓</td></tr><tr><td>externalIds</td><td>array</td><td>✓</td></tr><tr><td>works</td><td>array</td><td>✓</td></tr></tbody></table>



<a name="header_type_relationshiptype"></a>
##### RelationshipType

<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="1000px"></th><th><img width="200px"></th><th><img width="75px"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody></tbody></table>



<a name="header_type_servicebasemodel"></a>
##### ServiceBaseModel

<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="1000px"></th><th><img width="200px"></th><th><img width="75px"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody></tbody></table>



<a name="header_type_servicedescription"></a>
##### ServiceDescription

<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="1000px"></th><th><img width="200px"></th><th><img width="75px"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>name</td><td>string</td><td>✓</td></tr><tr><td>title</td><td>string</td><td>✓</td></tr><tr><td>version</td><td>string</td><td>✓</td></tr><tr><td>language</td><td>string</td><td>✓</td></tr><tr><td>description</td><td>string</td><td>✓</td></tr><tr><td>repoURL</td><td>string</td><td>✓</td></tr></tbody></table>



<a name="header_type_simplesuccess"></a>
##### SimpleSuccess

<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="1000px"></th><th><img width="200px"></th><th><img width="75px"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>ok</td><td>boolean</td><td>✓</td></tr></tbody></table>



<a name="header_type_statusresponse"></a>
##### StatusResponse

<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="1000px"></th><th><img width="200px"></th><th><img width="75px"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>status</td><td>string</td><td>✓</td></tr><tr><td>current_time</td><td>integer</td><td>✓</td></tr><tr><td>start_time</td><td>integer</td><td>✓</td></tr></tbody></table>



<a name="header_type_validationerror"></a>
##### ValidationError

<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="1000px"></th><th><img width="200px"></th><th><img width="75px"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>loc</td><td>array</td><td>✓</td></tr><tr><td>msg</td><td>string</td><td>✓</td></tr><tr><td>type</td><td>string</td><td>✓</td></tr></tbody></table>



<a name="header_type_workinput"></a>
##### WorkInput

<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="1000px"></th><th><img width="200px"></th><th><img width="75px"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>putCode</td><td>integer</td><td>✓</td></tr><tr><td>createdAt</td><td>integer</td><td>✓</td></tr><tr><td>updatedAt</td><td><div><i>Any Of</i></div><div>integer</div><div>null</div></td><td></td></tr><tr><td>source</td><td>string</td><td>✓</td></tr><tr><td>title</td><td>string</td><td>✓</td></tr><tr><td>date</td><td>string</td><td>✓</td></tr><tr><td>workType</td><td><div><i>All Of</i></div><div><a href="#user-content-header_type_worktype">WorkType</a></div></td><td>✓</td></tr><tr><td>url</td><td>string</td><td>✓</td></tr><tr><td>doi</td><td>string</td><td>✓</td></tr><tr><td>externalIds</td><td>array</td><td>✓</td></tr><tr><td>journal</td><td>string</td><td>✓</td></tr><tr><td>shortDescription</td><td>string</td><td>✓</td></tr><tr><td>citation</td><td><div><i>All Of</i></div><div><a href="#user-content-header_type_orcidcitation">ORCIDCitation</a></div></td><td>✓</td></tr><tr><td>selfContributor</td><td><div><i>All Of</i></div><div><a href="#user-content-header_type_orcidcontributorselfinput">ORCIDContributorSelfInput</a></div></td><td>✓</td></tr><tr><td>otherContributors</td><td>array</td><td>✓</td></tr></tbody></table>



<a name="header_type_workoutput"></a>
##### WorkOutput

<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="1000px"></th><th><img width="200px"></th><th><img width="75px"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>putCode</td><td>integer</td><td>✓</td></tr><tr><td>createdAt</td><td>integer</td><td>✓</td></tr><tr><td>updatedAt</td><td><div><i>Any Of</i></div><div>integer</div><div>null</div></td><td>✓</td></tr><tr><td>source</td><td>string</td><td>✓</td></tr><tr><td>title</td><td>string</td><td>✓</td></tr><tr><td>date</td><td>string</td><td>✓</td></tr><tr><td>workType</td><td><div><i>All Of</i></div><div><a href="#user-content-header_type_worktype">WorkType</a></div></td><td>✓</td></tr><tr><td>url</td><td>string</td><td>✓</td></tr><tr><td>doi</td><td>string</td><td>✓</td></tr><tr><td>externalIds</td><td>array</td><td>✓</td></tr><tr><td>journal</td><td>string</td><td>✓</td></tr><tr><td>shortDescription</td><td>string</td><td>✓</td></tr><tr><td>citation</td><td><div><i>All Of</i></div><div><a href="#user-content-header_type_orcidcitation">ORCIDCitation</a></div></td><td>✓</td></tr><tr><td>selfContributor</td><td><div><i>All Of</i></div><div><a href="#user-content-header_type_orcidcontributorselfoutput">ORCIDContributorSelfOutput</a></div></td><td>✓</td></tr><tr><td>otherContributors</td><td>array</td><td>✓</td></tr></tbody></table>



<a name="header_type_worksummaryinput"></a>
##### WorkSummaryInput

<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="1000px"></th><th><img width="200px"></th><th><img width="75px"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>putCode</td><td>integer</td><td>✓</td></tr><tr><td>createdAt</td><td>integer</td><td>✓</td></tr><tr><td>updatedAt</td><td><div><i>Any Of</i></div><div>integer</div><div>null</div></td><td></td></tr><tr><td>source</td><td>string</td><td>✓</td></tr><tr><td>title</td><td>string</td><td>✓</td></tr><tr><td>date</td><td>string</td><td>✓</td></tr><tr><td>workType</td><td><div><i>All Of</i></div><div><a href="#user-content-header_type_worktype">WorkType</a></div></td><td>✓</td></tr><tr><td>url</td><td>string</td><td>✓</td></tr><tr><td>doi</td><td>string</td><td>✓</td></tr><tr><td>externalIds</td><td>array</td><td>✓</td></tr><tr><td>journal</td><td><div><i>Any Of</i></div><div>string</div><div>null</div></td><td></td></tr></tbody></table>



<a name="header_type_worksummaryoutput"></a>
##### WorkSummaryOutput

<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="1000px"></th><th><img width="200px"></th><th><img width="75px"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>putCode</td><td>integer</td><td>✓</td></tr><tr><td>createdAt</td><td>integer</td><td>✓</td></tr><tr><td>updatedAt</td><td><div><i>Any Of</i></div><div>integer</div><div>null</div></td><td>✓</td></tr><tr><td>source</td><td>string</td><td>✓</td></tr><tr><td>title</td><td>string</td><td>✓</td></tr><tr><td>date</td><td>string</td><td>✓</td></tr><tr><td>workType</td><td><div><i>All Of</i></div><div><a href="#user-content-header_type_worktype">WorkType</a></div></td><td>✓</td></tr><tr><td>url</td><td>string</td><td>✓</td></tr><tr><td>doi</td><td>string</td><td>✓</td></tr><tr><td>externalIds</td><td>array</td><td>✓</td></tr><tr><td>journal</td><td><div><i>Any Of</i></div><div>string</div><div>null</div></td><td>✓</td></tr></tbody></table>



<a name="header_type_worktype"></a>
##### WorkType

<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="1000px"></th><th><img width="200px"></th><th><img width="75px"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody></tbody></table>



<a name="header_type_workupdate"></a>
##### WorkUpdate

    Represents a work record which has been fetched from ORCID, modified,
    and can be sent back to update the ORCID work record
    
<table><thead><tr><th colspan="3"><img width="2000px"></th></tr><tr><th><img width="1000px"></th><th><img width="200px"></th><th><img width="75px"></th><tr><th>Name</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td>putCode</td><td>integer</td><td>✓</td></tr><tr><td>title</td><td>string</td><td>✓</td></tr><tr><td>date</td><td>string</td><td>✓</td></tr><tr><td>workType</td><td><div><i>All Of</i></div><div><a href="#user-content-header_type_worktype">WorkType</a></div></td><td>✓</td></tr><tr><td>url</td><td>string</td><td>✓</td></tr><tr><td>doi</td><td>string</td><td>✓</td></tr><tr><td>externalIds</td><td>array</td><td>✓</td></tr><tr><td>journal</td><td>string</td><td>✓</td></tr><tr><td>shortDescription</td><td>string</td><td>✓</td></tr><tr><td>citation</td><td><div><i>All Of</i></div><div><a href="#user-content-header_type_orcidcitation">ORCIDCitation</a></div></td><td>✓</td></tr><tr><td>selfContributor</td><td><div><i>All Of</i></div><div><a href="#user-content-header_type_orcidcontributorselfinput">ORCIDContributorSelfInput</a></div></td><td>✓</td></tr><tr><td>otherContributors</td><td>array</td><td>✓</td></tr></tbody></table>



<a name="header_glossary"></a>
## Glossary
<dl>
<dt><a name="glossary_term_orcid"></a><a href='https://orcid.org'>ORCID</a></dt><dd>Open Researcher and Contributor ID
<dt><a name="glossary_term_public-link-record"></a>Public link record</dt><dd>The record used internally to associate a KBase User Account with an ORCID Account, with sensitive information such as tokens removed. Represented by the type <a href="#user-content-header_type_linkrecordpublic">LinkRecordPublic</a></dd>
</dl>
-fin-