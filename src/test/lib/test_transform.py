import json

from orcidlink.lib import utils
from orcidlink.lib.transform import parse_date, raw_work_to_work


def load_test_data(filename: str):
    test_data_path = f"{utils.module_dir()}/src/test/lib/test_transform/{filename}.json"
    with open(test_data_path) as fin:
        return json.load(fin)


# Test raw_work_to_work when we have the API running and can generate some test data.


def test_parse_date():
    assert parse_date("2000") == {"year": {"value": "2000"}}
    assert parse_date("2000/1") == {"year": {"value": "2000"}, "month": {"value": "01"}}
    assert parse_date("2000/12") == {
        "year": {"value": "2000"},
        "month": {"value": "12"},
    }
    assert parse_date("2000/1/2") == {
        "year": {"value": "2000"},
        "month": {"value": "01"},
        "day": {"value": "02"},
    }
    assert parse_date("2000/12/3") == {
        "year": {"value": "2000"},
        "month": {"value": "12"},
        "day": {"value": "03"},
    }
    assert parse_date("2000/12/34") == {
        "year": {"value": "2000"},
        "month": {"value": "12"},
        "day": {"value": "34"},
    }


def test_raw_work_to_work():
    test_work = load_test_data("work_1526002")
    test_work_transformed = load_test_data("work_1526002_transformed")
    value = raw_work_to_work(test_work)
    assert value == test_work_transformed
