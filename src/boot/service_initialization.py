import json
import logging
from typing import Any, Dict, OrderedDict, TypedDict, List
import os

import pymongo.errors
from bson import json_util
from orcidlink.lib import logger
from orcidlink.lib.config import config, get_service_description
from orcidlink.lib.utils import posix_time_millis
from pymongo import MongoClient


def test():
    print("logging?")
    logger.log_level(logging.DEBUG)
    logger.log_event("initialization-test", {"is_a": "test"}, logging.INFO)


def make_db_client() -> MongoClient[Dict[str, Any]]:
    c = config()
    return MongoClient(
        host=c.mongo.host,
        port=c.mongo.port,
        username=c.mongo.username,
        password=c.mongo.password,
        authSource=c.mongo.database,
        retrywrites=False,
    )


def check_db_connection():
    try:
        client = make_db_client()
    except pymongo.errors.ConnectionFailure as cf:
        return {"status": "error", "code": "connection-failure", "error": str(cf)}
    td = client.topology_description
    return {
        "status": "ok",
        "compatible": td.check_compatible(),
        "version": td.common_wire_version,
        "has_known_servers": td.has_known_servers,
        "readable": td.has_readable_server(),
        "writable": td.has_writable_server(),
    }


def check_db_database():
    try:
        client = make_db_client()
    except pymongo.errors.ConnectionFailure as cf:
        return {"status": "error", "code": "connection-failure", "message": str(cf)}
    database_name = config().mongo.database
    try:
        db = client.get_database(database_name)
    except Exception as dbe:
        return {
            "status": "error",
            "code": "database-not-found",
            "message": f'The orcidlink database "{database_name}" does not exist: {str(dbe)}',
        }

    if "description" not in db.list_collection_names():
        description_json = None
    else:
        # return {
        #     'status': 'error',
        #     'code': 'description-not-found',
        #     'message': f'The "description" collection must exist in the "{database_name}" database'
        # }

        description = db.get_collection("description")

        # count = description.estimated_document_count()
        #
        # if count == 0:
        #     return {
        #         'status': 'error',
        #         'code': 'description-not-found',
        #         'message': f'The "description" collection must have a document'
        #     }
        # if count > 1:
        #     return {
        #         'status': 'error',
        #         'code': 'description-invalid',
        #         'message': f'The "description" collection has too many documents ({description.count_documents()})'
        #     }

        description_doc = description.find_one()
        if description_doc is None:
            return {
                "status": "error",
                "code": "description-not-found",
                "message": f'The "description" collection must have a document',
            }

        del description_doc["_id"]
        description_json = json.loads(json_util.dumps(description_doc))

    return {
        "status": "ok",
        "collections": db.list_collection_names(),
        "description": description_json,
    }


def load_schema(version: str, collection: str) -> OrderedDict:
    schema_dir = os.path.join(os.path.dirname(__file__), "../../schema")
    schema_path = f"{schema_dir}/{version}/{collection}.json"
    with open(schema_path, "r", encoding="utf-8") as schema_file:
        return json.load(schema_file)


class Message(TypedDict):
    at: int
    message: str


def add_message(messages: List[Message], message: str) -> List[Message]:
    return messages.append({"at": posix_time_millis(), "message": message})


def create_collection(db, name: str, service_version: str):
    schema = load_schema(f"v{service_version}", name)["validator"]
    collection = db.create_collection(name, validator=schema)
    return collection


def initialize_v0_2_1(db):
    actions = []
    service_version = "0.2.1"

    create_collection(db, "linking_sessions_initial", service_version)
    actions.append(
        {
            "at": posix_time_millis(),
            "message": "created linking_session_initial collection",
        }
    )

    create_collection(db, "linking_sessions_started", service_version)
    actions.append(
        {
            "at": posix_time_millis(),
            "message": "created linking_session_started collection",
        }
    )

    create_collection(db, "linking_sessions_completed", service_version)
    actions.append(
        {
            "at": posix_time_millis(),
            "message": "created linking_session_completed collection",
        }
    )

    links_collection = create_collection(db, "links", service_version)
    actions.append({"at": posix_time_millis(), "message": "created links collection"})

    links_collection.create_index("username", unique=True)
    actions.append(
        {
            "at": posix_time_millis(),
            "message": "created username index for linking_session_completed collection",
        }
    )

    description_collection = create_collection(db, "description", service_version)
    actions.append(
        {"at": posix_time_millis(), "message": "created description collection"}
    )

    description_collection.insert_one(
        {
            "version": "0.2.1",
            "at": posix_time_millis(),
            "migrated": True,
            "messages": actions,
        }
    )

    return {
        "status": "ok",
        "message": "Migration successfully completed",
        "actions": actions,
    }


