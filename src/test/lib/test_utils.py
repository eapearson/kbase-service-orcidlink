import time

from orcidlink.lib import utils


def test_posix_time_millis():
    now = utils.posix_time_millis()
    assert isinstance(now, int)
    # a reasonable assumption is that the time returned is around
    # the same time as ... now.
    assert now - 1000 * time.time() < 1


def test_make_date():
    # just year
    assert utils.make_date(1234) == "1234"

    # year + month
    assert utils.make_date(1234, 56) == "1234/56"

    # year +  month + day
    assert utils.make_date(1234, 56, 78) == "1234/56/78"

    # nothing
    assert utils.make_date() == "** invalid date **"
