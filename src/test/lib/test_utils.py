import time

import pytest
from orcidlink.lib import utils


def test_current_time_millis():
    now = utils.current_time_millis()
    assert isinstance(now, int)
    # a reasonable assumption is that the time returned is around
    # the same time as ... now.
    assert now - 1000 * time.time() < 1


def test_get_kbase_config():
    config = utils.get_kbase_config()
    assert config is not None
    assert config.get('module-name') == 'ORCIDLink'
    assert config.get('service-language') == 'python'
    assert isinstance(config.get("module-description"), str)
    assert isinstance(config.get("module-version"), str)
    assert config.get('service-config').get('dynamic-service') is True


def test_make_date():
    # just year
    assert utils.make_date(1234) == "1234"

    # year + month
    assert utils.make_date(1234, 56) == "1234/56"

    # year +  month + day
    assert utils.make_date(1234, 56, 78) == "1234/56/78"

    # nothing
    assert utils.make_date() == "** invalid date **"


def test_get_prop():
    # simple object
    simple_object_value = {
        "foo": "bar"
    }
    value, found = utils.get_prop(simple_object_value, ["foo"])
    assert found is True
    assert value == "bar"

    # simple array
    simple_array_value = ["bar"]
    value, found = utils.get_prop(simple_array_value, [0])
    assert found is True
    assert value == "bar"

    # mixed object and array
    mixed_value = {
        "foo": ["bar"]
    }
    value, found = utils.get_prop(mixed_value, ["foo", 0])
    assert found is True
    assert value == "bar"

    # default value
    value, found = utils.get_prop(simple_object_value, ["baz"])
    assert found is False
    assert value is None

    value, found = utils.get_prop(simple_array_value, [1])
    assert found is False
    assert value is None

    value, found = utils.get_prop(mixed_value, ["foo", 2])
    assert found is False
    assert value is None

    # here we use the wrong type for the path
    value, found = utils.get_prop(simple_object_value, [0])
    assert found is False
    assert value is None

    value, found = utils.get_prop(simple_array_value, ["foo"])
    assert found is False
    assert value is None

    value, found = utils.get_prop(mixed_value, ["foo", "bar"])
    assert found is False
    assert value is None


def test_get_string_prop():
    # simple object
    simple_object_value = {
        "foo": "bar"
    }
    assert utils.get_string_prop(simple_object_value, ["foo"]) == "bar"

    # simple array
    simple_array_value = ["bar"]
    assert utils.get_string_prop(simple_array_value, [0]) == "bar"

    # mixed object and array
    mixed_value = {
        "foo": ["bar"]
    }
    assert utils.get_string_prop(mixed_value, ["foo", 0]) == "bar"

    # default value
    assert utils.get_string_prop(simple_object_value, ["baz"], "fuzz") == "fuzz"
    assert utils.get_string_prop(simple_array_value, [1], "fuzz") == "fuzz"
    assert utils.get_string_prop(mixed_value, ["foo", 2], "fuzz") == "fuzz"

    # here we use the wrong type for the path
    assert utils.get_string_prop(simple_object_value, [0], "fuzz") == "fuzz"
    assert utils.get_string_prop(simple_array_value, ["foo"], "fuzz") == "fuzz"
    assert utils.get_string_prop(mixed_value, ["foo", "bar"], "fuzz") == "fuzz"


def test_get_int_prop():
    # simple object
    def run_tests(test_value, expected_value, default_value, expected_default_value):
        simple_object_value = {
            "foo": test_value
        }
        assert utils.get_int_prop(simple_object_value, ["foo"]) == expected_value

        # simple array
        simple_array_value = [test_value]
        assert utils.get_int_prop(simple_array_value, [0]) == expected_value

        # mixed object and array
        mixed_value = {
            "foo": [test_value]
        }
        assert utils.get_int_prop(mixed_value, ["foo", 0]) == expected_value

        # default value
        assert utils.get_int_prop(simple_object_value, ["baz"], default_value) == expected_default_value
        assert utils.get_int_prop(simple_array_value, [1], default_value) == expected_default_value
        assert utils.get_int_prop(mixed_value, ["foo", 2], default_value) == expected_default_value

        # here we use the wrong type for the path
        assert utils.get_int_prop(simple_object_value, [0], default_value) == expected_default_value
        assert utils.get_int_prop(simple_array_value, ["foo"], default_value) == expected_default_value
        assert utils.get_int_prop(mixed_value, ["foo", "bar"], default_value) == expected_default_value

    run_tests(123, 123, 456, 456)
    run_tests("123", 123, 456, 456)
    run_tests(123, 123, "foo", "foo")

    with pytest.raises(ValueError):
        utils.get_int_prop({"foo": "bar"}, ["foo"])


