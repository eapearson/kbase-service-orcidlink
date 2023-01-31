import pytest
from orcidlink.service_clients import orcid_api
from orcidlink.translators import to_orcid


def test_parse_date():
    assert to_orcid.parse_date("2000") == orcid_api.Date(
        year=orcid_api.StringValue(value="2000")
    )
    assert to_orcid.parse_date("2000/1") == orcid_api.Date(
        year=orcid_api.StringValue(value="2000"),
        month=orcid_api.StringValue(value="01"),
    )
    assert to_orcid.parse_date("2000/12") == orcid_api.Date(
        year=orcid_api.StringValue(value="2000"),
        month=orcid_api.StringValue(value="12"),
    )
    assert to_orcid.parse_date("2000/1/2") == orcid_api.Date(
        year=orcid_api.StringValue(value="2000"),
        month=orcid_api.StringValue(value="01"),
        day=orcid_api.StringValue(value="02"),
    )
    assert to_orcid.parse_date("2000/12/3") == orcid_api.Date(
        year=orcid_api.StringValue(value="2000"),
        month=orcid_api.StringValue(value="12"),
        day=orcid_api.StringValue(value="03"),
    )
    assert to_orcid.parse_date("2000/12/34") == orcid_api.Date(
        year=orcid_api.StringValue(value="2000"),
        month=orcid_api.StringValue(value="12"),
        day=orcid_api.StringValue(value="34"),
    )

    with pytest.raises(ValueError, match="Date must have 1-3 parts; has 4: a/b/c/d"):
        to_orcid.parse_date("a/b/c/d")
