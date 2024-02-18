# SPDX-FileCopyrightText: 2024 Helge
#
# SPDX-License-Identifier: MIT

from .controller import Controller
from .multikey import Multikey


def test_empty_controller():
    controller = Controller()

    assert controller.build() == {}


def test_with_multikey():
    multikey = Multikey(
        id="https://server.example/users/alice#ed25519-key",
        controller="https://server.example/users/alice",
        multibase="z6MkrJVnaZkeFzdQyMZu1cgjg7k1pZZ6pvBQ7XJPt4swbTQ2",
    )

    controller = Controller(assertion_method=[multikey])

    result = controller.build()

    assert result["@context"] == [
        "https://www.w3.org/ns/did/v1",
        "https://w3id.org/security/multikey/v1",
    ]

    assert len(result["assertionMethod"]) == 1

    key = result["assertionMethod"][0]
    assert (
        key["publicKeyMultibase"] == "z6MkrJVnaZkeFzdQyMZu1cgjg7k1pZZ6pvBQ7XJPt4swbTQ2"
    )
    assert "@context" not in key
