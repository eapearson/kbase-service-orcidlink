##
# Constants
#
# Hard-coded, shared settings which are not dynamic enough to be configurable via the deployment config.
#

# Scopes to be requested, and subsequently granted, for the ORCID access token.
ORCID_SCOPES = "/read-limited /activities/update openid"

# How long a linking session is valid for after creation; in seconds.
LINKING_SESSION_TTL = 10 * 60
