# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 helge
#
# SPDX-License-Identifier: MIT

import logging
import re

import aiohttp

from bovine.models import JrdData
from .utils import BOVINE_CLIENT_NAME

logger = logging.getLogger(__name__)


async def lookup_with_webfinger(
    session: aiohttp.ClientSession, webfinger_url: str, params: dict
):
    async with session.get(
        webfinger_url, params=params, headers={"user-agent": BOVINE_CLIENT_NAME}
    ) as response:
        if response.status != 200:
            logger.warning(f"{params['resource']} not found using webfinger")
            return None
        text = await response.text("utf-8")
        data = JrdData.model_validate_json(text)

        if data.links is None:
            return None

        for entry in data.links:
            if entry.rel == "self" and re.match(r"application/.*json", entry.type):
                return entry.href

    return None
