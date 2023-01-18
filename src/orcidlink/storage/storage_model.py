from orcidlink.lib.config import config
from orcidlink.storage.storage_model_mongo import StorageModelMongo


def storage_model():
    mc = config().mongo
    return StorageModelMongo(mc.host, mc.port, mc.database, mc.username, mc.password)