def test_get_raw_prop():
    # simple object
    def run_tests(test_value, expected_value, default_value, expected_default_value):
        simple_object_value = {
            "foo": test_value
        }
        assert utils.get_raw_prop(simple_object_value, ["foo"]) == expected_value

        # simple array
        simple_array_value = [test_value]
        assert utils.get_raw_prop(simple_array_value, [0]) == expected_value

        # mixed object and array
        mixed_value = {
            "foo": [test_value]
        }
        assert utils.get_raw_prop(mixed_value, ["foo", 0]) == expected_value

        # default value
        assert utils.get_raw_prop(simple_object_value, ["baz"], default_value) == expected_default_value
        assert utils.get_raw_prop(simple_array_value, [1], default_value) == expected_default_value
        assert utils.get_raw_prop(mixed_value, ["foo", 2], default_value) == expected_default_value

        # here we use the wrong type for the path
        assert utils.get_raw_prop(simple_object_value, [0], default_value) == expected_default_value
        assert utils.get_raw_prop(simple_array_value, ["foo"], default_value) == expected_default_value
        assert utils.get_raw_prop(mixed_value, ["foo", "bar"], default_value) == expected_default_value

    run_tests(123, 123, 456, 456)
    run_tests("123", "123", 456, 456)
    run_tests(123, 123, "foo", "foo")


def test_set_prop():
    value = {"foo": "fee"}
    utils.set_prop(value, ["foo"], "bar")
    assert value == {"foo": "bar"}

    # Array
    value = {"foo": "fee", "bar": ["baz"]}
    assert utils.get_string_prop(value, ["bar", 0]) == "baz"
    utils.set_prop(value, ["bar", 0], "boo")
    assert utils.get_string_prop(value, ["bar", 0]) == "boo"
    assert value == {"foo": "fee", "bar": ["boo"]}

    # Even deeper
    value = {"foo": "fee", "bar": ["baz", {"abc": "def"}]}
    assert utils.get_string_prop(value, ["bar", 1, "abc"]) == "def"
    utils.set_prop(value, ["bar", 1, "abc"], "xyz")
    assert utils.get_string_prop(value, ["bar", 1, "abc"]) == "xyz"
    assert value == {"foo": "fee", "bar": ["baz", {"abc": "xyz"}]}


def test_set_prop_errors():
    value = {"foo": "fee", "bar": ["baz", {"abc": "def"}]}

    with pytest.raises(ValueError, match="Cannot set prop; cannot get path element 'fix' in dict"):
        utils.set_prop(value, ["fix", "fax"], "x")

    with pytest.raises(ValueError, match="Cannot set prop; cannot get path element '2' in array"):
        utils.set_prop(value, ["bar", 2, "fax"], "x")

    with pytest.raises(ValueError, match="Cannot set prop; path element 'a' is not int for array"):
        utils.set_prop(value, ["bar", "a", "fax"], "x")

    with pytest.raises(ValueError, match="Cannot set prop; reached leaf too early"):
        utils.set_prop(value, ["foo", "a", "fax"], "x")

    with pytest.raises(ValueError, match="Cannot set prop; cannot get leaf element 'fix' in dict"):
        utils.set_prop(value, ["fix"], "x")

    with pytest.raises(ValueError, match="Cannot set prop; cannot get leaf element '2' in array"):
        utils.set_prop(value, ["bar", 2], "x")

    with pytest.raises(ValueError, match="Cannot set prop; leaf path element 'bee' is not int for array"):
        utils.set_prop(value, ["bar", "bee"], "x")

    with pytest.raises(ValueError, match="Cannot set prop; leaf is not a dict or list"):
        utils.set_prop(value, ["foo", "fee"], "x")
