# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 helge
#
# SPDX-License-Identifier: MIT

import logging
import json
import warnings
import http_sf
import hashlib

from urllib.parse import urlparse
from dataclasses import dataclass
from typing import Callable, Awaitable, Tuple
import bovine.utils
from bovine.utils import parse_gmt

from .helper import content_digest_sha256
from .http_signature import HttpSignature
from .signature import parse_signature_header
from .types import CryptographicIdentifier

logger = logging.getLogger(__name__)


@dataclass
class SignatureChecker:
    """Dataclass to encapsulate the logic of checking a HTTP signature

    :param key_retriever: used to resolve the keyId to the cryptographic information"""

    key_retriever: Callable[
        [str], Awaitable[Tuple[str | None, str | None] | CryptographicIdentifier | None]
    ]

    async def validate_signature(
        self,
        method: str,
        url: str,
        headers: dict,
        body: Callable[[], Awaitable[str | bytes]],
    ) -> str | None:
        """Valids a given signature

        :param method: The http method either get or post
        :param url: The url being queried
        :param headers: The request headers
        :param body: A coroutine resolving the the request body. Used for post requests to check the digest.
        """
        if "signature" not in headers:
            logger.debug("Signature not present on request for %s", url)
            logger.debug(json.dumps(dict(headers)))
            return None

        if method.lower() == "post":
            if not self.validate_digest(headers, await body()):
                logger.warning("Validating digest failed")
                return None

        try:
            http_signature = HttpSignature()
            parsed_signature = parse_signature_header(headers["signature"])
            signature_fields = parsed_signature.fields

            if (
                "(request-target)" not in signature_fields
                or "date" not in signature_fields
            ):
                logger.warning("Required field not present in signature")
                return None

            if method.lower() == "post" and all(
                field not in signature_fields for field in ["digest", "content-digest"]
            ):
                logger.warning("Digest not present, but computable")
                return None

            http_date = parse_gmt(headers["date"])
            if not bovine.utils.check_max_offset_now(http_date):
                logger.warning(f"Encountered invalid http date {headers['date']}")
                return None

            for field in signature_fields:
                if field == "(request-target)":
                    method = method.lower()
                    parsed_url = urlparse(url)
                    path = parsed_url.path
                    http_signature.with_field(field, f"{method} {path}")
                else:
                    http_signature.with_field(field, headers[field])

            key_result = await self.key_retriever(parsed_signature.key_id)

            if isinstance(key_result, tuple):
                warnings.warn(
                    "Returning a tuple from key_retriever is deprecated, return a CryptographicIdentifier instead, will be remove in bovine 0.6.0",
                    DeprecationWarning,
                )
                key_result = CryptographicIdentifier.from_pem(*key_result)

            if key_result is None:
                logger.debug(f"Could not retrieve key from {parsed_signature.key_id}")
                return None

            return http_signature.verify_with_identity(
                key_result, parsed_signature.signature
            )

        except Exception as e:
            logger.exception(str(e))
            logger.error(headers)
            return None

        return None

    async def validate_signature_request(self, request) -> str | None:
        """Validates a given signature

        :param request: The request object"""
        return await self.validate_signature(
            request.method, request.url, request.headers, request.get_data
        )

    def validate_digest(self, headers: dict, body: bytes) -> bool:
        """Validates the digest. First checks the `digest` header
        then the `content-digest` header.

        :param headers: The headers of the request
        :param body: The body of the request, currently a warning is raised if body is of type str
        :return: True if digest is present and valid
        """

        if isinstance(body, str):
            warnings.warn("Got body of type str expected bytes")
            body = body.encode("utf-8")

        if "digest" in headers:
            request_digest = headers["digest"]
            request_digest = request_digest[:4].lower() + request_digest[4:]
            digest = content_digest_sha256(body)
            if request_digest != digest:
                logger.warning("Different digest")
                return False

            return True

        if "content-digest" in headers:
            try:
                parsed = http_sf.parse(
                    headers["content-digest"].encode("utf-8"), tltype="dict"
                )
            except Exception as e:
                logger.warning(
                    "Failed to parse header %s with %s",
                    headers["content-digest"],
                    repr(e),
                )
                return False
            valid = False

            if "sha-256" in parsed:
                if parsed["sha-256"][0] == hashlib.sha256(body).digest():
                    valid = True
                else:
                    return False

            if "sha-512" in parsed:
                if parsed["sha-512"][0] == hashlib.sha512(body).digest():
                    valid = True
                else:
                    return False

            return valid

        return False
