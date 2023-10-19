# TODO

## here are some changes I want to make as I add a schema;

Generaally, I'm noticing that the schema is python-centric, or rather, centric to the api, not the data. E.g. "kind" rather than "state" for the linking session:


## linking_sessions

kind -> state

or

put linking session states in to different tables. With the latter the schema is both more expressive and stricter wrt the required fields.

skip_prompt - why string not boolean? try to make it a boolean

username -> owner

## Errors

let us make all JSON-emitted errors compatible with JSON-RPC 2.0, meaning:

code: int
message: string - single sentence
data: any json, but we should always make it an object

I've been using string codes, because they are easier to grok, but for compliance,
we should use ints.

Note that JSON-RPC 2.0 reserves some codes: https://www.jsonrpc.org/specification#error_object

auth uses int codes ... e.g. https://github.com/kbase/auth2/blob/1408e96d0bacdff3ba41f58f3123a1d4708e1d44/src/us/kbase/auth2/lib/exceptions/ErrorType.java#L20

I think it would be good if each app had a range. there is no way to align all apps at this point in time, but it is feasible to have an error registry.

auth uses codes in the range 10000 - 70000: it is fairly greedy.

for future error codes, let us be more conservative. I think a range of 100 is fine for all services, apps, etc.

We could start at 1000:

| From | To   | Service   |
|------|------|-----------|
| 1000 | 1099 | orcidlink |


Each repo must have a human and machine readable file (format?) documenting all error codes.

E.g. yaml with the following fields

- `code` - numeric (integer) error code
- `description` - textual description of the error 
- `message` - default message to return for this code; actual usage may override this.
- `statusCode` - for errors returned directly as JSON, use this status code in the response.
- `dataSchema` - maybe? - a schema describing the data that will be sent in in the error response.