# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 helge
#
# SPDX-License-Identifier: MIT

from .multikey import Multikey


def test_multikey_from_multibase():
    multikey = Multikey(
        id="https://server.example/users/alice#ed25519-key",
        controller="https://server.example/users/alice",
        multibase="z6MkrJVnaZkeFzdQyMZu1cgjg7k1pZZ6pvBQ7XJPt4swbTQ2",
    )
    expected = {
        "@context": "https://w3id.org/security/multikey/v1",
        "id": "https://server.example/users/alice#ed25519-key",
        "type": "Multikey",
        "controller": "https://server.example/users/alice",
        "publicKeyMultibase": "z6MkrJVnaZkeFzdQyMZu1cgjg7k1pZZ6pvBQ7XJPt4swbTQ2",
    }

    assert multikey.build() == expected


def test_from_multibase_and_controller():
    multikey = Multikey.from_multibase_and_controller(
        "https://server.example/users/alice",
        "z6MkrJVnaZkeFzdQyMZu1cgjg7k1pZZ6pvBQ7XJPt4swbTQ2",
    )
    expected = {
        "@context": "https://w3id.org/security/multikey/v1",
        "id": "https://server.example/users/alice#z6MkrJVnaZkeFzdQyMZu1cgjg7k1pZZ6pvBQ7XJPt4swbTQ2",
        "type": "Multikey",
        "controller": "https://server.example/users/alice",
        "publicKeyMultibase": "z6MkrJVnaZkeFzdQyMZu1cgjg7k1pZZ6pvBQ7XJPt4swbTQ2",
    }

    assert multikey.build() == expected
