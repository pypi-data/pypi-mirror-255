# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 helge
#
# SPDX-License-Identifier: MIT

import json
import logging
from typing import List

from pyld import jsonld

from bovine.utils.pyld_requests import requests_document_loader

from .cache import JsonLDCache

logger = logging.getLogger(__name__)


default_context = [
    "https://www.w3.org/ns/activitystreams",
    "https://w3id.org/security/v1",
    "https://www.w3.org/ns/did/v1",
    "https://w3id.org/security/multikey/v1",
    {
        "Hashtag": "as:Hashtag",
    },
]
"""Defines the context used to communicate with other Fediverse software"""


bovine_context = [
    "https://www.w3.org/ns/activitystreams",
    {
        "publicKey": {"@id": "https://w3id.org/security#publicKey", "@type": "@id"},
        "publicKeyPem": "https://w3id.org/security#publicKeyPem",
        "owner": {"@id": "https://w3id.org/security#owner", "@type": "@id"},
        "to": {"@id": "as:to", "@type": "@id", "@container": "@set"},
        "cc": {"@id": "as:cc", "@type": "@id", "@container": "@set"},
        "tag": {"@id": "as:tag", "@type": "@id", "@container": "@set"},
        "items": {"@id": "as:items", "@type": "@id", "@container": "@set"},
        "attachment": {"@id": "as:attachment", "@type": "@id", "@container": "@set"},
        "Hashtag": "as:Hashtag",
    },
    "https://www.w3.org/ns/did/v1",
    "https://w3id.org/security/multikey/v1",
]
""" Defines the context about:bovine used internally in the bovine stack"""

bovine_context_name = "about:bovine"
"""Defines the name of the bovine context"""

