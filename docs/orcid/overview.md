# ORCID Integration Overview

One of the primary tasks of this service is to provide a controlled interface to ORCID
services. The conduit for this interface is composed of 3 primary elements:

- The ORCID implementation of OAuth 3-legged flow, used to obtain authorization for
  KBase to access ORCID on behalf of the user. This is composed of:
    - browser-interactive endpoints in which the browser follows a link to ORCID,
      within ORCID, then back to KBase
    - OAuth API endopint which provides for server-server interaction during the OAuth
      flow
- The ORCID API which is used to access the user's ORCID record once authorization has
  been provided and the KBase ORCID Link created with the above.

These  ORCID interfaces are implemented

