<!--
SPDX-FileCopyrightText: 2023-2024 Helge

SPDX-License-Identifier: MIT
-->

# Changes to Bovine

## bovine 0.5.9

- Support RFC 9530 by allowing the `digest_method` to be set in actor. Furthermore, one may replace `digest` with `content-digest` and bovine will still consider the requests valid.
- Embedded objects of type `DataIntegrity` can now have their own context [Issue 180](https://codeberg.org/bovine/bovine/issues/180)

## bovine 0.5.8

- Add containers
- Begin work on [Issue 151](https://codeberg.org/bovine/bovine/issues/151).

## bovine 0.5.7

- `bovine.parse.Actor.cryptographic_identiers` now also extracts Multikeys [Issue 112](https://codeberg.org/bovine/bovine/issues/112)
- Replace `request-cache` with own `bovine.jsonld.cache` [Issue 48](https://codeberg.org/bovine/bovine/issues/48)
- `JrdData` and `JrdLink` are now members of `bovine.models` and generated. [Issue 145](https://codeberg.org/bovine/bovine/issues/145)
- Better debug logging for `BovineActor.get` and `BovineActor.post`. [Issue 143](https://codeberg.org/bovine/bovine/issues/143)
- Finish all the stuff related to Verifiable Credentials [Issue 132](https://codeberg.org/bovine/bovine/issues/132)
- Add reuse headers [Issue 133](https://codeberg.org/bovine/bovine/issues/133)

## bovine 0.5.6

- Request headers can now be properly set in clients [Issue 136](https://codeberg.org/bovine/bovine/issues/136)

## bovine 0.5.5

- `bovine.utils.date` absorbed into `bovine.utils` and documented
- New method `CryptographicIdentifier.from_did_key`
- `object_factory.reply` now works if attributedTo is a dictionary, see [Pull Request 123](https://codeberg.org/bovine/bovine/pulls/123)

## bovine 0.5.4

- Add implementation for FEP-8b32, see [Issue 7](https://codeberg.org/bovine/bovine/issues/7)
- Add deprecation warnings for bovine 0.6.0
- Add `bovine.types.CryptographicSecret` and `bovine.types.CryptographicIdentifier` and start using them.

## bovine 0.5.3

- Begin implementing support for Multikey.
- Python 3.12 should now be supported.
- Add support for [FEP-e232](https://codeberg.org/fediverse/fep/src/branch/main/fep/e232/fep-e232.md), [Issue 91](https://codeberg.org/bovine/bovine/issues/91)

## Version 0.5.2

- Add ability to follow links to parse json-ld [Issue 80](https://codeberg.org/bovine/bovine/issues/80)
- replaces multiformats with based58 see [Issue 85](https://codeberg.org/bovine/bovine/issues/85)
- `parse_fediverse_handle` can now handles uris starting with `acct:`, [Issue 84](https://codeberg.org/bovine/bovine/issues/84)

## Version 0.5.1

- `BovineActor.get` returns a Tombstone for 404 and 410 errors
- `Object` now supports icon and mediaType
- Add `bovine.clients.web`
- Add `bovine.utils.JrdData` and `.JrdLink`

## Version 0.4.0

- Changed signatures of `BovineClient` and `BovineActor` to take keyword arguments
- Document internals of `bovine.crypto`
- Add `bovine.parse`
- `BovineClient.proxy_element` renamed to just `proxy`
- `activity_factory` now has a method to create `Undo` activities
- `activity_factory` now sets `to` to the actor of a follow request for `accept`, `reject`
- Make dev, test, doc dependencies optional
- Add `bovine.crypto.build_validate_http_signature_raw`

## Version 0.3.1

- BovineClient.inbox / outbox are no longer coroutines
- BovineActor improved getting of resources
- Environment flag `BUTCHER_ALLOW_HTTP` that enables usage of http for webfinger lookup in BovineClient creation

## Version 0.3.0

- Force "items" to a `@container` of type `@set` in the `about:bovine` context
- Repair to CollectionHelper. Add collection_helper to BovineClient.

## Version 0.2.6

- Signature of `webfinger_response_json` changed (__breaking__)
- Improve addressing of object and activities. Add `as_followers` method.
- ServerSentEvent.id is now a str (was int)
- Improved CollectionHelper to be able iterate over Collection and OrderedCollection type of ActivityStreams objects.

## Version 0.2.3

- Improved REPL functionality

## Version 0.2.2

- Add command `python -mbovine.repl`.

## Version 0.2.1

- Repair jsonld request resolver

## Version 0.2.0

- Support [fep-4adb](https://codeberg.org/fediverse/fep/src/branch/main/feps/fep-4adb.md)
- Add jsonld functionality

## Version 0.1.4

- Bugfix: ObjectFactor.actor_for_mention didn't proxy the requested actor_id.

## Version 0.1.3

- Tutorial on hashtag announce bot
- Implement fep-612d
- Make `validate_moo_auth_signature` also return the domain
- Document how to get the activity id from location header after send_to_outbox

## Version 0.1.2

- Add reject to activity_factory
- Add url property to Actor
- Add python -m bovine.msg and python -m bovine.ed25519_key features

## Version 0.1.1

- Improved tutorial

## Version 0.1.0

- 2023-04-13 Added bovine.crypto module with all crypto routines, previously in bovine. Added documentation, added test cases for http signatures
- 2023-04-11 Added attachment, width, height to Object
- 2023-04-10 Activities and Objects should no longer contain empty to, cc properties
- 2023-04-09 Include sphinx.ext.viewcode in documentation

## Version 0.0.13

- 2023-04-08: Add ability to create Mention based on actor uri
- 2023-04-08: Add documentation for bovine.activitystreams.utils
- 2023-04-02: EventSource no longer returns ServerSentEvent with empty data