activitystreams_context = {
    "@vocab": "_:",
    "Accept": "as:Accept",
    "Activity": "as:Activity",
    "Add": "as:Add",
    "Announce": "as:Announce",
    "Application": "as:Application",
    "Arrive": "as:Arrive",
    "Article": "as:Article",
    "Audio": "as:Audio",
    "Block": "as:Block",
    "Collection": "as:Collection",
    "CollectionPage": "as:CollectionPage",
    "Create": "as:Create",
    "Delete": "as:Delete",
    "Dislike": "as:Dislike",
    "Document": "as:Document",
    "Event": "as:Event",
    "Flag": "as:Flag",
    "Follow": "as:Follow",
    "Group": "as:Group",
    "Ignore": "as:Ignore",
    "Image": "as:Image",
    "IntransitiveActivity": "as:IntransitiveActivity",
    "Invite": "as:Invite",
    "IsContact": "as:IsContact",
    "IsFollowedBy": "as:IsFollowedBy",
    "IsFollowing": "as:IsFollowing",
    "IsMember": "as:IsMember",
    "Join": "as:Join",
    "Leave": "as:Leave",
    "Like": "as:Like",
    "Link": "as:Link",
    "Listen": "as:Listen",
    "Mention": "as:Mention",
    "Move": "as:Move",
    "Note": "as:Note",
    "Object": "as:Object",
    "Offer": "as:Offer",
    "OrderedCollection": "as:OrderedCollection",
    "OrderedCollectionPage": "as:OrderedCollectionPage",
    "Organization": "as:Organization",
    "Page": "as:Page",
    "Person": "as:Person",
    "Place": "as:Place",
    "Profile": "as:Profile",
    "Public": {"@id": "as:Public", "@type": "@id"},
    "Question": "as:Question",
    "Read": "as:Read",
    "Reject": "as:Reject",
    "Relationship": "as:Relationship",
    "Remove": "as:Remove",
    "Service": "as:Service",
    "TentativeAccept": "as:TentativeAccept",
    "TentativeReject": "as:TentativeReject",
    "Tombstone": "as:Tombstone",
    "Travel": "as:Travel",
    "Undo": "as:Undo",
    "Update": "as:Update",
    "Video": "as:Video",
    "View": "as:View",
    "accuracy": {"@id": "as:accuracy", "@type": "xsd:float"},
    "actor": {"@id": "as:actor", "@type": "@id"},
    "alsoKnownAs": {"@id": "as:alsoKnownAs", "@type": "@id"},
    "altitude": {"@id": "as:altitude", "@type": "xsd:float"},
    "anyOf": {"@id": "as:anyOf", "@type": "@id"},
    "as": "https://www.w3.org/ns/activitystreams#",
    "attachment": {"@id": "as:attachment", "@type": "@id"},
    "attributedTo": {"@id": "as:attributedTo", "@type": "@id"},
    "audience": {"@id": "as:audience", "@type": "@id"},
    "bcc": {"@id": "as:bcc", "@type": "@id"},
    "bto": {"@id": "as:bto", "@type": "@id"},
    "cc": {"@id": "as:cc", "@type": "@id"},
    "closed": {"@id": "as:closed", "@type": "xsd:dateTime"},
    "content": "as:content",
    "contentMap": {"@container": "@language", "@id": "as:content"},
    "context": {"@id": "as:context", "@type": "@id"},
    "current": {"@id": "as:current", "@type": "@id"},
    "deleted": {"@id": "as:deleted", "@type": "xsd:dateTime"},
    "describes": {"@id": "as:describes", "@type": "@id"},
    "duration": {"@id": "as:duration", "@type": "xsd:duration"},
    "endTime": {"@id": "as:endTime", "@type": "xsd:dateTime"},
    "endpoints": {"@id": "as:endpoints", "@type": "@id"},
    "first": {"@id": "as:first", "@type": "@id"},
    "followers": {"@id": "as:followers", "@type": "@id"},
    "following": {"@id": "as:following", "@type": "@id"},
    "formerType": {"@id": "as:formerType", "@type": "@id"},
    "generator": {"@id": "as:generator", "@type": "@id"},
    "height": {"@id": "as:height", "@type": "xsd:nonNegativeInteger"},
    "href": {"@id": "as:href", "@type": "@id"},
    "hreflang": "as:hreflang",
    "icon": {"@id": "as:icon", "@type": "@id"},
    "id": "@id",
    "image": {"@id": "as:image", "@type": "@id"},
    "inReplyTo": {"@id": "as:inReplyTo", "@type": "@id"},
    "inbox": {"@id": "ldp:inbox", "@type": "@id"},
    "instrument": {"@id": "as:instrument", "@type": "@id"},
    "items": {"@id": "as:items", "@type": "@id"},
    "last": {"@id": "as:last", "@type": "@id"},
    "latitude": {"@id": "as:latitude", "@type": "xsd:float"},
    "ldp": "http://www.w3.org/ns/ldp#",
    "liked": {"@id": "as:liked", "@type": "@id"},
    "likes": {"@id": "as:likes", "@type": "@id"},
    "location": {"@id": "as:location", "@type": "@id"},
    "longitude": {"@id": "as:longitude", "@type": "xsd:float"},
    "mediaType": "as:mediaType",
    "name": "as:name",
    "nameMap": {"@container": "@language", "@id": "as:name"},
    "next": {"@id": "as:next", "@type": "@id"},
    "oauthAuthorizationEndpoint": {
        "@id": "as:oauthAuthorizationEndpoint",
        "@type": "@id",
    },
    "oauthTokenEndpoint": {"@id": "as:oauthTokenEndpoint", "@type": "@id"},
    "object": {"@id": "as:object", "@type": "@id"},
    "oneOf": {"@id": "as:oneOf", "@type": "@id"},
    "orderedItems": {"@container": "@list", "@id": "as:items", "@type": "@id"},
    "origin": {"@id": "as:origin", "@type": "@id"},
    "outbox": {"@id": "as:outbox", "@type": "@id"},
    "partOf": {"@id": "as:partOf", "@type": "@id"},
    "preferredUsername": "as:preferredUsername",
    "prev": {"@id": "as:prev", "@type": "@id"},
    "preview": {"@id": "as:preview", "@type": "@id"},
    "provideClientKey": {"@id": "as:provideClientKey", "@type": "@id"},
    "proxyUrl": {"@id": "as:proxyUrl", "@type": "@id"},
    "published": {"@id": "as:published", "@type": "xsd:dateTime"},
    "radius": {"@id": "as:radius", "@type": "xsd:float"},
    "rel": "as:rel",
    "relationship": {"@id": "as:relationship", "@type": "@id"},
    "replies": {"@id": "as:replies", "@type": "@id"},
    "result": {"@id": "as:result", "@type": "@id"},
    "sharedInbox": {"@id": "as:sharedInbox", "@type": "@id"},
    "shares": {"@id": "as:shares", "@type": "@id"},
    "signClientKey": {"@id": "as:signClientKey", "@type": "@id"},
    "source": "as:source",
    "startIndex": {"@id": "as:startIndex", "@type": "xsd:nonNegativeInteger"},
    "startTime": {"@id": "as:startTime", "@type": "xsd:dateTime"},
    "streams": {"@id": "as:streams", "@type": "@id"},
    "subject": {"@id": "as:subject", "@type": "@id"},
    "summary": "as:summary",
    "summaryMap": {"@container": "@language", "@id": "as:summary"},
    "tag": {"@id": "as:tag", "@type": "@id"},
    "target": {"@id": "as:target", "@type": "@id"},
    "to": {"@id": "as:to", "@type": "@id"},
    "totalItems": {"@id": "as:totalItems", "@type": "xsd:nonNegativeInteger"},
    "type": "@type",
    "units": "as:units",
    "updated": {"@id": "as:updated", "@type": "xsd:dateTime"},
    "uploadMedia": {"@id": "as:uploadMedia", "@type": "@id"},
    "url": {"@id": "as:url", "@type": "@id"},
    "vcard": "http://www.w3.org/2006/vcard/ns#",
    "width": {"@id": "as:width", "@type": "xsd:nonNegativeInteger"},
    "xsd": "http://www.w3.org/2001/XMLSchema#",
}

