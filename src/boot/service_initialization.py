import json
import logging
import os
from typing import Any, Dict, List, OrderedDict, TypedDict

import pymongo.errors
from bson import json_util
from pymongo import MongoClient

from orcidlink.lib.logger import log_level, log_event
from orcidlink.lib.config import Config2, get_service_description
from orcidlink.lib.utils import posix_time_millis


def test():
    log_level(logging.DEBUG)
    log_event("initialization-test", {"is_a": "test"}, logging.INFO)


def make_db_client() -> MongoClient[Dict[str, Any]]:
    config = Config2()
    return MongoClient(
        host=config.get_mongo_host(),
        port=config.get_mongo_port(),
        username=config.get_mongo_username(),
        password=config.get_mongo_password(),
        authSource=config.get_mongo_database(),
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
    config = Config2()
    database_name = config.get_mongo_database()
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
    messages.append({"at": posix_time_millis(), "message": message})
    return messages


def get_schema(service_version, collection_name):
    return load_schema(f"v{service_version}", collection_name)["validator"]


def create_collection(db, name: str, service_version: str):
    schema = get_schema(service_version, name)
    collection = db.create_collection(name, validator=schema)
    return collection


def migrate_v021_to_v030(db):
    service_version = "0.3.0"

    # The first migration, which will be the case in this branch, adds index and
    # then updates the description to show that it has been migrated.

    actions = []

    # Add schema for links
    db.command("collMod", "links", validator=get_schema(service_version, "links"))
    actions.append(
        {
            "at": posix_time_millis(),
            "message": "added schema for 'links'",
        }
    )

    # Remove old linking_sessions
    db.get_collection("linking_sessions").drop()
    actions.append(
        {
            "at": posix_time_millis(),
            "message": "dropped 'linking_sessions'",
        }
    )

    # Add linking_sessions_initial
    create_collection(db, "linking_sessions_initial", service_version)
    actions.append(
        {
            "at": posix_time_millis(),
            "message": "created 'linking_session_initial' collection",
        }
    )

    # Add linking_sessions_started
    create_collection(db, "linking_sessions_started", service_version)
    actions.append(
        {
            "at": posix_time_millis(),
            "message": "created 'linking_session_started' collection",
        }
    )

    # Add linking_sessions_completed
    create_collection(db, "linking_sessions_completed", service_version)
    actions.append(
        {
            "at": posix_time_millis(),
            "message": "created 'linking_session_completed' collection",
        }
    )

    # Update the database description
    description = db.get_collection("description").find_one()
    db.get_collection("description").update_one(
        {"_id": description["_id"]},
        {"$set": {"version": service_version, "migrated": True}},
    )

    return {
        "status": "ok",
        "message": "Migration successfully completed",
        "actions": actions,
    }


def initialize_v021(db):
    actions = []
    service_version = "0.2.1"

    # linking sessions are looked up by session_id
    linking_sessions = db.get_collection("linking_sessions")
    linking_sessions.create_index("session_id")
    actions.append("added index on session_id to linking_sessions")

    # links are looked up by username
    links = db.get_collection("links")
    links.create_index("username")
    actions.append("added index on username to links")

    db.get_collection("description").insert_one(
        {"version": service_version, "at": posix_time_millis(), "migrated": True}
    )

    return {
        "status": "ok",
        "message": "Migration successfully completed",
        "actions": actions,
    }


def initialize_v030(db):
    actions = []
    service_version = "0.3.0"

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
            "version": service_version,
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
        database_name = Config2().get_mongo_database()
        db = client.get_database(database_name)
        description = db.get_collection("description").find_one()

        service_description = get_service_description()

        if service_description.version == "0.2.1":
            if description is None:
                return initialize_v021(db)
            else:
                return {
                    "status": "error",
                    "code": "migration-error",
                    "message": f"No migration available for version {service_description.version}",
                }

        elif service_description.version == "0.3.0":
            if description is None:
                return initialize_v030(db)
            else:
                database_version = description["version"]
                if database_version == service_description.version:
                    return {
                        "status": "ok",
                        "code": "migration-not-required",
                        "message": "Database already migrated for this version",
                    }
                elif database_version == "0.2.1":
                    return migrate_v021_to_v030(db)
                else:
                    return {
                        "status": "error",
                        "code": "migration-error",
                        "message": f"No migration available from db version {description['version']} to service version {service_description.version}",
                    }

        else:
            return {
                "status": "error",
                "code": "migration-error",
                "message": f"No migration available for version {service_description.version}",
            }
    except Exception as dbe:
        print("DEBUGgin error", str(dbe))
        return {
            "status": "error",
            "code": "migration-error",
            "message": f"The migration failed: {str(dbe)}",
        }


def main():
    log_level(logging.DEBUG)
    log_event("initialization-start", {"message": "initializing orcidlink service"})

    result = check_db_connection()
    log_event("initialization-check-connection", result)
    if result["status"] == "error":
        raise Exception("mongodb connection check failed - see logs")

    result = check_db_database()
    log_event("initialization-check-database", result)
    if result["status"] == "error":
        raise Exception("mongodb database check failed - see logs")

    result = migrate_db()
    log_event("initialization-migrate-database", result)
    if result["status"] == "error":
        raise Exception("mongodb database migration failed - see logs")


main()
