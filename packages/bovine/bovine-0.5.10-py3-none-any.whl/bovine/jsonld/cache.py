# SPDX-FileCopyrightText: 2024 helge
#
# SPDX-License-Identifier: MIT

import json
import sqlite3
import logging

logger = logging.getLogger(__name__)


class JsonLDCache:
    def __init__(self, filename="bovine_jsonld_cache.sqlite"):
        self.filename = filename

        self.connection = sqlite3.connect(filename)

        cursor = self.connection.execute(
            """CREATE TABLE IF NOT EXISTS jsonld (
            url TEXT PRIMARY KEY,
            context TEXT
        )"""
        )

        cursor.execute("SELECT url, context FROM jsonld")
        items = cursor.fetchall()

        self.cache = {x[0]: json.loads(x[1]) for x in items}

        cursor.close()
        self.connection.commit()

    def retrieve(self, url):
        return self.cache.get(url)

    def add(self, url, context):
        self.cache[url] = context

        cursor = self.connection.executemany(
            "INSERT INTO jsonld VALUES (?, ?)", [(url, json.dumps(context))]
        )
        cursor.close()
        self.connection.commit()
