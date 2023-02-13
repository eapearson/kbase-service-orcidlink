import json
import logging
import uuid
from typing import Any

from orcidlink.lib.utils import epoch_time_millis


def log_event(event: str, data: Any, level: str) -> str:
    # We use a separate logger, configured to save the
    # entire message as a simple string ... and that string
    # is a JSON-encoded message object.
    # The resulting log file, then, is y it is a JSON stream format, since it
    # contains multiple objects in sequence.
    orcidlink_log = logging.getLogger("orcidlink")
    log_id = str(uuid.uuid4())
    if len(orcidlink_log.handlers) == 0:
        # Here we may change the logging handler to something like HTTP, syslog, io stream,
        # see https://docs.python.org/3/library/logging.handlers.html
        handler = logging.FileHandler("/tmp/orcidlink.log")
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)
        orcidlink_log.addHandler(handler)

    message = json.dumps(
        {
            # If logs are combined, we need to tie log entries to
            # a specific version of a service in a specific environment.
            "service": "orcidlink",
            "version": "n/a",
            "environment": "n/a",
            # General log entry; information that any log entry
            # will need.
            # id helps create a unique reference to a log entry; perhaps
            # should be uuid, service + uuid, or omitted and only created
            # by a logging repository service.
            "id": log_id,
            "timestamp": epoch_time_millis(),
            # The actual, specific event. The event name is a simple
            # string, the data is a dict or serializable class whose
            # definition is implied by the event name.
            "event": {
                "name": event,
                # the event context captures information common to instances
                # of this kind of event. As a narrative ui event, part of the context
                # is the narrative object, the current user, and the current user's
                # browser. Clearly more could be captured here, e.g. the browser model,
                # narrative session id, etc.
                "context": {
                    # I tried to update kbase_env to reflect the current narrative ref,
                    # but to no avail so far. The kbase_env here is not the same as the
                    # one used when saving a narrative and getting the new version, so it does
                    # not reflect an updated narrative object version.
                    # If that isn't possible, we can store the ws and object id instead.
                    # "narrative_ref": kbase_env.narrative_ref,
                    # Log entries for authenticated contexts should identify the user
                    "username": "n/a",
                    # Log entries resulting from a network call can/should identify
                    # the ip address of the caller
                    "client_ip": "n/a"
                    # could be more context, like the jupyter / ipython / etc. versions
                },
                # This is the specific data sent in this logging event
                "data": data,
            },
        }
    )

    if level == "debug":
        orcidlink_log.debug(message)
    elif level == "info":
        orcidlink_log.info(message)
    elif level == "warning":
        orcidlink_log.warning(message)
    elif level == "error":
        orcidlink_log.error(message)
    elif level == "critical":
        orcidlink_log.critical(message)
    else:
        raise ValueError(
            f"log level must be one of debug, info, warning, error, or critical; it is '{level}'"
        )
    return log_id
