# SPDX-FileCopyrightText: 2024 helge
#
# SPDX-License-Identifier: MIT

import pytest

from .helper import unknown_to_list, reduce_to_ids


@pytest.mark.parametrize(
    ("unknown", "expected"),
    [(None, []), ("test", ["test"]), (["a"], ["a"]), ({"a": "b"}, [{"a": "b"}])],
)
def test_unknown_to_list(unknown, expected):
    assert unknown_to_list(unknown) == expected


@pytest.mark.parametrize(
    ("input_list", "expected"), [([], []), (["a"], ["a"]), ([{"id": "A"}], ["A"])]
)
def test_reduce_to_ids(input_list, expected):
    assert reduce_to_ids(input_list) == expected
