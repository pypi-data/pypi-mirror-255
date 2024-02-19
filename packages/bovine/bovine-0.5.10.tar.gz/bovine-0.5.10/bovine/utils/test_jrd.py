# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 helge
#
# SPDX-License-Identifier: MIT

from . import JrdData, JrdLink, pydantic_to_json


def test_jrd_link():
    assert pydantic_to_json(JrdLink()) == {}
    assert pydantic_to_json(JrdLink(rel="rel", href="href", type="type")) == {
        x: x for x in ["rel", "href", "type"]
    }


def test_jrd_asdict():
    assert pydantic_to_json(JrdData()) == {}
    assert pydantic_to_json(JrdData(subject="acct:test")) == {"subject": "acct:test"}

    link = JrdLink(href="https://some.example/")

    assert pydantic_to_json(JrdData(links=[link])) == {
        "links": [{"href": "https://some.example/"}]
    }
