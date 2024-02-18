# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 helge
#
# SPDX-License-Identifier: MIT

import logging
import warnings
from cryptography.exceptions import InvalidSignature

from .helper import (
    did_key_to_public_key,
    sign_message,
    verify_signature,
)

from .multibase import (
    multibase_decode,
    multibase_58btc_encode,
    multibase_to_private_key,
)

from .types import CryptographicSecret, CryptographicIdentifier

logger = logging.getLogger(__name__)


def build_signature(host, method, target):
    return (
        HttpSignature()
        .with_field("(request-target)", f"{method} {target}")
        .with_field("host", host)
    )


class HttpSignature:
    """Helper class to build http signatures

    Usage: Add fields used for signature with `with_fields`. Then
    use `build_signature` or `verify` depending on use case.
    """

    def __init__(self):
        self.fields = []

    def build_signature(self, key_id: str, private_key: str):
        """Returns the signature string when signed with private_key"""

        warnings.warn(
            "Deprecated use sign_for_http_draft instead, will be remove in bovine 0.6.0",
            DeprecationWarning,
        )

        message = self.build_message()

        signature_string = sign_message(private_key, message)
        headers = " ".join(name for name, _ in self.fields)

        signature_parts = [
            f'keyId="{key_id}"',
            'algorithm="rsa-sha256"',
            f'headers="{headers}"',
            f'signature="{signature_string}"',
        ]

        return ",".join(signature_parts)

    def sign_for_http_draft(self, secret: CryptographicSecret):
        message = self.build_message()

        signature_string = secret.sign(message)
        headers = " ".join(name for name, _ in self.fields)

        signature_parts = [
            f'keyId="{secret.key_id}"',
            'algorithm="rsa-sha256"',
            f'headers="{headers}"',
            f'signature="{signature_string}"',
        ]

        return ",".join(signature_parts)

    def ed25519_sign(self, private_encoded):
        private_key = multibase_to_private_key(private_encoded)

        message = self.build_message()

        return multibase_58btc_encode(private_key.sign(message.encode("utf-8")))

    def ed25519_verify(self, did_key, signature):
        public_key = did_key_to_public_key(did_key)

        if signature[0] != "z":
            raise ValueError(f"Expected signature to start with a z, got: {signature}")

        signature = multibase_decode(signature)

        message = self.build_message().encode("utf-8")

        try:
            public_key.verify(signature, message)
        except InvalidSignature:
            return False

        return True

    def verify(self, public_key: str, signature: str):
        """Verifies signature"""
        warnings.warn(
            "Deprecated use verify_with_identity instead, will be remove in bovine 0.6.0",
            DeprecationWarning,
        )

        message = self.build_message()
        return verify_signature(public_key, message, signature)

    def verify_with_identity(self, identifier: CryptographicIdentifier, signature: str):
        return identifier.verify(self.build_message(), signature)

    def build_message(self):
        """Builds the message"""
        return "\n".join(f"{name}: {value}" for name, value in self.fields)

    def with_field(self, field_name, field_value):
        """Adds a field to be used when building a http signature"""
        self.fields.append((field_name, field_value))
        return self

    @property
    def headers(self):
        """Headers as specified when building http signature"""
        return {name: value for name, value in self.fields if name[0] != "("}
