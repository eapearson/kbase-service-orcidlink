import contextlib
import copy
import json
import os
from test.mocks.data import load_data_json
from test.mocks.env import MOCK_KBASE_SERVICES_PORT, MOCK_ORCID_OAUTH_PORT, TEST_ENV
from test.mocks.mock_contexts import (
    mock_auth_service,
    mock_orcid_oauth_service,
    no_stderr,
)
from test.mocks.testing_utils import clear_storage_model, generate_kbase_token
from typing import Any, Optional
from unittest import mock

from fastapi.testclient import TestClient

from orcidlink.lib.utils import posix_time_millis
from orcidlink.main import app
from orcidlink.model import LinkingSessionInitial, LinkRecord
from orcidlink.routers.manage import (
    FilterByEpochTime,
    FilterByORCIDId,
    FilterByUsername,
    QueryFind,
    QuerySort,
    QuerySortSpec,
    SearchQuery,
    augment_with_time_filter,
)
from orcidlink.storage.storage_model import storage_model

client = TestClient(app)

TEST_DATA_DIR = os.environ["TEST_DATA_DIR"]

TEST_LINK = load_data_json(TEST_DATA_DIR, "link1.json")
TEST_LINK_BAR = load_data_json(TEST_DATA_DIR, "link-bar.json")


@contextlib.contextmanager
def mock_services():
    with no_stderr():
        with mock_auth_service(MOCK_KBASE_SERVICES_PORT):
            yield


async def create_link(link_record):
    sm = storage_model()
    await sm.db.links.drop()
    await sm.create_link_record(LinkRecord.model_validate(link_record))


#
# Tests
#


async def test_is_manager_yup():
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            await create_link(TEST_LINK)

            client = TestClient(app)
            response = client.get(
                "/manage/is_manager",
                headers={"Authorization": generate_kbase_token("amanager")},
            )
            assert response.status_code == 200
            result = response.json()
            assert result["is_manager"] is True


async def test_is_manager_nope():
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            await create_link(TEST_LINK)

            client = TestClient(app)
            response = client.get(
                "/manage/is_manager",
                headers={"Authorization": generate_kbase_token("foo")},
            )
            assert response.status_code == 200
            result = response.json()
            assert result["is_manager"] is False


async def test_augment_with_time_filter_none():
    possible_filter = None

    result = augment_with_time_filter({}, "y", possible_filter)
    assert result == {}


async def test_augment_with_time_filter_some():
    possible_filter: FilterByEpochTime = FilterByEpochTime(eq=123)

    result = augment_with_time_filter({}, "y", possible_filter)
    assert result is not None
    assert "y" in result
    assert "$eq" in result["y"]
    assert result["y"]["$eq"] == 123

    possible_filter: FilterByEpochTime = FilterByEpochTime(gt=123)

    result = augment_with_time_filter({}, "y", possible_filter)
    assert result is not None
    assert "y" in result
    assert "$gt" in result["y"]
    assert result["y"]["$gt"] == 123

    possible_filter: FilterByEpochTime = FilterByEpochTime(gte=123)

    result = augment_with_time_filter({}, "y", possible_filter)
    assert result is not None
    assert "y" in result
    assert "$gte" in result["y"]
    assert result["y"]["$gte"] == 123

    possible_filter: FilterByEpochTime = FilterByEpochTime(lt=123)
    result = augment_with_time_filter({}, "y", possible_filter)
    assert result is not None
    assert "y" in result
    assert "$lt" in result["y"]
    assert result["y"]["$lt"] == 123

    possible_filter: FilterByEpochTime = FilterByEpochTime(lte=123)
    result = augment_with_time_filter({}, "y", possible_filter)
    assert result is not None
    assert "y" in result
    assert "$lte" in result["y"]
    assert result["y"]["$lte"] == 123


TEST_LINK = load_data_json(TEST_DATA_DIR, "link1.json")


async def test_get_links_no_query():
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            await create_link(TEST_LINK)

            client = TestClient(app)
            response = client.get(
                "/link", headers={"Authorization": generate_kbase_token("foo")}
            )
            assert response.status_code == 200

            # Now, a manager should be able to see the link.

            response2 = client.post(
                "/manage/links",
                headers={"Authorization": generate_kbase_token("amanager")},
                content=json.dumps({}),
            )
            assert response2.status_code == 200
            result = response2.json()
            assert "links" in result
            assert len(result["links"]) == 1


