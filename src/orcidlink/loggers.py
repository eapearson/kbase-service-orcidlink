import datetime
import logging

# See this very useful article: https://guicommits.com/how-to-log-in-python-like-a-pro/


def format_time_in_rfc3339(
    _self: logging.Formatter, record: logging.LogRecord, _: str | None = None
) -> str:
    return datetime.datetime.fromtimestamp(
        record.created, datetime.timezone.utc
    ).isoformat()


# logging.Formatter.formatTime = format_time_in_rfc3339


# class ORCIDRequestLogEntry(ServiceBaseModel):
#     request_id: str = Field(...)
#     request_at: int = Field(...)
#     api: str = Field(...)  # TODO: enum of api, oauth
#     url: str = Field(...)
#     method: str = Field(...)
#     query_string: str = Field(...)
#     data: Any = Field(...)


# class ORCIDLogging(object):
#     def __init__(self, message: str, entry: ORCIDRequestLogEntry):
#         self.message = message
#         self.entry = entry

#     def __str__(self):
#         return json.dumps(dict(self.entry))


# orcid_logger = logging.getLogger('orcid-api')
# orcid_logger.setLevel(logging.DEBUG)


# logging.config.dictConfig(LOGGING_CONFIG)
