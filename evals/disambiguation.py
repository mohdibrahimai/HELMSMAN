"""Disambiguation contract detectors and evaluators.

This module defines simple heuristics for determining whether a query
is ambiguous and whether a clarifying question was asked before
answering. These heuristics are intentionally naïve and should be
replaced with more robust logic in a production system.
"""

from __future__ import annotations

from typing import List, Dict


# List of tokens that commonly indicate ambiguity (entity collisions)
AMBIGUOUS_ENTITIES = {
    "jordan",  # could be a country or a person
    "apple",  # fruit vs company
    "mercury",  # element vs planet
    "amazon",  # company vs river
    "washington",  # state vs city vs person
}

# Relative date terms that indicate ambiguous time references
RELATIVE_DATE_TERMS = {"last", "next", "this", "recent", "ago"}


def detect_ambiguity(query: str) -> bool:
    """Return True if the query contains ambiguous terms.

    This function checks for the presence of any token in
    `AMBIGUOUS_ENTITIES` or any relative date terms. It performs a
    case‑insensitive substring search. This is a simplistic heuristic
    intended for demonstration purposes.
    """
    lower = (query or "").lower()
    if not lower:
        return False
    for term in AMBIGUOUS_ENTITIES:
        if term in lower:
            return True
    for term in RELATIVE_DATE_TERMS:
        if term in lower:
            return True
    return False


def check_asked_then_answered(conversation: List[str], args: Dict) -> bool:
    """Return True if the assistant asked a clarifying question before answering.

    :param conversation: list of utterances; element 0 is user query,
        element 1 is assistant response. Real conversations may have
        more turns but this simplistic check only examines the first
        response.
    :param args: dictionary of arguments defined in the contract (e.g.
        list of interrogative phrases)
    :returns: True if the assistant response contains a question mark
        or interrogative words, False otherwise.
    """
    if not conversation or len(conversation) < 2:
        return False
    # Only examine the assistant's first response
    assistant_response = conversation[1].lower()
    interrogatives = args.get("clarify_interrogatives", [])
    # Check for question mark
    if "?" in assistant_response:
        return True
    # Check for interrogative phrases
    for phrase in interrogatives:
        if phrase.lower() in assistant_response:
            return True
    return False