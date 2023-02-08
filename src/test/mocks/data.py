import json
import os

from orcidlink.lib import utils


def load_test_data(collection: str, filename: str):
    test_data_path = utils.module_path(f"test/data/{collection}/{filename}.json")
    with open(test_data_path) as fin:
        return json.load(fin)


def load_data_file(filename: str):
    test_data_path = utils.module_path(f"test/data/{filename}")
    with open(test_data_path, "r") as fin:
        return fin.read()


def load_data_json(filename: str):
    test_data_path = utils.module_path(f"test/data/{filename}")
    with open(test_data_path, "r") as fin:
        return json.load(fin)


def project_root() -> str:
    root_dir = os.environ.get("PROJECT_ROOT")
    if root_dir is None:
        raise ValueError("PROJECT_ROOT environment variable not set")
    return root_dir
