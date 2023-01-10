import json

from orcidlink.lib import utils


def load_test_data(collection: str, filename: str):
    test_data_path = f"{utils.module_dir()}/src/test/data/{collection}/{filename}.json"
    with open(test_data_path) as fin:
        return json.load(fin)