async def test_get_links_with_find():
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            foo_link = TEST_LINK

            bar_link = copy.deepcopy(TEST_LINK)
            bar_link["orcid_auth"]["orcid"] = "orcid-id-bar"
            bar_link["username"] = "bar"

            baz_link = copy.deepcopy(TEST_LINK)
            baz_link["orcid_auth"]["orcid"] = "orcid-id-baz"
            baz_link["username"] = "baz"

            sm = storage_model()
            await sm.db.links.drop()
            await sm.create_link_record(LinkRecord.model_validate(foo_link))
            await sm.create_link_record(LinkRecord.model_validate(bar_link))
            await sm.create_link_record(LinkRecord.model_validate(baz_link))

            client = TestClient(app)

            response2 = client.post(
                "/manage/links",
                headers={"Authorization": generate_kbase_token("amanager")},
                content=json.dumps({}),
            )
            assert response2.status_code == 200
            result = response2.json()
            assert "links" in result
            assert len(result["links"]) == 3

            def assert_find(find: QueryFind, expected_links: int) -> None:
                # Simple query of the username
                username_query = SearchQuery(
                    find=find, sort=None, offset=None, limit=None
                )

                response2 = client.post(
                    "/manage/links",
                    headers={"Authorization": generate_kbase_token("amanager")},
                    content=json.dumps(username_query.model_dump()),
                )
                assert response2.status_code == 200
                result = response2.json()
                assert len(result["links"]) == expected_links

            query_by_user = QueryFind(username=FilterByUsername(eq="foo"))
            assert_find(query_by_user, 1)
            query_by_orcid = QueryFind(orcid=FilterByORCIDId(eq="orcid-id-foo"))
            assert_find(query_by_orcid, 1)


async def test_get_links_with_sort():
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            foo_link = TEST_LINK

            bar_link = copy.deepcopy(TEST_LINK)
            bar_link["orcid_auth"]["orcid"] = "orcid-id-bar"
            bar_link["username"] = "bar"

            baz_link = copy.deepcopy(TEST_LINK)
            baz_link["orcid_auth"]["orcid"] = "orcid-id-baz"
            baz_link["username"] = "baz"

            sm = storage_model()
            await sm.db.links.drop()
            await sm.create_link_record(LinkRecord.model_validate(foo_link))
            await sm.create_link_record(LinkRecord.model_validate(bar_link))
            await sm.create_link_record(LinkRecord.model_validate(baz_link))

            client = TestClient(app)

            response2 = client.post(
                "/manage/links",
                headers={"Authorization": generate_kbase_token("amanager")},
                content=json.dumps({}),
            )
            assert response2.status_code == 200
            result = response2.json()
            assert "links" in result
            assert len(result["links"]) == 3

            def assert_sort(sort_spec: QuerySort) -> Any:
                # Simple query of the username
                username_query = SearchQuery(
                    find=None, sort=sort_spec, offset=None, limit=None
                )

                response2 = client.post(
                    "/manage/links",
                    headers={"Authorization": generate_kbase_token("amanager")},
                    content=json.dumps(username_query.model_dump()),
                )
                assert response2.status_code == 200
                return response2.json()

            query_sort_by_username: QuerySort = QuerySort(
                specs=[QuerySortSpec(field_name="username", descending=True)]
            )
            sorted = assert_sort(query_sort_by_username)
            assert sorted is not None
            assert len(sorted["links"]) == 3
            first_link = sorted["links"][0]
            assert first_link["username"] == "foo"


