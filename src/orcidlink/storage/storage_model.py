from orcidlink.runtime import config
from orcidlink.storage.storage_model_mongo import StorageModelMongo


def storage_model() -> StorageModelMongo:
    return StorageModelMongo(
        config().mongo_host,
        config().mongo_port,
        config().mongo_database,
        config().mongo_username,
        config().mongo_password,
    )
