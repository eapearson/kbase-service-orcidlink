# Database Migration

As ORCID Link evolves over time, its database will too. This raises the question
of how a deployed database, populated with data, can be changed to support the
service.

Well, the answer is "database migration". The server provides a couple of
features to enable database migration.

First, it has a concept of
