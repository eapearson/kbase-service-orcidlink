import json

from orcidlink.lib import utils


def load_test_data(collection: str, filename: str):
    test_data_path = f"{utils.module_dir()}/test/data/{collection}/{filename}.json"
    with open(test_data_path) as fin:
        return json.load(fin)


def load_data_file(filename: str):
    test_data_path = f"{utils.module_dir()}/test/data/{filename}"
    with open(test_data_path, "r") as fin:
        return fin.read()


def load_data_json(filename: str):
    test_data_path = f"{utils.module_dir()}/test/data/{filename}"
    with open(test_data_path, "r") as fin:
        return json.load(fin)
