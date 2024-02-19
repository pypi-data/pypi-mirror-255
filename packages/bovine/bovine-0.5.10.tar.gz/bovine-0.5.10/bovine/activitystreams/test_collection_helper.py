# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 helge
#
# SPDX-License-Identifier: MIT

import pytest
from unittest.mock import AsyncMock
from bovine import BovineClient
from bovine.activitystreams import OrderedCollection
from .collection_helper import CollectionHelper


# See https://codeberg.org/bovine/bovine/issues/69
async def test_multiple_collection_iteration():
    collection_id = "https://bovine.example/collection"
    items = [collection_id + "/two", collection_id + "/three"]
    client = AsyncMock(BovineClient)
    client.proxy.return_value = OrderedCollection(collection_id, items=items).build()

    collection_helper = CollectionHelper(collection_id, client, resolve=False)

    result = [item async for item in collection_helper]

    assert result == items

    result = [item async for item in collection_helper]

    assert result == items


@pytest.mark.skip("requires instance requests")
async def test_collections():
    # remote = "https://metalhead.club/users/mariusor/following"
    # remote = "FIXME"
    remote = "https://mastodon.social/users/the_milkman/outbox"

    async with BovineClient.from_file("bovine_user.toml") as client:
        collection_helper = CollectionHelper(remote, client, resolve=False)

        async for item in collection_helper:
            print(item)
