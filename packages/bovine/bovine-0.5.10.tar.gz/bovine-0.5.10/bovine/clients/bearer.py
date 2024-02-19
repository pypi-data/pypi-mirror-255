# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 helge
#
# SPDX-License-Identifier: MIT

import aiohttp

from dataclasses import dataclass
from bovine.utils import get_gmt_now

from .event_source import EventSource
from .utils import BOVINE_CLIENT_NAME


@dataclass
class BearerAuthClient:
    """Client for using Bearer authentication.

    :param session: The session
    :param bearer_key: The bearer key used in the header `Authorization: Bearer ${bearer_key}`
    """

    session: aiohttp.ClientSession
    bearer_key: str

    async def get(self, url: str, headers: dict = {}):
        """GET of resource.  By default the accept header `application/json` is set. You can override this using `headers`.

        :param url: The target url
        :param headers: additional request headers.
        """
        request_headers = {
            "accept": "application/json",
            "data": get_gmt_now(),
            "user-agent": BOVINE_CLIENT_NAME,
            **headers,
            "authorization": f"Bearer {self.bearer_key}",
        }

        return await self.session.get(url, headers=request_headers)

    async def post(
        self,
        url: str,
        body: str,
        headers: dict = {},
        content_type: str = "application/activity+json",
    ):
        """POST to resource  By default the accept header `application/json` is set. You can override this using `headers`.

        :param url: The target url
        :param body: The request body
        :param headers: additional request headers.
        :param content_type: The content_type of the body
        """
        request_headers = {
            "accept": "application/json",
            "data": get_gmt_now(),
            "user-agent": BOVINE_CLIENT_NAME,
            "content-type": content_type,
            **headers,
            "authorization": f"Bearer {self.bearer_key}",
        }

        return await self.session.post(url, data=body, headers=request_headers)

    def event_source(self, url: str, headers: dict = {}) -> EventSource:
        """Returns an EventSource for the server sent events given by url. Accept header is `text/event-stream` by default

        :param url: The target url
        :param headers: additional request headers.
        """
        request_headers = {
            "accept": "text/event-stream",
            "data": get_gmt_now(),
            "user-agent": BOVINE_CLIENT_NAME,
            **headers,
            "authorization": f"Bearer {self.bearer_key}",
        }
        return EventSource(self.session, url, headers=request_headers)
