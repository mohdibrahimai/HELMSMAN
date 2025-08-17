"""Utility functions for aggregating contract results into metrics.

This module is not currently used by the reference orchestrator but is
provided as a starting point for future work. In a more complete
implementation the orchestrator would call into these functions to
compute pass rates and other summary statistics from the per‑item
contract results.
"""

from __future__ import annotations

from typing import Iterable, Dict, Any


def pass_rate(results: Iterable[bool]) -> float:
    """Compute the fraction of True values in an iterable."""
    total = 0
    passed = 0
    for r in results:
        total += 1
        if r:
            passed += 1
    return passed / total if total else 0.0


def combine_metrics(metrics: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    """Combine multiple metric dicts into a single summary.

    This naive implementation simply aggregates numeric values by
    averaging them. Non‑numeric values are ignored. Real systems would
    need more sophisticated logic depending on the metric semantics.
    """
    combined: Dict[str, Any] = {}
    counts: Dict[str, int] = {}
    for metric in metrics:
        for k, v in metric.items():
            if isinstance(v, (int, float)):
                combined[k] = combined.get(k, 0.0) + v
                counts[k] = counts.get(k, 0) + 1
    # Compute averages
    for k in combined:
        combined[k] /= counts[k]
    return combined