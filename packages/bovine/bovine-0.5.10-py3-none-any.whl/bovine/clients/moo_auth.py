# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 helge
#
# SPDX-License-Identifier: MIT

import aiohttp
from dataclasses import dataclass

from bovine.crypto.helper import content_digest_sha256
from bovine.crypto.http_signature import build_signature
from bovine.utils import get_gmt_now

from .event_source import EventSource
from .utils import BOVINE_CLIENT_NAME, host_target_from_url


@dataclass
class MooAuthClient:
    """Client for using Moo-Auth-1 authentication

    :param session: The session
    :param did_key: The did key, i.e. `did:key:z...`
    :param private_key: private key corresponding to did_key
    """

    session: aiohttp.ClientSession
    did_key: str
    private_key: str

    async def get(self, url: str, headers: dict = {}):
        """GET for resource

        :param url: url to query
        :param headers: Additional headers"""
        host, target = host_target_from_url(url)

        accept = "application/activity+json"
        date_header = get_gmt_now()

        signature_helper = build_signature(host, "get", target).with_field(
            "date", date_header
        )
        signature_header = signature_helper.ed25519_sign(self.private_key)

        headers = {
            "accept": accept,
            "user-agent": BOVINE_CLIENT_NAME,
            **headers,
            **signature_helper.headers,
            "authorization": f"Moo-Auth-1 {self.did_key}",
            "x-moo-signature": signature_header,
        }

        return await self.session.get(url, headers=headers)

    async def post(
        self,
        url: str,
        body: str,
        headers: dict = {},
        content_type: str = "application/activity+json",
    ):
        """POST to resource

        :param url: The target url
        :param body: The request body
        :param headers: additional request headers.
        :param content_type: The content_type of the body
        """
        host, target = host_target_from_url(url)
        accept = "application/activity+json"
        date_header = get_gmt_now()

        digest = content_digest_sha256(body)

        signature_helper = (
            build_signature(host, "post", target)
            .with_field("date", date_header)
            .with_field("digest", digest)
        )
        signature_header = signature_helper.ed25519_sign(self.private_key)

        headers = {
            "accept": accept,
            "content-type": content_type,
            "user-agent": BOVINE_CLIENT_NAME,
            **headers,
            **signature_helper.headers,
            "authorization": f"Moo-Auth-1 {self.did_key}",
            "x-moo-signature": signature_header,
        }

        return await self.session.post(url, data=body, headers=headers)

    def event_source(self, url: str, headers: dict = {}):
        """Returns an event source

        :param url: url of event source
        :param headers: additional headers"""
        host, target = host_target_from_url(url)
        date_header = get_gmt_now()
        accept = "text/event-stream"
        signature_helper = build_signature(host, "get", target).with_field(
            "date", date_header
        )
        signature_header = signature_helper.ed25519_sign(self.private_key)

        headers = {
            "accept": accept,
            "user-agent": BOVINE_CLIENT_NAME,
            **headers,
            **signature_helper.headers,
            "authorization": f"Moo-Auth-1 {self.did_key}",
            "x-moo-signature": signature_header,
        }

        return EventSource(self.session, url, headers=headers)
