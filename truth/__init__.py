"""Truth checking utilities.

The truthlens_adapter module exposes a simple interface for assessing
whether claims in an answer are supported by the provided citations. In
a fully fledged system this would integrate with a fact verification
model or service. Here we implement a very naive heuristic: if the
answer includes at least one citation then all claims are marked as
supported. It is intended solely for demonstration purposes.
"""

from .truthlens_adapter import TruthLens

__all__ = ["TruthLens"]