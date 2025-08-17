"""Citation evaluation detectors and scoring functions.

This module implements simplified versions of claim detection and
citation quality checks. In the full HELMSMAN system these would
interface with advanced fact checking services (TruthLens) to assess
support, contradiction and coverage. Here we use naive heuristics to
determine whether a response contains factual claims and whether the
provided citations meet the minimum count and independence requirements.
"""

from __future__ import annotations

import re
from typing import Dict, List


def detect_claims(answer: str, args: Dict = None) -> bool:
    """Heuristic to decide if an answer contains factual claims.

    We consider an answer to contain claims if it includes any digits
    (suggesting numeric facts), capitalised proper nouns or is simply
    long enough. This is a very rough approximation and should be
    replaced with proper claim detection.
    """
    if not answer or not answer.strip():
        return False
    # Contains any digit
    if any(ch.isdigit() for ch in answer):
        return True
    # Contains a capitalised word longer than 3 letters (proper noun)
    tokens = re.findall(r"\b[A-Z][a-zA-Z]{3,}\b", answer)
    if tokens:
        return True
    # Length heuristic
    if len(answer) > 30:
        return True
    return False


def check_citation_quality(citations: List[str], args: Dict = None) -> bool:
    """Determine whether citations meet minimum count and independence.

    This simplified evaluator receives a list of citation identifiers and
    verifies that there are at least `min_citations` of them and, if
    required, that they are distinct. In a full implementation you
    would cross‑reference the citation URLs or domains to ensure true
    independence and use TruthLens to compute precision and coverage.

    :param citations: list of citation IDs returned by the answerer
    :param args: optional dict with keys `min_citations` and
        `require_independent_domains`
    :returns: True if the citations meet the thresholds, False otherwise
    """
    min_citations = args.get('min_citations', 2) if args else 2
    if len(citations) < min_citations:
        return False
    if args and args.get('require_independent_domains', False):
        # Here we treat distinct IDs as independent; real implementation
        # should map IDs to domains and ensure uniqueness
        if len(set(citations)) < len(citations):
            return False
    return True