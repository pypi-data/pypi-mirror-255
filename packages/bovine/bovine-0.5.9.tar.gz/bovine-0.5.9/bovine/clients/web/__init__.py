# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 helge
#
# SPDX-License-Identifier: MIT

import aiohttp
import json

from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
from dataclasses import dataclass, field
from bs4 import BeautifulSoup
from functools import cached_property
from bovine.activitystreams.object_factory import Object
from bovine.clients.utils import BOVINE_CLIENT_NAME
from bovine.jsonld import with_activitystreams_context


def safe_json_loads(text: str) -> dict | None:
    try:
        return json.loads(text)
    except Exception:
        return None


class RobotFileDeniesAccess(Exception):
    """Used to indicate that robots.txt does not allow the user agent
    to access the url being queried"""

    pass


@dataclass
class WebPage:
    """Class to capture loading webpages and transforming their
    content in objects more usable in the Fediverse.

    :param url: URL of the webpage"""

    url: str
    text: str | None = None
    linked_ld: list = field(default_factory=list)

    async def fetch(
        self, session: aiohttp.ClientSession | None = None, fetch_linked_ld=False
    ):
        """Fetches the webpage and transform its content using
        BeautifulSoup"""
        if session is None:
            async with aiohttp.ClientSession() as session:
                await self._fetch_with_session(session, fetch_linked_ld=fetch_linked_ld)
        else:
            await self._fetch_with_session(session, fetch_linked_ld=fetch_linked_ld)

    async def _fetch_with_session(self, session, fetch_linked_ld):
        async with session.get(
            self.robots_url, headers={"user-agent": BOVINE_CLIENT_NAME}
        ) as response:
            robots = RobotFileParser()
            robots.parse((await response.text("utf-8")).split("\n"))

            if not robots.can_fetch(BOVINE_CLIENT_NAME, self.url):
                raise RobotFileDeniesAccess()
        async with session.get(
            self.url, headers={"accept": "text/html", "user-agent": BOVINE_CLIENT_NAME}
        ) as response:
            self.text = await response.text("utf-8")
            if fetch_linked_ld:
                links = response.links.getall("alternate")

                links = [
                    str(x["url"]) for x in links if x["type"] == "application/ld+json"
                ]
                for x in links:
                    async with session.get(
                        x,
                        headers={
                            "accept": "application/ld+json",
                            "user-agent": BOVINE_CLIENT_NAME,
                        },
                    ) as response:
                        self.linked_ld.append(await response.json())

    @cached_property
    def soup(self):
        return BeautifulSoup(self.text, features="lxml")

    @cached_property
    def jsonld(self) -> dict | list:
        """Usage for json-ld contained in a page

        ```python
        page = WebPage(
            "https://www.allrecipes.com/recipe/263822/pasta-alla-norma-eggplant-pasta/"
        )
        await page.fetch()
        print(page.jsonld[0][0])
        ```

        For json-ld contained in the link header

        ```python
        page = WebPage('https://www.wikidata.org/wiki/Q76')
        await page.fetch(fetch_linked_ld=True)
        print(page.jsonld[0][0])
        ```
        """
        raw = self.soup.find_all("script", attrs={"type": "application/ld+json"})

        raw = [safe_json_loads(tag.text) for tag in raw]

        return [x for x in raw if x] + self.linked_ld

    def meta_content_for_property(self, value: str) -> str | None:
        tag = self.soup.find("meta", attrs={"property": value})
        if tag:
            return tag.get("content")
        return None

    def meta_content_for_property_int(self, value: str) -> int | None:
        tag = self.soup.find("meta", attrs={"property": value})
        if tag:
            return int(tag.get("content"))
        return None

    @cached_property
    def open_graph_page(self) -> dict:
        """Creates an ActivityPub Page object from the Open Graph data"""
        image = Object(
            type="Image",
            url=self.meta_content_for_property("og:image"),
            name=self.meta_content_for_property("og:image:alt"),
            height=self.meta_content_for_property_int("og:image:height"),
            width=self.meta_content_for_property_int("og:image:width"),
            media_type=self.meta_content_for_property("og:image:type"),
        )
        page = Object(
            type="Page",
            name=self.meta_content_for_property("og:title"),
            url=self.meta_content_for_property("og:url"),
            summary=self.meta_content_for_property("og:description"),
            source={"url": self.url, "mediaType": "text/html"},
        )

        page.icon = image.build()

        return with_activitystreams_context(page.build())

    @cached_property
    def robots_url(self):
        parsed = urlparse(self.url)
        return f"{parsed.scheme}://{parsed.netloc}/robots.txt"
