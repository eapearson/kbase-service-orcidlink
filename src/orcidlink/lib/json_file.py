import json
import os
from pathlib import Path

from orcidlink.lib import utils


def get_json_file_path(name):
    root_path = Path(os.path.join(utils.module_dir(), "data"))
    if not root_path.exists():
        raise Exception("Root directory does not exist")

    filename = f"{name}.json"

    file_path = os.path.join(root_path, filename)

    if not Path(file_path).exists():
        raise Exception("File does not exist")

    return file_path


def get_json_file(name):
    file_path = get_json_file_path(name)
    with open(file_path, "r") as db_file:
        return json.load(db_file)
