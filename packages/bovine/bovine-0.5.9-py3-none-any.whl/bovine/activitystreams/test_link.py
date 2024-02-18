# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 helge
#
# SPDX-License-Identifier: MIT

from .link import Link


def test_object_link_fep_e232():
    link = Link.for_object("https://server.example/objects/123")

    assert link.build() == {
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Link",
        "mediaType": 'application/ld+json; profile="https://www.w3.org/ns/activitystreams"',
        "href": "https://server.example/objects/123",
        "name": "RE: https://server.example/objects/123",
    }
