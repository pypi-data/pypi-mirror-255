# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 helge
#
# SPDX-License-Identifier: MIT

import aiohttp
from unittest.mock import AsyncMock

from .bearer import BearerAuthClient


async def test_bearer_auth_get():
    session = AsyncMock(aiohttp.ClientSession)
    session.get = AsyncMock()
    client = BearerAuthClient(session=session, bearer_key="token")

    await client.get("https://somewhere.test/path")

    session.get.assert_awaited_once()

    args = session.get.await_args

    assert args[0][0] == "https://somewhere.test/path"
    assert args[1]["headers"]["accept"] == "application/json"


async def test_bearer_auth_get_request_text_html():
    session = AsyncMock(aiohttp.ClientSession)
    session.get = AsyncMock()
    client = BearerAuthClient(session=session, bearer_key="token")

    await client.get("https://somewhere.test/path", headers={"accept": "text/html"})

    session.get.assert_awaited_once()

    args = session.get.await_args

    assert args[0][0] == "https://somewhere.test/path"
    assert args[1]["headers"]["accept"] == "text/html"
