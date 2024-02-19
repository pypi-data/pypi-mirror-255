# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 helge
#
# SPDX-License-Identifier: MIT

from . import WebPage


def test_determine_robots_url():
    page = WebPage(
        "https://www.allrecipes.com/recipe/263822/pasta-alla-norma-eggplant-pasta/"
    )

    assert page.robots_url == "https://www.allrecipes.com/robots.txt"


async def test_web_page():
    page = WebPage(
        "https://www.allrecipes.com/recipe/263822/pasta-alla-norma-eggplant-pasta/"
    )

    page.text = """
<html>
<head>
<script type="application/ld+json">{"@id": "https://jsonld.example"}</script>
</head>
</html>
"""

    jsonld = page.jsonld

    assert jsonld == [{"@id": "https://jsonld.example"}]


async def test_open_graph_page():
    page = WebPage("https://www.imdb.com/title/tt0117500/")
    page.text = """
<html prefix="og: https://ogp.me/ns#">
<head>
<title>The Rock (1996)</title>
<meta property="og:title" content="The Rock" />
<meta property="og:type" content="video.movie" />
<meta property="og:url" content="https://www.imdb.com/title/tt0117500/" />
<meta property="og:image" content="https://ia.media-imdb.com/images/rock.jpg" />
<meta property="og:description" 
  content="Sean Connery found fame and fortune as the suave, sophisticated British agent, James Bond." />
<meta property="og:image:type" content="image/jpeg" />
<meta property="og:image:width" content="400" />
<meta property="og:image:height" content="300" />
<meta property="og:image:alt" content="A shiny red apple with a bite taken out" />
</head>
</html>
"""

    result = page.open_graph_page

    assert result == {
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Page",
        "name": "The Rock",
        "summary": "Sean Connery found fame and fortune as the suave, sophisticated British agent, James Bond.",
        "url": "https://www.imdb.com/title/tt0117500/",
        "icon": {
            "type": "Image",
            "mediaType": "image/jpeg",
            "url": "https://ia.media-imdb.com/images/rock.jpg",
            "name": "A shiny red apple with a bite taken out",
            "height": 300,
            "width": 400,
        },
        "source": {
            "url": "https://www.imdb.com/title/tt0117500/",
            "mediaType": "text/html",
        },
    }
