# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 helge
#
# SPDX-License-Identifier: MIT


def validate_tos(tos: list | None):
    if tos is None:
        return True
    return all(validate_to(to) for to in tos)


def validate_to(to: str):
    if to.startswith("https://"):
        return True

    if "@" in to:
        return True

    return False
