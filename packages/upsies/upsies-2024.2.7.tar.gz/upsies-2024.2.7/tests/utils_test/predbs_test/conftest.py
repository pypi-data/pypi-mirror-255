import asyncio
from unittest.mock import Mock

import pytest


# Platform independent fs.filename_sanitization() mocking fixture from
# tests/conftest.py
@pytest.fixture(scope='module', autouse=True)
def strict_filename_sanitization(strict_filename_sanitization):
    pass


@pytest.fixture(scope='module', autouse=True)
def disable_http_requests(pytestconfig, module_mocker):
    if not pytestconfig.getoption('--allow-requests', None):
        # We sleep for a small amount of time to allow cached resonses to be
        # read and returned before concurrently running requests raise the
        # RuntimeError. This is important for requests made in predbs.multi.
        async def raise_after_delay(*_, **__):
            await asyncio.sleep(1)
            raise RuntimeError('HTTP requests are disabled; use --allow-requests')

        # We can't patch utils.http._request() because we want it to return
        # cached requests. utils.http._request() only uses
        # httpx.AsyncClient.send() so we can patch that.
        module_mocker.patch('httpx.AsyncClient.send', Mock(side_effect=raise_after_delay))
