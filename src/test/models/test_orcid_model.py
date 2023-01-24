import json

from orcidlink.lib import utils
from orcidlink.model import ORCIDWork
from orcidlink.models.orcid import raw_work_to_work


# TODO: should rename file to test_orcid.py, but need a test config tweak, because it gets confused
# since there is already a test_orcid.py elsewhere...


def load_test_data(filename: str):
    test_data_path = f"{utils.module_dir()}/src/test/lib/test_transform/{filename}.json"
    with open(test_data_path) as fin:
        return json.load(fin)


# Test raw_work_to_work when we have the API running and can generate some test data.


def test_raw_work_to_work():
    test_work = load_test_data("work_1526002")
    test_work_transformed = ORCIDWork.parse_obj(
        load_test_data("work_1526002_transformed")
    )
    value = raw_work_to_work(test_work)
    assert value == test_work_transformed
