import json
import os


def load_test_data(data_dir: str, collection: str, filename: str):
    # data_dir = os.environ["TEST_DATA_DIR"]
    test_data_path = f"{data_dir}/{collection}/{filename}.json"
    with open(test_data_path) as fin:
        return json.load(fin)


def load_data_file(data_dir: str, filename: str):
    # data_dir = os.environ["TEST_DATA_DIR"]
    test_data_path = f"{data_dir}/{filename}"
    with open(test_data_path, "r") as fin:
        return fin.read()


def load_data_json(data_dir: str, filename: str):
    # data_dir = os.environ["TEST_DATA_DIR"]
    test_data_path = f"{data_dir}/{filename}"
    with open(test_data_path, "r") as fin:
        return json.load(fin)


# TODO: is this used???
def project_root() -> str:
    root_dir = os.environ.get("PROJECT_ROOT")
    if root_dir is None:
        raise ValueError("PROJECT_ROOT environment variable not set")
    return root_dir
