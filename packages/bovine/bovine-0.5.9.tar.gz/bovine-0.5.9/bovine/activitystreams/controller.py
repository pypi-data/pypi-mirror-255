# SPDX-FileCopyrightText: 2024 Helge
#
# SPDX-License-Identifier: MIT

from dataclasses import dataclass, field
from typing import List

from bovine.jsonld import use_context

from .multikey import Multikey


@dataclass
class Controller:
    """Experimental class to represent a controller document
    see [FEP-521a](https://codeberg.org/fediverse/fep/src/branch/main/fep/521a/fep-521a.md)
    """

    assertion_method: List[Multikey] = field(default_factory=list)
    authentication: List[Multikey] = field(default_factory=list)

    def build(self):
        if len(self.assertion_method) == 0:
            return {}

        result = {
            "@context": [
                "https://www.w3.org/ns/did/v1",
            ],
            "assertionMethod": [key.build() for key in self.assertion_method],
        }

        return use_context(
            result,
            [
                "https://www.w3.org/ns/did/v1",
                "https://w3id.org/security/multikey/v1",
            ],
        )
