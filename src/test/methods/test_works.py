import contextlib
import os
from test.mocks.env import MOCK_KBASE_SERVICES_PORT, MOCK_ORCID_API_PORT
from test.mocks.mock_contexts import (
    mock_auth_service,
    mock_orcid_api_service,
    no_stderr,
)

import pytest

from orcidlink.model import LinkRecord
from orcidlink.storage import storage_model


@pytest.fixture
def fake_fs(fs):
    data_dir = os.environ["TEST_DATA_DIR"]
    fs.add_real_directory(data_dir)
    yield fs


# TEST_LINK = load_data_json("link1.json")

TEST_LINK = {
    "orcid_auth": {
        "access_token": "access-token",
        "token_type": "bearer",
        "refresh_token": "refresh-token",
        "expires_in": 631138518,
        "scope": "/read-limited openid /activities/update",
        "name": "Foo bar",
        "orcid": "0000-0003-4997-3076",
    },
    "created_at": 1669943616532,
    "expires_at": 2301082134532,
    "retires_at": 2301082134532,
    "username": "foo",
}


async def create_link():
    sm = storage_model.storage_model()
    await sm.db.links.drop()
    await sm.create_link_record(LinkRecord.model_validate(TEST_LINK))


@contextlib.contextmanager
def mock_services():
    with no_stderr():
        with mock_auth_service(MOCK_KBASE_SERVICES_PORT):
            with mock_orcid_api_service(MOCK_ORCID_API_PORT):
                yield


# def test_external_id():
#     with mock.patch.dict(os.environ, TEST_ENV, clear=True):
#         external_id = orcid_api.ExternalId(
#             external_id_type="foo",
#             external_id_value="value",
#             external_id_normalized=None,
#             external_id_url=orcid_api.ORCIDStringValue(value="url"),
#             external_id_relationship="rel",
#         )
# orcid_api.ORCIDExternalId.model_validate({
#     "external-id-type": "foo",
#     "external-id-value": "value",
#     "external-id-normalized": None,
#     "external-id-url": {
#         "value": "url"
#     },
#     "external-id-relationship": "rel"
# })
