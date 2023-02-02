import json

import pytest
from orcidlink.lib import json_file


@pytest.fixture
def fake_fs(fs):
    fs.create_file("/kb/module/data/foo/bar.json", contents=json.dumps({"baz": "buzz"}))
    yield fs


@pytest.fixture
def bad_fake_fs1(fs):
    # fs.create_file("/kb/module/data/foo/bar.json", contents=json.dumps({"baz": "buzz"}))
    yield fs


def test_get_prop():
    # simple object
    simple_object_value = {"foo": "bar"}
    value, found = json_file.get_prop(simple_object_value, ["foo"])
    assert found is True
    assert value == "bar"

    # simple array
    simple_array_value = ["bar"]
    value, found = json_file.get_prop(simple_array_value, [0])
    assert found is True
    assert value == "bar"

    # mixed object and array
    mixed_value = {"foo": ["bar"]}
    value, found = json_file.get_prop(mixed_value, ["foo", 0])
    assert found is True
    assert value == "bar"

    # default value
    value, found = json_file.get_prop(simple_object_value, ["baz"])
    assert found is False
    assert value is None

    value, found = json_file.get_prop(simple_array_value, [1])
    assert found is False
    assert value is None

    value, found = json_file.get_prop(mixed_value, ["foo", 2])
    assert found is False
    assert value is None

    # here we use the wrong type for the path
    with pytest.raises(ValueError, match="Path element not str"):
        json_file.get_prop(simple_object_value, [0])

    with pytest.raises(ValueError, match="Path element not int"):
        json_file.get_prop(simple_array_value, ["foo"])

    with pytest.raises(ValueError, match="Path element not int"):
        json_file.get_prop(mixed_value, ["foo", "bar"])
