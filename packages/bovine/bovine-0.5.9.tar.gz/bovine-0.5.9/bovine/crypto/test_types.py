# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 helge
#
# SPDX-License-Identifier: MIT

import pytest
from cryptography.hazmat.primitives.asymmetric import ed25519, rsa, ec

from .types import CryptographicIdentifier, CryptographicSecret
from .test import public_key, did_key, private_key, ed25519_key, ecp256_key


@pytest.mark.parametrize(
    "example",
    [
        {},
        {"type": "Key"},
        {"type": "Multikey"},
        {"type": "Multikey", "controller": "controller"},
        {"type": "Multikey", "publicKeyMultibase": "zxxx"},
        {"type": "Multikey", "controller": "controller", "publicKeyMultibase": "zxxx"},
        {
            "type": "Key",
            "controller": "controller",
            "publicKeyMultibase": did_key.removeprefix("did:key:"),
        },
    ],
)
def test_cryptographic_identity_from_multikey_error(example):
    with pytest.raises(ValueError):
        CryptographicIdentifier.from_multikey(example)


def test_cryptographic_identity_from_multikey():
    public_key_ed25519 = did_key.removeprefix("did:key:")
    controller = "https://com.example/issuer/123"
    multikey = {
        "id": f"{controller}#key-0",
        "type": "Multikey",
        "controller": controller,
        "publicKeyMultibase": public_key_ed25519,
    }

    identity = CryptographicIdentifier.from_multikey(multikey)

    assert identity.controller == controller

    signature = "0gHDz8Qn4+8gWC/byjTk7yvJxL0p4kiUSdxt6VZQvWQ9MBlRThMBDSrgJsNPHZWNMXtPSoL9+r0k\n3cUwYmIWDA=="

    assert identity.verify("moo", signature)
    assert identity.as_tuple() == (controller, public_key_ed25519)


def test_cryptographic_identity_from_multikey_rsa():
    controller = "https://com.example/issuer/123"
    public_key_rsa = "z4MXj1wBzi9jUstyQ1t9N9BHZpoQb4FQpaUfcc61XQigH9ua5R9aEN7YMK81PTKgWLGZXMqvy9eP4X42KgEsmNnZrwQbeT5R8oKhMHVQ5qcwTFwdX2gQeZLLDkUDJL3aJqmqSLK7mrgZ1CskMyD4p8eqFEUW1oufy9cE6Wyz7TQZFKpSCd1oY8HNue9cNRthZzXCdoX6DGVyewBFdivkohE1mhU1EpbKSYH66rx1cZpa6PJKzg4LbKSUqhHaftmsD1jWzFrKNUFzRmCGsihAjLVgsfjPaPmBUXNjYTFg1nCHWCGVGD3g9NhBwGiuu4vQR5PQfD6BCPZpGTaUZjWgZTHveef1pUDPvsCRuGDoGvrTnG8k7SeQp"
    multikey = {
        "id": f"{controller}#key-0",
        "type": "Multikey",
        "controller": controller,
        "publicKeyMultibase": public_key_rsa,
    }

    identity = CryptographicIdentifier.from_multikey(multikey)

    assert identity.controller == controller
    assert identity.as_tuple()[0] == controller

    identity_too = CryptographicIdentifier.from_tuple(*identity.as_tuple())

    assert identity.public_key == identity_too.public_key


@pytest.mark.parametrize(
    "example",
    [
        {},
        {"owner": "owner"},
        {"publicKeyPem": "xxxx"},
        {"owner": "owner", "publicKeyPem": "xxxx"},
    ],
)
def test_cryptographic_identity_from_public_key_error(example):
    with pytest.raises(ValueError):
        CryptographicIdentifier.from_public_key(example)


def test_cryptographic_identity_from_public_key():
    controller = "https://com.example/issuer/123"

    public_key_dict = {
        "id": f"{controller}/main-key",
        "owner": controller,
        "publicKeyPem": public_key,
    }

    identity = CryptographicIdentifier.from_public_key(public_key_dict)

    assert identity.controller == controller

    signature = "vaSYmwpEhGhB/o5QNC8MxYbJeBKDDiaZG0J4EsN0V/5+bFRgPbFK1oUgrdkiTT+farWXdVagPvIg44M/IYjPY8oExBS3mCt9oXDDWiDfBED8n2yrGHV6X/GWNxWUarmo4RcOBU2xWy9982/ZH+UyiPVEpanPi4REf9UYiF0dciZK1Yx3Nkqadnm9XTJJISHX4v88jkUGYaNnWcJ+SJMXuqklYJU/j8j4FVvf3vbFvuwGX1W5o7Zmk89xdJeRiGPYCM2zUgfzGoDHdVHuX8ksR+/xjzwLxMn/SerHuKSCzYivCpaxUqmX0VMTEwvPZ2H+hvXsqyLgR+zFnL7WdX6p7Q=="

    assert identity.verify("secret", signature)
    assert not identity.verify("secret", "")


