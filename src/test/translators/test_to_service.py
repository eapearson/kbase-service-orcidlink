import json

from orcidlink import model
from orcidlink.lib import utils
from orcidlink.service_clients import orcid_api
from orcidlink.translators import to_service  # raw_work_to_work


# TODO: should rename file to test_orcid.py, but need a test config tweak, because it gets confused
# since there is already a test_orcid.py elsewhere...


def load_test_data(filename: str):
    test_data_path = f"{utils.module_dir()}/test/data/{filename}.json"
    with open(test_data_path) as fin:
        return json.load(fin)


# Test raw_work_to_work when we have the API running and can generate some test data.


def test_raw_work_to_work():
    test_work = orcid_api.Work.parse_obj(load_test_data("orcid/work_1526002"))
    test_work_transformed = model.ORCIDWork.parse_obj(
        load_test_data("orcid/work_1526002_normalized")
    )
    value = to_service.raw_work_to_work(test_work)
    assert value.dict() == test_work_transformed.dict()


def test_transform_external_id():
    external_id_orcid_data = load_test_data("orcid/external_id")
    external_id_service_data = load_test_data("orcid/external_id_service")
    external_id_orcid = orcid_api.ORCIDExternalId.parse_obj(external_id_orcid_data)
    external_id_transformed = to_service.transform_external_id(external_id_orcid)
    external_id_service = model.ExternalId.parse_obj(external_id_service_data)

    assert external_id_transformed == external_id_service


def test_orcid_date_to_string_date():
    result = to_service.orcid_date_to_string_date(
        orcid_api.Date(year=orcid_api.StringValue(value="2000"))
    )

    assert result == "2000"

    result = to_service.orcid_date_to_string_date(
        orcid_api.Date(
            year=orcid_api.StringValue(value="2000"),
            month=orcid_api.StringValue(value="01"),
        )
    )

    assert result == "2000/1"

    result = to_service.orcid_date_to_string_date(
        orcid_api.Date(
            year=orcid_api.StringValue(value="2000"),
            month=orcid_api.StringValue(value="01"),
            day=orcid_api.StringValue(value="02"),
        )
    )

    assert result == "2000/1/2"
