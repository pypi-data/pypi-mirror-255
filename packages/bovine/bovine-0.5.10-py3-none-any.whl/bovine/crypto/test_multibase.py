# SPDX-FileCopyrightText: 2024 helge
#
# SPDX-License-Identifier: MIT

from .multibase import multibase_58btc_encode


def test_multibase_58btc_encode():
    message = "secret".encode("utf-8")
    result = multibase_58btc_encode(message)

    assert result == "zzTuS2beK"
