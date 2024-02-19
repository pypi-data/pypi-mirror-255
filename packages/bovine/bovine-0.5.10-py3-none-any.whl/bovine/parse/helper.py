# SPDX-FileCopyrightText: 2024 helge
#
# SPDX-License-Identifier: MIT

from typing import List


def unknown_to_list(obj) -> list:
    match obj:
        case dict() | str():
            return [obj]
        case list():
            return obj
    return []


def reduce_to_ids(list_obj: List) -> List[str]:
    return [x if isinstance(x, str) else x.get("id") for x in list_obj]
