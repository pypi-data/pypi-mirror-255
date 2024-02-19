# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 helge
#
# SPDX-License-Identifier: MIT

from dataclasses import dataclass


@dataclass
class Link:
    """Represents an ActivityStreams link object"""

    id: str | None = None
    type: str = "Link"
    media_type: str | None = None
    href: str | None = None
    name: str | None = None
    rel: str | None = None

    @staticmethod
    def for_object(obj):
        """Allows to create Object links following
        `FEP-e232 <https://codeberg.org/fediverse/fep/src/branch/main/fep/e232/fep-e232.md>`_
        """
        return Link(
            media_type='application/ld+json; profile="https://www.w3.org/ns/activitystreams"',
            href=obj,
            name=f"RE: {obj}",
        )

    def build(self):
        """Transform class to dict"""
        result = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": self.type,
        }
        if self.media_type:
            result["mediaType"] = self.media_type
        if self.href:
            result["href"] = self.href
        if self.name:
            result["name"] = self.name
        if self.rel:
            result["rel"] = self.rel

        return result
