"""Simple run comparison tool for Helmsman.

This module provides a utility to compare two JSON Lines result files
produced by the orchestrator. For each contract it computes the pass
rate in both runs and reports the absolute difference. It can also
apply threshold gates defined in a YAML configuration file and
exit with a non‑zero status if any gate fails.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from typing import Dict, List, Tuple

import yaml


def _load_results(path: str) -> List[Dict]:
    results: List[Dict] = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            results.append(json.loads(line))
    return results


def _compute_pass_rates(results: List[Dict]) -> Dict[str, float]:
    """Compute pass rate per contract from a run.

    :returns: mapping from contract_id to pass_rate in [0, 1]
    """
    counts = defaultdict(int)
    passes = defaultdict(int)
    for item in results:
        for res in item.get('contract_results', []):
            cid = res['id']
            counts[cid] += 1
            if res['passed']:
                passes[cid] += 1
    rates = {cid: (passes[cid] / counts[cid]) if counts[cid] else 0.0 for cid in counts}
    return rates


def _apply_gates(deltas: Dict[str, float], gates: Dict[str, float]) -> Tuple[bool, Dict[str, float]]:
    """Evaluate whether the deltas satisfy gate thresholds.

    Each gate is expressed as a maximum allowed difference. Returns a
    tuple of (passed: bool, failed_gates: mapping of gate to actual
    value). Only gates present in the `gates` dict are evaluated.
    """
    passed = True
    failed = {}
    for k, threshold in gates.items():
        # find corresponding delta; if missing, skip
        val = deltas.get(k)
        if val is None:
            continue
        # For simplicity we treat all thresholds as maximum allowed
        if abs(val) > threshold:
            passed = False
            failed[k] = val
    return passed, failed


def compare_runs(a_path: str, b_path: str, gates_path: str | None = None) -> int:
    """Compare two result files and optionally enforce gates.

    :returns: exit code (0 if passes, non‑zero if fails gates)
    """
    a_results = _load_results(a_path)
    b_results = _load_results(b_path)
    a_rates = _compute_pass_rates(a_results)
    b_rates = _compute_pass_rates(b_results)
    # Compute deltas
    all_cids = set(a_rates.keys()) | set(b_rates.keys())
    deltas = {cid: b_rates.get(cid, 0.0) - a_rates.get(cid, 0.0) for cid in all_cids}
    # Print summary
    print("Contract pass rates (A vs B):")
    for cid in sorted(all_cids):
        print(f"  {cid}: {a_rates.get(cid, 0.0):.2f} -> {b_rates.get(cid, 0.0):.2f} (delta={deltas[cid]:+.2f})")
    exit_code = 0
    if gates_path:
        with open(gates_path, 'r', encoding='utf-8') as gf:
            gates_conf = yaml.safe_load(gf) or {}
        passed, failed = _apply_gates(deltas, gates_conf)
        if not passed:
            print("\nGate thresholds exceeded:")
            for g, v in failed.items():
                print(f"  {g}: delta {v:+.2f} (threshold {gates_conf[g]:.2f})")
            exit_code = 1
        else:
            print("\nAll gates passed.")
    return exit_code


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare two Helmsman run outputs.")
    parser.add_argument("--a", required=True, help="Path to first run JSONL file (baseline)")
    parser.add_argument("--b", required=True, help="Path to second run JSONL file")
    parser.add_argument("--gates", help="Optional YAML file specifying gate thresholds")
    args = parser.parse_args()
    exit_code = compare_runs(args.a, args.b, args.gates)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()