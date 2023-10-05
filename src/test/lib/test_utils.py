import contextlib
import time
from test.mocks.env import MOCK_KBASE_SERVICES_PORT
from test.mocks.mock_contexts import mock_auth_service, no_stderr

import pytest

from orcidlink.jsonrpc.errors import AuthorizationRequiredError
from orcidlink.jsonrpc.utils import ensure_authorization2
from orcidlink.lib import utils


@contextlib.contextmanager
def mock_services():
    with no_stderr():
        with mock_auth_service(MOCK_KBASE_SERVICES_PORT):
            yield


def test_posix_time_millis():
    now = utils.posix_time_millis()
    assert isinstance(now, int)
    # a reasonable assumption is that the time returned is around
    # the same time as ... now.
    assert now - 1000 * time.time() < 1


def test_posix_time_seconds():
    now = utils.posix_time_seconds()
    assert isinstance(now, int)
    # a reasonable assumption is that the time returned is around
    # the same time as ... now.
    assert now - time.time() < 1


def test_make_date():
    # just year
    assert utils.make_date(1234) == "1234"

    # year + month
    assert utils.make_date(1234, 56) == "1234/56"

    # year +  month + day
    assert utils.make_date(1234, 56, 78) == "1234/56/78"

    # nothing
    assert utils.make_date() == "** invalid date **"


# TODO: this just covers one case, the rest are covered via other tests, but
# it sure would be nice to directly test this.
async def test_ensure_authorization2_error_no_authorization():
    with mock_services():
        with pytest.raises(AuthorizationRequiredError):
            await ensure_authorization2(None)
