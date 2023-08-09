from orcidlink.lib.config import Config2
from orcidlink.storage.storage_model_mongo import StorageModelMongo


def storage_model() -> StorageModelMongo:
    config = Config2()
    return StorageModelMongo(
        config.get_mongo_host(),
        config.get_mongo_port(),
        config.get_mongo_database(),
        config.get_mongo_username(),
        config.get_mongo_password(),
    )
