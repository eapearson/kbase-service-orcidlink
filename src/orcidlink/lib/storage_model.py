from orcidlink.lib.config import config

from orcidlink.lib.storage_model_mongo import StorageModelMongo

MOCK_MONGO = None


def storage_model():
    if config().module.STORAGE_MODEL == 'mongo':
        return StorageModelMongo(
            config().module.MONGO_USERNAME,
            config().module.MONGO_PASSWORD)
    else:
        raise ValueError(f'Unsupported storage model "{config().module.STORAGE_MODEL}"')
