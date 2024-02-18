# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 helge
#
# SPDX-License-Identifier: MIT

import aiohttp

from bovine import BovineClient
from bovine.clients import lookup_account_with_webfinger
from bovine.utils import now_isoformat

from .validation import validate_tos


def validate(to, public):
    if not validate_tos(to):
        print("Invalid recipients")
        exit(1)

    if len(to) == 0 and not public:
        print("Specify at least one recipient")
        exit(1)


async def resolve(session: aiohttp.ClientSession, to: str) -> str | None:
    if "@" in to:
        return await lookup_account_with_webfinger(session, to)

    return to


async def process(secret, host, to, public, message):
    if host and secret:
        client = BovineClient(host=host, secret=secret)
    else:
        client = BovineClient.from_file("bovine_user.toml")

    async with client:
        recipients = [await resolve(client.session, to) for to in to]

        mentions = [
            await client.object_factory.mention_for_actor_uri(recipient)
            for recipient in recipients
        ]
        mentions = [m.build() for m in mentions]

        note = client.object_factory.note(
            to=set(recipients),
            tag=mentions,
            content=message,
            published=now_isoformat(),
        )

        if public:
            note = note.as_public()

        create = client.activity_factory.create(note.build()).build()

        await client.send_to_outbox(create)