@pytest.mark.parametrize(
    "example",
    ["", "zxxxxx", "did:key:zxdsafh"],
)
def test_cryptographic_identity_from_did_key_error(example):
    with pytest.raises(ValueError):
        CryptographicIdentifier.from_did_key(example)


# Some examples for this tests are from https://w3c-ccg.github.io/did-method-key
@pytest.mark.parametrize(
    ["did", "key_type"],
    [
        (
            "did:key:z6MknGc3ocHs3zdPiJbnaaqDi58NGb4pk1Sp9WxWufuXSdxf",
            ed25519.Ed25519PublicKey,
        ),
        (
            "did:key:z6MkiTBz1ymuepAQ4HEHYSF1H8quG5GLVVQR3djdX3mDooWp",
            ed25519.Ed25519PublicKey,
        ),
        (
            "did:key:z4MXj1wBzi9jUstyPMS4jQqB6KdJaiatPkAtVtGc6bQEQEEsKTic4G7Rou3iBf9vPmT5dbkm9qsZsuVNjq8HCuW1w24nhBFGkRE4cd2Uf2tfrB3N7h4mnyPp1BF3ZttHTYv3DLUPi1zMdkULiow3M1GfXkoC6DoxDUm1jmN6GBj22SjVsr6dxezRVQc7aj9TxE7JLbMH1wh5X3kA58H3DFW8rnYMakFGbca5CB2Jf6CnGQZmL7o5uJAdTwXfy2iiiyPxXEGerMhHwhjTA1mKYobyk2CpeEcmvynADfNZ5MBvcCS7m3XkFCMNUYBS9NQ3fze6vMSUPsNa6GVYmKx2x6JrdEjCk3qRMMmyjnjCMfR4pXbRMZa3i",
            rsa.RSAPublicKey,
        ),
        (
            "did:key:zDnaerDaTF5BXEavCrfRZEk316dpbLsfPDZ3WJ5hRTPFU2169",
            ec.EllipticCurvePublicKey,
        ),
        (
            "did:key:zDnaerx9CtbPJ1q36T5Ln5wYt3MQYeGRG5ehnPAmxcf5mDZpv",
            ec.EllipticCurvePublicKey,
        ),
        (
            "did:key:z82Lm1MpAkeJcix9K8TMiLd5NMAhnwkjjCBeWHXyu3U4oT2MVJJKXkcVBgjGhnLBn2Kaau9",
            ec.EllipticCurvePublicKey,
        ),
        (
            "did:key:z82LkvCwHNreneWpsgPEbV3gu1C6NFJEBg4srfJ5gdxEsMGRJUz2sG9FE42shbn2xkZJh54",
            ec.EllipticCurvePublicKey,
        ),
    ],
)
def test_cryptographic_identity_from_did_key(did, key_type):
    identifier = CryptographicIdentifier.from_did_key(did)

    assert identifier.controller == did
    assert isinstance(identifier.public_key, key_type)

    a, b = identifier.as_tuple()
    identifier = CryptographicIdentifier.from_tuple(a, b)

    assert identifier.controller == did
    assert isinstance(identifier.public_key, key_type)


def test_sign_document_fails_for_rsa():
    secret = CryptographicSecret.from_pem("http://localhost/key", private_key)

    with pytest.raises(ValueError):
        secret.sign_document({"@context": [], "https://boo.example": "value"})


@pytest.mark.parametrize(
    ["multibase", "use_rdfc", "cryptosuite"],
    [
        (ed25519_key, False, "eddsa-jcs-2022"),
        (ed25519_key, True, "eddsa-rdfc-2022"),
        (ecp256_key, False, "ecdsa-jcs-2019"),
        (ecp256_key, True, "ecdsa-rdfc-2019"),
    ],
)
def test_sign_document_has_correct_cryptosuite(multibase, use_rdfc, cryptosuite):
    secret = CryptographicSecret.from_multibase("http://localhost/key", multibase)

    signed = secret.sign_document(
        {"@context": [], "https://boo.example": "value"}, use_rdfc=use_rdfc
    )

    assert signed.get("proof").get("cryptosuite") == cryptosuite

    identifier = CryptographicIdentifier("controller", secret.private_key.public_key())

    assert identifier.verify_document(signed) == "controller"
