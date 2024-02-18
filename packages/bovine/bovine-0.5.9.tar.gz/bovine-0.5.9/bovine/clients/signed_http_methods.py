# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 helge
#
# SPDX-License-Identifier: MIT

import logging

import aiohttp
from typing import Callable, Tuple

from bovine.crypto.http_signature import build_signature
from bovine.crypto.types import CryptographicSecret
from bovine.utils import get_gmt_now

from .event_source import EventSource
from .utils import BOVINE_CLIENT_NAME, host_target_from_url

logger = logging.getLogger(__name__)


async def signed_get(
    session: aiohttp.ClientSession,
    secret: CryptographicSecret,
    url: str,
    headers: dict = {},
) -> aiohttp.ClientResponse:
    logger.debug(f"Signed get with {secret.key_id} on {url}")

    host, target = host_target_from_url(url)
    accept = "application/activity+json"
    date_header = get_gmt_now()

    signature_helper = (
        build_signature(host, "get", target)
        .with_field("date", date_header)
        .with_field("accept", accept)
    )

    signature_header = signature_helper.sign_for_http_draft(secret)

    headers = {
        "user-agent": BOVINE_CLIENT_NAME,
        **headers,
        **signature_helper.headers,
        "signature": signature_header,
    }

    return await session.get(url, headers=headers, allow_redirects=False)


def signed_event_source(
    session: aiohttp.ClientSession,
    secret: CryptographicSecret,
    url: str,
    headers: dict = {},
):
    logger.debug(f"Signed event source with {secret.key_id} on {url}")

    host, target = host_target_from_url(url)
    accept = "text/event-stream"
    date_header = get_gmt_now()

    signature_helper = (
        build_signature(host, "get", target)
        .with_field("date", date_header)
        .with_field("accept", accept)
    )

    signature_header = signature_helper.sign_for_http_draft(secret)

    headers = {
        "user-agent": BOVINE_CLIENT_NAME,
        **headers,
        **signature_helper.headers,
        "signature": signature_header,
    }
    return EventSource(session, url, headers=headers)


async def signed_post(
    session: aiohttp.ClientSession,
    secret: CryptographicSecret,
    url: str,
    body: str,
    digest_method: Callable[[bytes], Tuple[str, str]],
    headers: dict = {},
    content_type=None,
) -> aiohttp.ClientResponse:
    logger.debug(f"Signed post with {secret.key_id} on {url}")

    host, target = host_target_from_url(url)

    if content_type is None:
        content_type = "application/activity+json"
    date_header = get_gmt_now()

    digest_header, digest = digest_method(body.encode("utf-8"))

    signature_helper = (
        build_signature(host, "post", target)
        .with_field("date", date_header)
        .with_field(digest_header, digest)
        .with_field("content-type", content_type)
    )

    signature_header = signature_helper.sign_for_http_draft(secret)

    headers = {
        "user-agent": BOVINE_CLIENT_NAME,
        **headers,
        **signature_helper.headers,
        "signature": signature_header,
    }

    return await session.post(url, data=body, headers=headers)
