# SPDX-FileCopyrightText: 2024 helge
#
# SPDX-License-Identifier: MIT

import pytest

from .cache import JsonLDCache


@pytest.fixture
def cache():
    yield JsonLDCache(filename=":memory:")


def test_creation(cache):
    assert cache.retrieve("https://one.test/") is None


def test_add_element(cache):
    context = {"hello": "world"}

    cache.add("https://two.test/", context)

    assert cache.retrieve("https://one.test/") is None
    assert cache.retrieve("https://two.test/") == context


def test_load(tmp_path):
    filename = tmp_path / "cache.sqlite"
    cache = JsonLDCache(filename=filename)
    context = {"hello": "world"}
    cache.add("https://two.test/", context)

    loaded = JsonLDCache(filename=filename)
    assert loaded.retrieve("https://two.test/") == context
