import pytest

from orcidlink import model
from orcidlink.lib.service_clients import orcid_api
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


def test_transform_contributor_self():
    model_contributor = model.ORCIDContributorSelf(
        orcidId="1111-2222-3333-4444",
        name="bar",
        roles=[
            model.ContributorRole(role=model.ContributorRoleValue.conceptualization),
            model.ContributorRole(role=model.ContributorRoleValue.validation),
        ],
    )
    orcid_contributor_record = to_orcid.transform_contributor_self(model_contributor)
    assert len(orcid_contributor_record) == 2


def test_transform_contributor():
    model_contributor = model.ORCIDContributor(
        orcidId="1111-2222-3333-4444",
        name="bar",
        roles=[
            model.ContributorRole(role=model.ContributorRoleValue.conceptualization),
            model.ContributorRole(role=model.ContributorRoleValue.validation),
        ],
    )
    orcid_contributor_record = to_orcid.transform_contributor(model_contributor)
    assert len(orcid_contributor_record) == 2


def test_transform_contributors_self():
    model_contributors = [
        model.ORCIDContributorSelf(
            orcidId="1111-2222-3333-4444",
            name="bar",
            roles=[
                model.ContributorRole(
                    role=model.ContributorRoleValue.conceptualization
                ),
                model.ContributorRole(role=model.ContributorRoleValue.validation),
            ],
        ),
        model.ORCIDContributorSelf(
            orcidId="1111-2222-3333-4444",
            name="mouse",
            roles=[
                model.ContributorRole(role=model.ContributorRoleValue.formal_analysis),
                model.ContributorRole(
                    role=model.ContributorRoleValue.writing_review_editing
                ),
            ],
        ),
    ]

    orcid_contributors = to_orcid.transform_contributors_self(model_contributors)
    assert len(orcid_contributors) == 4


def test_transform_contributors():
    model_contributors = [
        model.ORCIDContributor(
            orcidId="1111-2222-3333-4444",
            name="bar",
            roles=[
                model.ContributorRole(
                    role=model.ContributorRoleValue.conceptualization
                ),
                model.ContributorRole(role=model.ContributorRoleValue.validation),
            ],
        ),
        model.ORCIDContributor(
            orcidId="1111-2222-3333-4444",
            name="mouse",
            roles=[
                model.ContributorRole(role=model.ContributorRoleValue.formal_analysis),
                model.ContributorRole(
                    role=model.ContributorRoleValue.writing_review_editing
                ),
            ],
        ),
    ]

    orcid_contributors = to_orcid.transform_contributors(model_contributors)
    assert len(orcid_contributors) == 4
