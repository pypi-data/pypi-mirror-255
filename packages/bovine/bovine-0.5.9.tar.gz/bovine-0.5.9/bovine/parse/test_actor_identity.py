# SPDX-FileCopyrightText: 2024 helge
#
# SPDX-License-Identifier: MIT

import pytest

from bovine.crypto.test import public_key, public_key_multibase
from bovine.crypto.types import CryptographicIdentifier

from . import Actor

base_actor = {
    "@context": "about:bovine",
    "id": "https://local/actor",
    "inbox": "https://local/actor/inbox",
    "outbox": "https://local/actor/outbox",
    "preferredUsername": "alice",
}


@pytest.mark.parametrize(
    ["key_data", "key_ids"],
    [
        (
            {
                "publicKey": {
                    "id": base_actor["id"] + "#key",
                    "publicKeyPem": public_key,
                    "owner": base_actor["id"],
                }
            },
            {base_actor["id"] + "#key"},
        ),
        (
            {
                "publicKey": [
                    {
                        "id": base_actor["id"] + "#key",
                        "publicKeyPem": public_key,
                        "owner": base_actor["id"],
                    }
                ]
            },
            {base_actor["id"] + "#key"},
        ),
        (
            {
                "publicKey": [
                    {
                        "id": base_actor["id"] + "#one",
                        "publicKeyPem": public_key,
                        "owner": base_actor["id"],
                    },
                    {
                        "id": base_actor["id"] + "#two",
                        "publicKeyPem": public_key,
                        "owner": base_actor["id"],
                    },
                ]
            },
            {base_actor["id"] + "#one", base_actor["id"] + "#two"},
        ),
        (
            {
                "assertionMethod": [
                    {
                        "id": base_actor["id"] + "#one",
                        "type": "Multikey",
                        "controller": base_actor["id"],
                        "publicKeyMultibase": public_key_multibase,
                    }
                ]
            },
            {base_actor["id"] + "#one"},
        ),
        (
            {
                "assertionMethod": {
                    "id": base_actor["id"] + "#one",
                    "type": "Multikey",
                    "controller": base_actor["id"],
                    "publicKeyMultibase": public_key_multibase,
                }
            },
            {base_actor["id"] + "#one"},
        ),
        (
            {
                "authentication": {
                    "id": base_actor["id"] + "#one",
                    "type": "Multikey",
                    "controller": base_actor["id"],
                    "publicKeyMultibase": public_key_multibase,
                }
            },
            {base_actor["id"] + "#one"},
        ),
        (
            {
                "verificationMethod": {
                    "id": base_actor["id"] + "#one",
                    "type": "Multikey",
                    "controller": base_actor["id"],
                    "publicKeyMultibase": public_key_multibase,
                }
            },
            {base_actor["id"] + "#one"},
        ),
    ],
)
def test_valid_cryptographic_identifier(key_data, key_ids):
    actor = Actor({**base_actor, **key_data})

    identifiers = actor.cryptographic_identifiers

    assert len(identifiers) > 0

    assert all(isinstance(x, CryptographicIdentifier) for x in identifiers)
    assert all(x.controller == base_actor["id"] for x in identifiers)

    assert {x.id for x in identifiers} == key_ids


@pytest.mark.parametrize(
    ["key_data", "relationships"],
    [
        (
            {
                "assertionMethod": {
                    "id": base_actor["id"] + "#one",
                    "type": "Multikey",
                    "controller": base_actor["id"],
                    "publicKeyMultibase": public_key_multibase,
                }
            },
            {"assertionMethod"},
        ),
        (
            {
                "authentication": {
                    "id": base_actor["id"] + "#one",
                    "type": "Multikey",
                    "controller": base_actor["id"],
                    "publicKeyMultibase": public_key_multibase,
                }
            },
            {"authentication"},
        ),
        (
            {
                "verificationMethod": {
                    "id": base_actor["id"] + "#one",
                    "type": "Multikey",
                    "controller": base_actor["id"],
                    "publicKeyMultibase": public_key_multibase,
                }
            },
            set(),
        ),
    ],
)
def test_verification_relationships(key_data, relationships):
    actor = Actor({**base_actor, **key_data})

    identifiers = actor.cryptographic_identifiers

    assert len(identifiers) == 1
    assert identifiers[0].verification_relationships == relationships
