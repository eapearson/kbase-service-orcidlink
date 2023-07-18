from test.mocks.data import load_test_data

import pytest

from orcidlink import model
from orcidlink.service_clients import orcid_api
from orcidlink.service_clients.orcid_api import ExternalId, ExternalIds, StringValue
from orcidlink.translators import to_service

# TODO: should rename file to test_orcid.py, but need a test config tweak, because it gets confused
# since there is already a test_orcid.py elsewhere...


# def load_test_data(filename: str):
#     test_data_path = f"{utils.module_dir()}/test/data/{filename}.json"
#     with open(test_data_path) as fin:
#         return json.load(fin)


# Test transform_work when we have the API running and can generate some test data.


def test_transform_work_summary():
    test_work_summary_no_doi = load_test_data("orcid", "work_summary_no_doi")
    with pytest.raises(
        ValueError,
        match='there must be one external id of type "doi" and relationship "self"',
    ):
        orcid_data = orcid_api.WorkSummary.model_validate(test_work_summary_no_doi)
        to_service.transform_work_summary(orcid_data)

    test_work_summary_multi_doi = load_test_data("orcid", "work_summary_multi_doi")
    with pytest.raises(
        ValueError,
        match='there may be only one external id of type "doi" and relationship "self"',
    ):
        orcid_data = orcid_api.WorkSummary.model_validate(test_work_summary_multi_doi)
        to_service.transform_work_summary(orcid_data)


def test_transform_work():
    test_work = orcid_api.Work.model_validate(
        load_test_data("orcid", "work_1526002")["bulk"][0]["work"]
    )
    test_profile = orcid_api.ORCIDProfile.model_validate(
        load_test_data("orcid", "profile")
    )
    test_work_transformed = model.Work.model_validate(
        load_test_data("orcid", "work_1526002_model")
    )
    value = to_service.transform_work(test_profile, test_work)
    assert value.model_dump() == test_work_transformed.model_dump()

    test_work = orcid_api.Work.model_validate(
        load_test_data("orcid", "work_1487805")["bulk"][0]["work"]
    )
    test_work_transformed = model.Work.model_validate(
        load_test_data("orcid", "work_1487805_model")
    )
    value = to_service.transform_work(test_profile, test_work)
    assert value.model_dump() == test_work_transformed.model_dump()


def test_transform_work_no_credit_name():
    test_work = orcid_api.Work.model_validate(
        load_test_data("orcid", "work_1526002")["bulk"][0]["work"]
    )
    test_profile = orcid_api.ORCIDProfile.model_validate(
        load_test_data("orcid", "profile")
    )
    test_profile.person.name.credit_name = None
    value = to_service.transform_work(test_profile, test_work)
    assert value.selfContributor.name == "Erik Pearson"


def test_transform_work_errors_no_journal():
    test_work = orcid_api.Work.model_validate(
        load_test_data("orcid", "work_1526002")["bulk"][0]["work"]
    )
    test_work.journal_title = None
    test_profile = orcid_api.ORCIDProfile.model_validate(
        load_test_data("orcid", "profile")
    )
    with pytest.raises(ValueError, match='the "journal" field may not be empty'):
        to_service.transform_work(test_profile, test_work)


def test_transform_work_errors_no_citation():
    test_work = orcid_api.Work.model_validate(
        load_test_data("orcid", "work_1526002")["bulk"][0]["work"]
    )
    test_work.citation = None
    test_profile = orcid_api.ORCIDProfile.model_validate(
        load_test_data("orcid", "profile")
    )
    with pytest.raises(ValueError, match='the "citation" field may not be empty'):
        to_service.transform_work(test_profile, test_work)


def test_transform_work_errors_no_short_description():
    test_work = orcid_api.Work.model_validate(
        load_test_data("orcid", "work_1526002")["bulk"][0]["work"]
    )
    test_work.short_description = None
    test_profile = orcid_api.ORCIDProfile.model_validate(
        load_test_data("orcid", "profile")
    )
    with pytest.raises(
        ValueError, match='the "short_description" field may not be empty'
    ):
        to_service.transform_work(test_profile, test_work)


def test_transform_work_errors_no_doi():
    test_work = orcid_api.Work.model_validate(
        load_test_data("orcid", "work_1526002")["bulk"][0]["work"]
    )
    test_work.external_ids.external_id = []
    test_profile = orcid_api.ORCIDProfile.model_validate(
        load_test_data("orcid", "profile")
    )
    with pytest.raises(
        ValueError,
        match='there must be one external id of type "doi" and relationship "self"',
    ):
        to_service.transform_work(test_profile, test_work)


def test_transform_work_errors_too_many_dois():
    test_work = orcid_api.Work.model_validate(
        load_test_data("orcid", "work_1526002")["bulk"][0]["work"]
    )
    test_work.external_ids = ExternalIds(
        external_id=[
            ExternalId(
                external_id_type="doi",
                external_id_value="foo",
                external_id_relationship="self",
                external_id_url=StringValue(value="bar"),
            ),
            ExternalId(
                external_id_type="doi",
                external_id_value="foo",
                external_id_relationship="self",
                external_id_url=StringValue(value="bar"),
            ),
        ]
    )
    test_profile = orcid_api.ORCIDProfile.model_validate(
        load_test_data("orcid", "profile")
    )
    with pytest.raises(
        ValueError,
        match='there may be only one external id of type "doi" and relationship "self"',
    ):
        to_service.transform_work(test_profile, test_work)


def test_transform_external_id():
    external_id_orcid_data = load_test_data("orcid", "external_id")
    external_id_service_data = load_test_data("orcid", "external_id_service")
    external_id_orcid = orcid_api.ExternalId.model_validate(external_id_orcid_data)
    external_id_transformed = to_service.transform_external_id(external_id_orcid)
    external_id_service = model.ExternalId.model_validate(external_id_service_data)

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


def test_transform_orcid_profile_no_credit_name():
    raw_test_profile = load_test_data("orcid", "profile")
    raw_test_profile["person"]["name"]["credit-name"] = None
    assert raw_test_profile["person"]["name"]["credit-name"] is None
    orcid_profile = orcid_api.ORCIDProfile.model_validate(raw_test_profile)
    assert orcid_profile.person.name.credit_name is None
    model_profile = to_service.orcid_profile(orcid_profile)
    assert model_profile.orcidId == "0000-0003-4997-3076"
    assert model_profile.creditName is None


def test_transform_orcid_profile_affiliation_group_not_list():
    raw_test_profile = load_test_data("orcid", "profile")
    # coerce the affiliation group to a single instance, rather than list.
    raw_test_profile["activities-summary"]["employments"][
        "affiliation-group"
    ] = raw_test_profile["activities-summary"]["employments"]["affiliation-group"][0]
    orcid_profile = orcid_api.ORCIDProfile.model_validate(raw_test_profile)
    model_profile = to_service.orcid_profile(orcid_profile)
    assert isinstance(model_profile.employment, list)
    assert model_profile.employment[0].name == "Lawrence Berkeley National Laboratory"
