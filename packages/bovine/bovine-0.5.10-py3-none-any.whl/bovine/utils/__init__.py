# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 helge
#
# SPDX-License-Identifier: MIT

from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple

from bs4 import BeautifulSoup

from bovine.models import JrdLink, JrdData

GMT_STRING = "%a, %d %b %Y %H:%M:%S GMT"


def pydantic_to_json(obj) -> dict:
    """Transforms a pydantic object from [bovine.models][bovine.models]
    into a dictionary, that can be serialized as json"""
    return obj.model_dump(mode="json", exclude_none=True)


def webfinger_response_json(account: str, url: str) -> dict:
    """helper to generate a webfinger response"""
    return pydantic_to_json(
        JrdData(
            subject=account,
            links=[JrdLink(href=url, rel="self", type="application/activity+json")],
        )
    )


def parse_fediverse_handle(account: str) -> Tuple[str, Optional[str]]:
    """Splits fediverse handle in name and domain Supported forms are:

    * user@domain -> (user, domain)
    * @user@domain -> (user, domain)
    * acct:user@domain -> (user, domain)
    """
    if account[0] == "@":
        account = account[1:]
    account = account.removeprefix("acct:")

    if "@" in account:
        user, domain = account.split("@", 1)
        return user, domain
    return account, None


def now_isoformat() -> str:
    """Returns now in Isoformat, e.g. "2023-05-31T18:11:35Z", to be used as the value
    of published"""
    return (
        datetime.now(tz=timezone.utc).replace(microsecond=0, tzinfo=None).isoformat()
        + "Z"
    )


def activity_pub_object_id_from_html_body(body: str) -> str | None:
    """Determines the object identifier from the html body
    by parsing it and looking for link tags with rel="alternate"
    and type application/activity+json"""

    soup = BeautifulSoup(body, features="lxml")
    element = soup.find(
        "link", attrs={"rel": "alternate", "type": "application/activity+json"}
    )
    if not element:
        return None

    return element.attrs.get("href")


def get_gmt_now() -> str:
    """Returns the current time in UTC as a GMT formatted string as used
    in the HTTP Date header"""
    return datetime.now(tz=timezone.utc).strftime(GMT_STRING)


def parse_gmt(date_string: str) -> datetime:
    """Parses a GMT formatted string as used in HTTP Date header"""
    return datetime.strptime(date_string, GMT_STRING).replace(tzinfo=timezone.utc)


def check_max_offset_now(dt: datetime, minutes: int = 5) -> bool:
    """Checks that offset of a datetime to now to be less than minutes"""

    now = datetime.now(tz=timezone.utc)

    if dt > now + timedelta(minutes=minutes):
        return False

    if dt < now - timedelta(minutes=minutes):
        return False

    return True
