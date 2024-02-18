# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 helge
#
# SPDX-License-Identifier: MIT

from typing import Optional, Tuple, Callable, Awaitable

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, rsa

import bovine

from .helper import (
    content_digest_sha256,
    public_key_to_did_key,
    private_key_to_base58,
)
from .multibase import multibase_to_private_key
from .http_signature import HttpSignature
from .signature_checker import SignatureChecker
from .types import CryptographicIdentifier


def generate_ed25519_private_key() -> str:
    """Returns a multicodec/multibase encoded ed25519 private key"""
    private_key = ed25519.Ed25519PrivateKey.generate()

    return private_key_to_base58(private_key)


def private_key_to_did_key(private_key_str: str) -> str:
    """Computes public key in did key form of Ed25519 private key

    :param private_key_str: multibase/multicodec encoded Ed25519 private key

    :return: did:key"""

    private_key = multibase_to_private_key(private_key_str)

    return public_key_to_did_key(private_key.public_key())


def generate_rsa_public_private_key() -> Tuple[str, str]:
    """Generates a new pair of RSA public and private keys.

    :returns: pem encoded public and private key
    """

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    public_key = private_key.public_key()
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    return public_key_pem.decode("utf-8"), private_key_pem.decode("utf-8")


def build_validate_http_signature(
    key_retriever: Callable[
        [str], Awaitable[Tuple[str | None, str | None] | CryptographicIdentifier | None]
    ],
):
    """Creates a validate_signature function. validate_signature takes the request
    as parameter and returns the owner if the http signature is valid. If you do not wish to use [quart](https://quart.palletsprojects.com/en/latest/) (or a compatible framework), you should use [build_validate_http_signature_raw][bovine.crypto.build_validate_http_signature_raw].

    Example for the `key_retriever` argument.

    ```python
    from bovine.crypto.types import CryptographicIdentifier

    async def retrieve(key_id):
        async with aiohttp.ClientSession() as session:
            response = await session.get(key_id)
            data = await response.json()
            return CryptographicIdentifier.from_publickey(
                data.get("publicKey", data)
            )

    validator = build_validate_http_signature(retrieve)
    ```

    `validator` then accepts as argument a `werzeug.wrappers.Request` object.


    :param key_retriever:
        A coroutine that given a key id returns the corresponding
        CryptographicIdentifier or a tuple `public_key, owner`. Here
        `public_key` is assumed to be PEM encoded and owner is an URI. In the Fediverse
        use case, owner will be the actor id.

    :return: The coroutine [SignatureChecker.validate_signature_request][bovine.crypto.signature_checker.SignatureChecker.validate_signature_request]
    """

    signature_checker = SignatureChecker(key_retriever)
    return signature_checker.validate_signature_request


def build_validate_http_signature_raw(
    key_retriever: Callable[
        [str], Awaitable[Tuple[str | None, str | None] | CryptographicIdentifier | None]
    ],
):
    """Creates a validate_signature function. validate_signature takes
    `(method, url, headers, body)` as parameters and returns
    the owner if the http signature is valid.
    The rest of behavior is as `build_validate_http_signature`.

    :return: The coroutine [SignatureChecker.validate_signature][bovine.crypto.signature_checker.SignatureChecker.validate_signature]
    """

    signature_checker = SignatureChecker(key_retriever)
    return signature_checker.validate_signature


async def validate_moo_auth_signature(
    request, domain
) -> Tuple[Optional[str], Optional[str]]:
    """Validates the `Moo-Auth-1 <https://blog.mymath.rocks/2023-03-15/BIN1_Moo_Authentication_and_Authoriation>`_ signature of the request.
    Returns the did-key if the signature is valid.

    :param request:
        The request to validate the signature for.
    :param domain:
        The domain the request is made to.

    :returns:
        On success the did key and domain, on failure None, None
        When no domain is passed the did key and None is returned
    """  # noqa: E501
    didkey = request.headers["authorization"][11:]
    signature = request.headers["x-moo-signature"]

    dt = bovine.utils.parse_gmt(request.headers["date"])
    if domain != request.headers["host"]:
        raise ValueError("Invalid host name")
    if not bovine.utils.check_max_offset_now(dt):
        raise ValueError("Invalid date offset")

    if request.method.lower() == "get":
        http_signature = (
            HttpSignature()
            .with_field("(request-target)", "get " + request.path)
            .with_field("host", request.headers["host"])
            .with_field("date", request.headers["date"])
        )
    else:
        raw_data = await request.get_data()
        digest = content_digest_sha256(raw_data)
        if digest != request.headers["digest"]:
            return None, None
        http_signature = (
            HttpSignature()
            .with_field("(request-target)", "post " + request.path)
            .with_field("host", request.headers["host"])
            .with_field("date", request.headers["date"])
            .with_field("digest", request.headers["digest"])
        )

    if http_signature.ed25519_verify(didkey, signature):
        return didkey, None
    return None, None
