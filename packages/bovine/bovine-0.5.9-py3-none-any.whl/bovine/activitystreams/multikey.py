# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 helge
#
# SPDX-License-Identifier: MIT

from dataclasses import dataclass


@dataclass
class Multikey:
    """Represents a Multikey"""

    id: str
    controller: str
    multibase: str
    type: str = "Multikey"

    def build(self):
        return {
            "@context": "https://w3id.org/security/multikey/v1",
            "id": self.id,
            "type": self.type,
            "controller": self.controller,
            "publicKeyMultibase": self.multibase,
        }

    @staticmethod
    def from_multibase_and_controller(controller, multibase):
        return Multikey(
            id=f"{controller}#{multibase}", controller=controller, multibase=multibase
        )
