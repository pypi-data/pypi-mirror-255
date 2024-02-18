# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 helge
#
# SPDX-License-Identifier: MIT

import aiohttp

from . import fetch_nodeinfo


async def test_fetch_nodeinfo():
    async with aiohttp.ClientSession() as session:
        result = await fetch_nodeinfo(session, "mymath.rocks")

        assert result

        assert result["software"]["name"] == "bovine"
        assert "version" in result["software"]