def migrate_db():
    try:
        client = make_db_client()
        database_name = config().mongo.database
        db = client.get_database(database_name)
        description = db.get_collection("description").find_one()

        service_description = get_service_description()
        service_version = service_description.version

        if service_version == "0.2.1":
            if description is None:
                return initialize_v0_2_1(db)
                # Initial migration. In fact, this is the first version for which there is a
                # migration defined.
                # actions = []
                # needs an index
                # linking sessions are looked up by session_id

                # create_collection(db, "linking_sessions_initial", service_version)
                # create_collection(db, "linking_sessions_started", service_version)
                # create_collection(db, "linking_sessions_complete", service_version)
                # links_collection = create_collection(db, "links", service_version)
                # links_collection.create_index("username", unique=True)
                # description_collection = create_collection(db, "description", service_version)

                # linking_sessions_schema = load_schema(f'v{service_version}', 'linking_sessions')['validator']
                # linking_sessions_collection = db.create_collection("linking_sessions", validator=linking_sessions_schema)

                # # Linking sessions started

                # linking_sessions_schema = load_schema(f'v{service_version}', 'linking_sessions')['validator']
                # linking_sessions_collection = db.create_collection("linking_session_started", validator=linking_sessions_started_schema)

                # # linking_sessions = db.get_collection("linking_sessions")
                # linking_sessions_collection.create_index("session_id", unique=True)
                # actions.append({"at": posix_time_millis(), "message": "added index on session_id to linking_sessions"})

                # links are looked up by username
                # links_schema = load_schema(f'v{service_version}', 'links_schema')['validator']
                # links = db.get_collection("links")
                # links.create_index("username", unique=True)
                # actions.append({"at": posix_time_millis(), "message": "added unique index on username to links"})

                # # # links can also be looked up by, and must be unique by, orcid id!

                # # # The description collection describes the database!

                # description_schema = load_schema(f'v{service_version}', 'description')["validator"]
                # # print('About to create description - ', description_schema)
                # db.create_collection('description', validator=description_schema)

                # print('Created collection "description"')

            else:
                database_version = description["version"]
                if database_version == service_version:
                    # I don't think this case ever appeared in the wild, but it did in testing.
                    if description["migrated"] is True:
                        return {
                            "status": "ok",
                            "code": "migration-not-required",
                            "message": "Database already migrated for this version",
                        }

                    # The first migration, which will be the case in this branch, adds index and
                    # then updates the description to show that it has been migrated.

                    actions = []
                    # needs an index
                    # linking sessions are looked up by session_id
                    linking_sessions = db.get_collection("linking_sessions")
                    linking_sessions.create_index("session_id")
                    actions.append("added index on session_id to linking_sessions")

                    # links are looked up by username
                    links = db.get_collection("links")
                    links.create_index("username")
                    actions.append("added index on username to links")

                    db.get_collection("description").update_one(
                        {"_id": description["_id"]}, {"$set": {"migrated": True}}
                    )

                    return {
                        "status": "ok",
                        "message": "Migration successfully completed",
                        "actions": actions,
                    }
                else:
                    return {
                        "status": "error",
                        "code": "migration-error",
                        "message": f"No migration available from db version {description['version']} to service version {service_version}",
                    }
        else:
            # Initialize latest version.

            return {
                "status": "error",
                "code": "migration-error",
                "message": f"No migration available for version {service_version}",
            }
    except Exception as dbe:
        print("DEBUGgin error", str(dbe))
        return {
            "status": "error",
            "code": "migration-error",
            "message": f"The migration failed: {str(dbe)}",
        }


# def list_db_collections():


def main():
    logger.log_level(logging.DEBUG)
    logger.log_event(
        "initialization-start", {"message": "initializing orcidlink service"}
    )

    result = check_db_connection()
    logger.log_event("initialization-check-connection", result)
    if result["status"] == "error":
        raise Exception("mongodb connection check failed - see logs")

    result = check_db_database()
    logger.log_event("initialization-check-database", result)
    if result["status"] == "error":
        raise Exception("mongodb database check failed - see logs")

    result = migrate_db()
    logger.log_event("initialization-migrate-database", result)
    if result["status"] == "error":
        raise Exception("mongodb database migration failed - see logs")


main()