async def test_get_links_with_range():
    """
    In which we ensure that offset and limit work
    """
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            foo_link = TEST_LINK

            bar_link = copy.deepcopy(TEST_LINK)
            bar_link["orcid_auth"]["orcid"] = "orcid-id-bar"
            bar_link["username"] = "bar"

            baz_link = copy.deepcopy(TEST_LINK)
            baz_link["orcid_auth"]["orcid"] = "orcid-id-baz"
            baz_link["username"] = "baz"

            sm = storage_model()
            await sm.db.links.drop()
            await sm.create_link_record(LinkRecord.model_validate(foo_link))
            await sm.create_link_record(LinkRecord.model_validate(bar_link))
            await sm.create_link_record(LinkRecord.model_validate(baz_link))

            client = TestClient(app)

            response2 = client.post(
                "/manage/links",
                headers={"Authorization": generate_kbase_token("amanager")},
                content=json.dumps({}),
            )
            assert response2.status_code == 200
            result = response2.json()
            assert "links" in result
            assert len(result["links"]) == 3

            def assert_range(
                offset: Optional[int] = None, limit: Optional[int] = None
            ) -> Any:
                # Simple query of the username
                username_query = SearchQuery(
                    find=None, sort=None, offset=offset, limit=limit
                )

                response2 = client.post(
                    "/manage/links",
                    headers={"Authorization": generate_kbase_token("amanager")},
                    content=json.dumps(username_query.model_dump()),
                )
                assert response2.status_code == 200
                return response2.json()

            result = assert_range(offset=1, limit=2)
            assert len(result["links"]) == 2

            result = assert_range(offset=2, limit=1)
            assert len(result["links"]) == 1

            result = assert_range(offset=1)
            assert len(result["links"]) == 2

            result = assert_range(limit=1)
            assert len(result["links"]) == 1


async def test_get_links_error_not_admin():
    """
    In this test, we attempt to delete expired linking sessions with a
    non-admin account.
    """
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            client = TestClient(app)

            response2 = client.post(
                "/manage/links",
                headers={"Authorization": generate_kbase_token("foo")},
                content=json.dumps({}),
            )
            assert response2.status_code == 403


async def test_get_stats():
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            foo_link = TEST_LINK

            bar_link = copy.deepcopy(TEST_LINK)
            bar_link["orcid_auth"]["orcid"] = "orcid-id-bar"
            bar_link["username"] = "bar"

            baz_link = copy.deepcopy(TEST_LINK)
            baz_link["orcid_auth"]["orcid"] = "orcid-id-baz"
            baz_link["username"] = "baz"

            client = TestClient(app)

            response2 = client.get(
                "/manage/stats",
                headers={"Authorization": generate_kbase_token("amanager")},
            )

            stats = response2.json()
            assert stats["stats"]["links"]["all_time"] == 3

            sm = storage_model()
            await sm.db.links.drop()
            await sm.create_link_record(LinkRecord.model_validate(foo_link))
            await sm.create_link_record(LinkRecord.model_validate(bar_link))
            await sm.create_link_record(LinkRecord.model_validate(baz_link))

            response3 = client.get(
                "/manage/stats",
                headers={"Authorization": generate_kbase_token("amanager")},
            )
            stats = response3.json()

            # TODO: setup and test all status conditions.
            assert stats["stats"]["links"]["all_time"] == 3


async def test_get_stats_error_not_admin():
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            client = TestClient(app)

            response2 = client.get(
                "/manage/stats", headers={"Authorization": generate_kbase_token("foo")}
            )
            assert response2.status_code == 403


async def test_delete_expired_linking_sessions_none():
    """
    In this test, we have not created any sessions to delete.

    It should succeed with 204.
    """
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            client = TestClient(app)

            response2 = client.delete(
                "/manage/expired_linking_sessions",
                headers={"Authorization": generate_kbase_token("amanager")},
            )
            assert response2.status_code == 204


async def test_delete_expired_linking_sessions_some():
    """
    In this test, we create one session in each state.

    It should succeed with 204. We use the stats call to see how many
    sessions there are before (should all be 0) and after (should all be 1).
    """
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            client = TestClient(app)

            model = storage_model()
            await clear_storage_model()
            await model.create_linking_session(
                LinkingSessionInitial(
                    session_id="session-foo",
                    username="foo",
                    created_at=posix_time_millis(),
                    expires_at=posix_time_millis() - 60_000,
                )
            )

            stats = await model.get_stats()
            assert stats.linking_sessions_initial.expired == 1

            # response3 = client.get(
            #     "/manage/stats",
            #     headers={"Authorization": generate_kbase_token("amanager")}
            # )
            # stats = response3.json()

            # TODO: setup and test all status conditions.
            # assert stats["stats"]["links"]['all_time'] == 3

            response2 = client.delete(
                "/manage/expired_linking_sessions",
                headers={"Authorization": generate_kbase_token("amanager")},
            )
            assert response2.status_code == 204

            # response3 = client.get(
            #     "/manage/stats",
            #     headers={"Authorization": generate_kbase_token("amanager")}
            # )
            # stats = response3.json()

            # TODO: setup and test all status conditions.
            # assert stats["stats"]["links"]['all_time'] == 3

            stats = await model.get_stats()
            assert stats.linking_sessions_initial.expired == 0


