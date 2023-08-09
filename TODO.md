# TODO

## here are some changes I want to make as I add a schema;

Generaally, I'm noticing that the schema is python-centric, or rather, centric to the api, not the data. E.g. "kind" rather than "state" for the linking session:


## linking_sessions

kind -> state

or

put linking session states in to different tables. With the latter the schema is both more expressive and stricter wrt the required fields.

skip_prompt - why string not boolean? try to make it a boolean

username -> owner