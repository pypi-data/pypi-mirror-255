# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 helge
#
# SPDX-License-Identifier: MIT

import aiohttp
from typing import Callable, Tuple
import bovine.clients.signed_http_methods

from bovine.crypto.types import CryptographicSecret
from bovine.crypto.helper import content_digest_sha256


def legacy_digest_method(body):
    return "digest", content_digest_sha256(body)


class SignedHttpClient:
    """Client for using HTTP Signatures"""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        public_key_url: str,
        private_key: str,
        digest_method: Callable[[bytes], Tuple[str, str]] | None = None,
    ):
        """Creates the http client. By using [content_digest_sha256_rfc_9530][bovine.crypto.helper.content_digest_sha256_rfc_9530] one can send the Content Digest according to RFC 9530.

        :param session: The aiohttp.ClientSession
        :param public_key_url: Used as keyId when signing
        :param private_key: The pem encoded private key
        :param digest_method: Allow specifying the method used to compute the digest
        """
        self.session = session
        self.secret = CryptographicSecret.from_pem(public_key_url, private_key)

        if digest_method is None:
            digest_method = legacy_digest_method
        self.digest_method = digest_method

    async def get(self, url: str, headers: dict = {}) -> aiohttp.ClientResponse:
        """Retrieves url using a signed get request

        :param url: URL to get
        :param headers: extra headers"""
        return await bovine.clients.signed_http_methods.signed_get(
            self.session, self.secret, url, headers
        )

    async def post(
        self, url: str, body: str, headers: dict = {}, content_type: str = None
    ):
        """Posts to url using a signed post request

        :param url: URL to post to
        :param body: The post body
        :param headers: extra headers
        :param content_type: Content type of the message"""
        return await bovine.clients.signed_http_methods.signed_post(
            self.session,
            self.secret,
            url,
            body,
            headers=headers,
            digest_method=self.digest_method,
            content_type=content_type,
        )

    def event_source(self, url: str):
        """Opens an event source to url

        :param url: Url to query"""
        return bovine.clients.signed_http_methods.signed_event_source(
            self.session, self.secret, url
        )