async def test_delete_expired_linking_sessions_error_not_admin():
    """
    In this test, we attempt to delete expired linking sessions with a
    non-admin account.
    """
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            client = TestClient(app)

            response2 = client.delete(
                "/manage/expired_linking_sessions",
                headers={"Authorization": generate_kbase_token("foo")},
            )
            assert response2.status_code == 403


async def test_get_linking_sessions_some():
    """
    In this test, we create one session in each state.

    It should succeed with 204. We use the stats call to see how many
    sessions there are before (should all be 0) and after (should all be 1).
    """
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            client = TestClient(app)

            model = storage_model()
            await clear_storage_model()
            await model.create_linking_session(
                LinkingSessionInitial(
                    session_id="session-foo",
                    username="foo",
                    created_at=posix_time_millis(),
                    expires_at=posix_time_millis() - 60_000,
                )
            )

            stats = await model.get_stats()
            assert stats.linking_sessions_initial.expired == 1

            # response3 = client.get(
            #     "/manage/stats",
            #     headers={"Authorization": generate_kbase_token("amanager")}
            # )
            # stats = response3.json()

            # TODO: setup and test all status conditions.
            # assert stats["stats"]["links"]['all_time'] == 3

            response2 = client.get(
                "/manage/linking_sessions",
                headers={"Authorization": generate_kbase_token("amanager")},
            )
            assert response2.status_code == 200

            sessions = response2.json()
            assert "initial_linking_sessions" in sessions
            assert len(sessions["initial_linking_sessions"]) == 1
            assert len(sessions["started_linking_sessions"]) == 0
            assert len(sessions["completed_linking_sessions"]) == 0


async def test_get_linking_sessions_error_not_admin():
    """
    In this test, we attempt to delete expired linking sessions with a
    non-admin account.
    """
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            client = TestClient(app)

            response2 = client.get(
                "/manage/linking_sessions",
                headers={"Authorization": generate_kbase_token("foo")},
            )
            assert response2.status_code == 403


async def test_get_link():
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            await create_link(TEST_LINK)

            client = TestClient(app)
            response = client.get(
                "/link", headers={"Authorization": generate_kbase_token("foo")}
            )
            assert response.status_code == 200

            # Now, a manager should be able to see the link.

            response2 = client.get(
                "/manage/link/foo",
                headers={"Authorization": generate_kbase_token("amanager")},
            )
            assert response2.status_code == 200
            result = response2.json()
            assert result is not None


async def test_get_link_error_not_found():
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            await create_link(TEST_LINK)

            client = TestClient(app)
            response = client.get(
                "/link", headers={"Authorization": generate_kbase_token("foo")}
            )
            assert response.status_code == 200

            # Now, a manager should be able to see the link.

            response2 = client.get(
                "/manage/link/bar",
                headers={"Authorization": generate_kbase_token("amanager")},
            )
            assert response2.status_code == 404


async def test_get_link_error_not_admin():
    """
    In this test, we attempt to delete expired linking sessions with a
    non-admin account.
    """
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            client = TestClient(app)

            response2 = client.get(
                "/manage/link/foo",
                headers={"Authorization": generate_kbase_token("foo")},
            )
            assert response2.status_code == 403


async def test_patch_refresh_tokens():
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT):
                await create_link(TEST_LINK_BAR)

                client = TestClient(app)

                response = client.patch(
                    "/manage/refresh-tokens/bar",
                    headers={"Authorization": generate_kbase_token("foo")},
                )
                assert response.status_code == 403

                response2 = client.patch(
                    "/manage/refresh-tokens/bar",
                    headers={"Authorization": generate_kbase_token("amanager")},
                )
                assert response2.status_code == 200

                response_value = response2.json()
                assert response_value["link"]["username"] == TEST_LINK_BAR["username"]


async def test_patch_refresh_tokens_error_not_found():
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT):
                await create_link(TEST_LINK_BAR)

                client = TestClient(app)

                response2 = client.patch(
                    "/manage/refresh-tokens/baz",
                    headers={"Authorization": generate_kbase_token("amanager")},
                )
                assert response2.status_code == 404
