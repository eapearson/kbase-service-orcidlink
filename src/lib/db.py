import datetime
import json
import os
from pathlib import Path

from lib import utils


################################
# Database
################################


class FileStorage:
    def __init__(self, directory="work/data"):
        self.root_path = Path(os.path.join(utils.module_dir(), directory))

    def get_collection_file_path(self, collection, name, add_extension=True, require_exists=True,
                                 require_not_exists=False):
        dir_path = Path(self.root_path, collection)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
        if add_extension:
            filename = f"{name}.json"
        else:
            filename = name
        file_path = os.path.join(dir_path, filename)
        if require_exists:
            if not Path(file_path).exists():
                raise Exception('File does not exist');
        if require_not_exists:
            if Path(file_path).exists():
                raise Exception('File already exists');
        return file_path

    def get_collection_path(self, collection):
        dir_path = Path(self.root_path, collection)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path

    def get_collection_index(self, collection):
        file_path = self.get_collection_file_path(collection, 'index', require_exists=False)
        if not Path(file_path).exists():
            return {'last_id': 0, 'entities': {}}

        with open(file_path, "r") as db_file:
            return json.load(db_file)

    def create_collection_index_entry(self, collection, name):
        index = self.get_collection_index(collection)
        index['last_id'] += 1
        # TODO: add date created
        index['entities'][name] = {
            'id': index['last_id'],
            'created': datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
        }

        self.save_collection_index(collection, index)

        return index['last_id']

    def save_collection_index(self, collection, index):
        file_path = self.get_collection_file_path(collection, 'index', require_exists=False)
        with open(file_path, "w") as db_file:
            json.dump(index, db_file, indent=4)

    def delete_collection_index_entry(self, collection, name):
        index = self.get_collection_index(collection)
        entry = index['entities'].get(name)
        if entry is None:
            return

        del index['entities'][name]

        self.save_collection_index(collection, index)

        return

    def get_collection_index_id(self, collection, name):
        index = self.get_collection_index(collection)
        entry = index['entities'].get(name)
        if entry is None:
            return None
        return entry['id']

    def get_collection_entity(self, collection, name):
        entity_id = self.get_collection_index_id(collection, name)
        if entity_id is None:
            return None

        return self.get_collection_entity_by_id(collection, entity_id)

    def get_collection_entity_by_id(self, collection, entity_id):
        if entity_id is None:
            return None

        file_path = self.get_collection_file_path(collection, entity_id, require_exists=False)
        if not Path(file_path).exists():
            # TODO: actually, this is an error.
            return None
        with open(file_path, "r") as db_file:
            return json.load(db_file)

    # Public data access methods

    def get(self, collection, name):
        return self.get_collection_entity(collection, name)

    def list(self, collection):
        index = self.get_collection_index(collection)

        entity_values = [value for entity_name, value in index['entities'].items()]

        result = list(map(
            lambda entity_value: self.get_collection_entity_by_id(collection, entity_value['id']),
            entity_values
        ))

        return result

    def save(self, collection, name, value):
        entity_id = self.get_collection_index_id(collection, name)
        file_path = self.get_collection_file_path(collection, str(entity_id), require_exists=False)
        with open(file_path, "w") as db_file:
            json.dump(value, db_file, indent=4)

    # TODO: manipulate index, manipulate entity; then as a unit save index, save entity.
    def create(self, collection, name, value):
        entity_id = self.create_collection_index_entry(collection, name)
        file_path = self.get_collection_file_path(collection, str(entity_id), require_exists=False,
                                                  require_not_exists=True)
        with open(file_path, "w") as db_file:
            json.dump(value, db_file, indent=4)

    def update(self, collection, name, value):
        entity_id = self.get_collection_index_id(collection, name)
        file_path = self.get_collection_file_path(collection, str(entity_id), require_exists=True)
        with open(file_path, "w") as db_file:
            json.dump(value, db_file, indent=4)

    def delete(self, collection, name):
        entity_id = self.get_collection_index_id(collection, name)
        file_path = self.get_collection_file_path(collection, str(entity_id), require_exists=False)

        # Ignore delete request if does not exist; this ensures it is idemptotent.
        if not Path(file_path).exists():
            return

        try:
            os.remove(file_path)
        except:
            # We don't care if it fails, and we don't want to use exists first
            # as it encourages a race condition.
            # TODO: detect reason; if doesn't exist, ok; otherwise raise error
            pass

        try:
            self.delete_collection_index_entry(collection, name)
        except:
            pass
