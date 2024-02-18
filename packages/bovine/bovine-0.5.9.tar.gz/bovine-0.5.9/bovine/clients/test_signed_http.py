# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 helge
#
# SPDX-License-Identifier: MIT

from unittest.mock import AsyncMock

import aiohttp

from bovine.crypto.test import private_key
from bovine.crypto.helper import content_digest_sha256_rfc_9530

from .signed_http import SignedHttpClient


async def test_activity_pub_client_get():
    session = AsyncMock(aiohttp.ClientSession)
    url = "https://test_domain/test_path"
    public_key_url = "public_key_url"
    session = AsyncMock(aiohttp.ClientSession)
    session.get = AsyncMock()

    client = SignedHttpClient(session, public_key_url, private_key)

    await client.get(url)

    session.get.assert_awaited_once()


async def test_activity_pub_client_post():
    session = AsyncMock(aiohttp.ClientSession)
    url = "https://test_domain/test_path"
    public_key_url = "public_key_url"
    session = AsyncMock(aiohttp.ClientSession)
    session.post = AsyncMock()

    client = SignedHttpClient(session, public_key_url, private_key)

    await client.post(url, "hello")

    session.post.assert_awaited_once()

    args = session.post.await_args_list[0]
    headers = args[1]["headers"]
    assert headers["digest"] == "sha-256=LPJNul+wow4m6DsqxbninhsWHlwfp0JecwQzYpOLmCQ="


async def test_activity_pub_client_post_rfc_9530():
    session = AsyncMock(aiohttp.ClientSession)
    url = "https://test_domain/test_path"
    public_key_url = "public_key_url"
    session = AsyncMock(aiohttp.ClientSession)
    session.post = AsyncMock()

    client = SignedHttpClient(
        session,
        public_key_url,
        private_key,
        digest_method=content_digest_sha256_rfc_9530,
    )

    await client.post(url, '{"cows": "good"}')

    session.post.assert_awaited_once()

    args = session.post.await_args_list[0]
    headers = args[1]["headers"]
    assert (
        headers["content-digest"]
        == "sha-256=:MILb5lUDD6Z0pDSxhgxj+hMBEw0uTzP3g2qUJGHMp9k=:"
    )
    assert headers["content-type"] == "application/activity+json"
