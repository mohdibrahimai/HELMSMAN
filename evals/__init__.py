"""Evaluation functions for contracts.

This package exposes detector and evaluator functions used by the
contracts. Each module corresponds to a particular contract or group of
related contracts.
"""

from .disambiguation import detect_ambiguity, check_asked_then_answered
from .citation_precision import detect_claims, check_citation_quality

__all__ = [
    "detect_ambiguity",
    "check_asked_then_answered",
    "detect_claims",
    "check_citation_quality",
]