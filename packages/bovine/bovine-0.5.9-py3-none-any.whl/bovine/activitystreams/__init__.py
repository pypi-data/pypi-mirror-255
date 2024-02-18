# SPDX-FileCopyrightText: 2023-2024 Helge
#
# SPDX-License-Identifier: MIT

from dataclasses import dataclass
from typing import Optional, Tuple

from bovine.types import Visibility

from .activity_factory import ActivityFactory
from .object_factory import ObjectFactory


def factories_for_actor_object(
    actor_profile: dict,
) -> Tuple[ActivityFactory, ObjectFactory]:
    """Builds activity and object factories from actor object

    :param actor_profile: The actor profile as a dictionary
    :return: Activity- and object factory
    """
    return ActivityFactory(actor_profile), ObjectFactory(
        actor_information=actor_profile
    )


@dataclass
class WithPublicKey:
    """Represents an object having a legacy public key specified under the `publicKey` key"""

    public_key: Optional[str] = None
    public_key_name: Optional[str] = None

    def build_public_key(self, id) -> dict | None:
        if self.public_key:
            return {
                "@context": "https://w3id.org/security/v1",
                "publicKey": {
                    "id": f"{id}#{self.public_key_name}",
                    "owner": id,
                    "publicKeyPem": self.public_key,
                },
            }
        return None


@dataclass
class Actor(WithPublicKey):
    """Actor class represents the basic ActivityStreams actor."""

    id: str | None = None
    type: str = "Person"
    name: Optional[str] = None
    preferred_username: Optional[str] = None
    inbox: Optional[str] = None
    outbox: Optional[str] = None
    followers: Optional[str] = None
    following: Optional[str] = None
    event_source: Optional[str] = None
    proxy_url: Optional[str] = None

    summary: Optional[str] = None
    icon: Optional[dict] = None
    url: Optional[str] = None

    def build(self, visibility=Visibility.PUBLIC):
        """Creates the json-ld representation of the actor."""
        result = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "id": self.id,
            "type": self.type,
            **self._build_endpoints(visibility=visibility),
        }
        public_key = self.build_public_key(self.id)

        if public_key:
            result["@context"] = [result["@context"], public_key["@context"]]
            result = {**public_key, **result}

        if self.preferred_username:
            result["preferredUsername"] = self.preferred_username

        if visibility == Visibility.WEB:
            return result

        if self.name:
            result["name"] = self.name
        elif self.preferred_username:
            result["name"] = self.preferred_username

        for key, value in {
            "summary": self.summary,
            "icon": self.icon,
            "url": self.url,
        }.items():
            if value is not None:
                result[key] = value

        return result

    def _build_endpoints(self, visibility):
        result = {}

        if visibility == Visibility.WEB:
            return result

        if self.inbox:
            result["inbox"] = self.inbox
        else:
            result["inbox"] = self.id

        if self.outbox:
            result["outbox"] = self.outbox
        else:
            result["outbox"] = self.id

        if visibility != Visibility.OWNER:
            return result

        endpoints = self._build_user_endpoints()
        if endpoints:
            result["endpoints"] = endpoints

        if self.followers:
            result["followers"] = self.followers
        if self.following:
            result["following"] = self.following

        return result

    def _build_user_endpoints(self):
        endpoints = {}
        if self.event_source:
            endpoints["eventSource"] = self.event_source
        if self.proxy_url:
            endpoints["proxyUrl"] = self.proxy_url
        return endpoints


@dataclass
class Collection:
    id: str
    items: list

    def build(self) -> dict:
        return {
            "@context": "https://www.w3.org/ns/activitystreams",
            "id": self.id,
            "items": self.items,
            "type": "Collection",
        }


@dataclass
class OrderedCollection:
    id: str
    items: list | None = None
    count: int = 0
    first: str | None = None
    last: str | None = None

    def build(self) -> dict:
        result = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "id": self.id,
            "totalItems": self.count,
            "type": "OrderedCollection",
        }

        if self.items:
            result["orderedItems"] = self.items

        if self.first:
            result["first"] = self.first

        if self.last:
            result["last"] = self.last

        return result


@dataclass
class OrderedCollectionPage:
    id: str
    items: list
    part_of: str
    next: str | None = None
    prev: str | None = None

    def build(self) -> dict:
        result = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "id": self.id,
            "partOf": self.part_of,
            "orderedItems": self.items,
            "type": "OrderedCollectionPage",
        }

        if self.next:
            result["next"] = self.next

        if self.prev:
            result["prev"] = self.prev

        return result
