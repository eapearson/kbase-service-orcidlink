import itertools
import json
from typing import Any

from fastapi.testclient import TestClient

from orcidlink.model import LinkRecord
from orcidlink.storage.storage_model import storage_model


def repeat_str(it: str, repetitions: int) -> str:
    return "".join(itertools.repeat(it, repetitions))


def generate_kbase_token(part: str) -> str:
    return f"{part}{repeat_str('x', 32 - len(part))}"


TOKEN_FOO = generate_kbase_token("foo")
TOKEN_BAR = generate_kbase_token("bar")
TOKEN_BAZ = generate_kbase_token("baz")


async def clear_storage_model():
    sm = storage_model()
    await sm.db.linking_sessions_completed.delete_many({})
    await sm.db.linking_sessions_initial.delete_many({})
    await sm.db.linking_sessions_started.delete_many({})
    await sm.db.links.delete_many({})


async def assert_create_linking_session(client: TestClient, authorization: str):
    #
    # Create linking session.
    #

    response = client.post(
        "/linking-sessions", headers={"Authorization": authorization}
    )

    #
    # Inspect the response for sensible answers.
    #
    assert response.status_code == 201
    session_info = response.json()
    assert isinstance(session_info["session_id"], str)
    return session_info


def assert_start_linking_session(
    client: TestClient,
    session_id: str,
    kbase_session: str | None = None,
    kbase_session_backup: str | None = None,
    return_link: str | None = None,
    skip_prompt: str | None = None,
):
    headers = {}
    if kbase_session is not None:
        headers["Cookie"] = f"kbase_session={kbase_session}"
    elif kbase_session_backup is not None:
        headers["Cookie"] = f"kbase_session_backup={kbase_session_backup}"

    params = {}
    if return_link is not None:
        params["return_link"] = return_link
    if skip_prompt is not None:
        params["skip_prompt"] = skip_prompt

    # TODO: should be put or post
    response = client.get(
        f"/linking-sessions/{session_id}/oauth/start",
        headers=headers,
        params=params,
        follow_redirects=False,
    )
    assert response.status_code == 302


def assert_continue_linking_session(
    client: TestClient,
    session_id: str,
    kbase_session: str | None = None,
    expected_response_code: int | None = None,
):
    # FINISH
    #
    # Get linking session again.
    #

    params = {
        "code": "foo",
        "state": json.dumps({"session_id": session_id}),
    }

    headers = {}
    if kbase_session is not None:
        headers["Cookie"] = f"kbase_session={kbase_session}"

    response = client.get(
        "/linking-sessions/oauth/continue",
        headers=headers,
        params=params,
        follow_redirects=False,
    )
    assert response.status_code == expected_response_code


def assert_finish_linking_session(
    client: TestClient,
    session_id: str,
    kbase_session: str | None = None,
    expected_response_code: int = 200,
):
    # FINISH
    #
    # Get linking session again.
    #
    headers = {}
    if kbase_session is not None:
        headers["authorization"] = kbase_session
    response = client.put(f"/linking-sessions/{session_id}/finish", headers=headers)
    assert response.status_code == expected_response_code


async def create_link(link_record: Any) -> None:
    sm = storage_model()
    await sm.db.links.drop()
    await sm.create_link_record(LinkRecord.model_validate(link_record))


async def update_link(link_record: Any) -> None:
    sm = storage_model()
    await sm.save_link_record(link_record)


async def get_link(username: str) -> LinkRecord | None:
    sm = storage_model()
    link_record = await sm.get_link_record(username)
    return link_record