litepub_context = [
    "https://www.w3.org/ns/activitystreams",
    "https://w3id.org/security/v1",
    {
        "Emoji": "toot:Emoji",
        "Hashtag": "as:Hashtag",
        "PropertyValue": "schema:PropertyValue",
        "atomUri": "ostatus:atomUri",
        "conversation": {"@id": "ostatus:conversation", "@type": "@id"},
        "discoverable": "toot:discoverable",
        "manuallyApprovesFollowers": "as:manuallyApprovesFollowers",
        "capabilities": "litepub:capabilities",
        "ostatus": "http://ostatus.org#",
        "schema": "http://schema.org#",
        "toot": "http://joinmastodon.org/ns#",
        "value": "schema:value",
        "sensitive": "as:sensitive",
        "litepub": "http://litepub.social/ns#",
        "invisible": "litepub:invisible",
        "directMessage": "litepub:directMessage",
        "listMessage": {"@id": "litepub:listMessage", "@type": "@id"},
        "oauthRegistrationEndpoint": {
            "@id": "litepub:oauthRegistrationEndpoint",
            "@type": "@id",
        },
        "EmojiReact": "litepub:EmojiReact",
        "ChatMessage": "litepub:ChatMessage",
        "alsoKnownAs": {"@id": "as:alsoKnownAs", "@type": "@id"},
    },
]


def wrapper(url, options, **kwargs):
    if url == bovine_context_name:
        return {
            "contentType": "application/ld+json",
            "contextUrl": None,
            "documentUrl": url,
            "document": {"@context": bovine_context},
        }
    elif url == "https://www.w3.org/ns/activitystreams":
        return {
            "contentType": "application/ld+json",
            "contextUrl": None,
            "documentUrl": url,
            "document": {"@context": activitystreams_context},
        }
    elif url.startswith("http://joinmastodon.org/ns"):
        # See https://github.com/go-fed/activity/issues/152 for why
        return {
            "contentType": "application/ld+json",
            "contextUrl": None,
            "documentUrl": url,
            "document": {"@context": []},
        }
    elif url == "http://schema.org":
        url = "https://schema.org/docs/jsonldcontext.jsonld"
    try:
        result = requests_document_loader(timeout=60)(url, options)
        return result
    except Exception as e:
        logger.warning("Failed to load %s with %s", url, repr(e))

        if url.endswith("litepub-0.1.jsonld"):
            return {
                "contentType": "application/ld+json",
                "contextUrl": None,
                "documentUrl": url,
                "document": {"@context": litepub_context},
            }

        return {
            "contentType": "application/ld+json",
            "contextUrl": None,
            "documentUrl": url,
            "document": {"@context": []},
        }


jsonld_cache = JsonLDCache()
"""Stores the cached contexts"""


def wrapper_with_context(url, options, **kwargs):
    context = jsonld_cache.retrieve(url)
    if context is not None:
        return {
            "contentType": "application/ld+json",
            "contextUrl": None,
            "documentUrl": url,
            "document": {"@context": context},
        }
    result = wrapper(url, options, **kwargs)
    jsonld_cache.add(url, result["document"]["@context"])

    return result


jsonld.set_document_loader(wrapper_with_context)


async def split_into_objects(input_data: dict) -> List[dict]:
    """Takes an object with an "id" property and separates
    out all the subobjects with an id"""

    if "@context" not in input_data:
        logger.warning("@context missing in %s", json.dumps(input_data))
        input_data["@context"] = default_context

    context = input_data["@context"]
    flattened = jsonld.flatten(input_data)
    compacted = jsonld.compact(flattened, context)

    if "@graph" not in compacted:
        return [compacted]

    local, remote = split_remote_local(compacted["@graph"])

    return [frame_object(obj, local, context) for obj in remote]


def frame_object(obj: dict, local: List[dict], context) -> dict:
    to_frame = {"@context": context, "@graph": [obj] + local}
    frame = {"@context": context, "id": obj["id"]}
    return jsonld.frame(to_frame, frame)


def split_remote_local(graph):
    local = [x for x in graph if x["id"].startswith("_")]
    remote = [x for x in graph if not x["id"].startswith("_")]

    return local, remote


def combine_items(data: dict, items: List[dict]) -> dict:
    """Takes data and replaces ids by the corresponding objects from items"""
    return frame_object(data, items, data["@context"])


def with_bovine_context(data: dict) -> dict:
    """Returns the object with the about:bovine context"""
    return use_context(data, "about:bovine")


def with_external_context(data: dict) -> dict:
    """Returns the object with the default external context"""
    return use_context(data, default_context)


def with_activitystreams_context(data: dict) -> dict:
    """Returns the object with the ActivityStreams context"""
    return use_context(data, "https://www.w3.org/ns/activitystreams")


def use_context(data, context):
    return jsonld.compact(data, context)


def value_from_object(data, key):
    result = data.get(key)
    if result is None:
        return result
    if isinstance(result, str):
        return result
    return result["@value"]
