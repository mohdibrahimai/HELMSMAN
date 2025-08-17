"""Naive truth assessment for Helmsman.

In the full HELMSMAN vision, TruthLens inspects each factual claim in
the model's answer and checks whether the cited sources truly support
those claims. Implementing such a capability requires sophisticated
natural language understanding and retrieval of supporting context. To
keep this repository self‑contained and free of external dependencies,
the `TruthLens` class implemented here simply assumes that any answer
with at least one citation fully supports all claims, and marks
uncited answers as unverifiable.

The `evaluate` method returns a dictionary keyed by claim index with
values "supported" or "unverifiable". It does not attempt to
segment the answer into individual claims beyond splitting on
sentence boundaries.
"""

from __future__ import annotations

import re
from typing import Dict, List, Tuple


class TruthLens:
    def __init__(self) -> None:
        pass

    def analyse(self, answer: str) -> List[str]:
        """Break an answer into naive claims (sentences).

        Splits the answer on sentence terminators and returns a list of
        claim strings. This is a crude approximation and does not
        attempt to handle abbreviations or quotes.
        """
        sentences = re.split(r'(?<=[.?!])\s+', answer.strip())
        return [s for s in sentences if s]

    def evaluate(self, answer: str, citations: List[str]) -> Dict[int, str]:
        """Assess claims in the answer.

        Returns a mapping from claim index to one of "supported",
        "contradicted" or "unverifiable". This naive implementation
        labels all claims as "supported" if any citation is present,
        otherwise marks them "unverifiable".
        """
        claims = self.analyse(answer)
        label = "supported" if citations else "unverifiable"
        return {i: label for i in range(len(claims))}