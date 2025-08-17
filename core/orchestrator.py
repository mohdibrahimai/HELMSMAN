"""Top‑level orchestration for running Helmsman evaluations.

This script ties together the contracts, retrieval harness, answer
generation and evaluation logic. It reads a set of test queries
("packs"), runs a model to produce answers, applies the contracts
and writes the results to a JSON Lines file. The JSONL output can be
post‑processed by the diff tool for comparisons between versions.

The design here is intentionally simple to serve as a reference
implementation. Real deployments would likely want to integrate a
production LLM, complex retrieval backends, streaming pipelines and
dashboards. This script aims to be runnable in a restricted
environment with no external network access.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..contracts import load_contracts
from ..contracts.schemas import Contract
from ..evals.disambiguation import detect_ambiguity, check_asked_then_answered
from ..evals.citation_precision import detect_claims, check_citation_quality
from ..rag.retrieve import Retriever
from ..rag.answer import Answerer
from ..truth.truthlens_adapter import TruthLens


def _load_pack(path: str) -> List[Dict[str, Any]]:
    """Read a JSON Lines test pack into a list of dicts."""
    items: List[Dict[str, Any]] = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            items.append(json.loads(line))
    return items


def _load_prompts(path: str) -> Dict[str, Any]:
    """Load prompt configuration from a YAML or JSON file.

    For the purposes of this reference implementation we only
    extract a single field `system_prompt` which is passed through to
    the answerer. Additional fields can be added to support more
    sophisticated prompt templating.
    """
    import yaml  # local import to avoid mandatory dependency
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError("Prompt file must contain a mapping")
    return data


def evaluate_contract(
    contract: Contract,
    query: str,
    answer: str,
    conversation: List[str],
    citations: List[str],
) -> Dict[str, Any]:
    """Evaluate a single contract on a query/answer pair.

    :returns: dict with `id`, `passed` and optional `message`
    """
    # Determine if contract applies based on precondition
    applies = True
    if contract.precondition:
        if contract.precondition == "query_is_ambiguous":
            applies = detect_ambiguity(query)
        elif contract.precondition == "contains_factual_claims":
            applies = detect_claims(answer)
        else:
            # Unknown precondition names default to True
            applies = True
    if not applies:
        return {
            "id": contract.id,
            "passed": True,
            "message": contract.messages.on_pass if contract.messages else None,
        }

    # Determine pass/fail based on pass_criteria
    result = True
    message: Optional[str] = None
    criteria = contract.metrics.pass_criteria if contract.metrics else None
    if criteria == "asked_then_answered":
        result = check_asked_then_answered(conversation, contract.detectors["asked_then_answered"].args if contract.detectors else {})
        if result:
            message = contract.messages.on_pass if contract.messages else None
        else:
            # choose appropriate message field
            # For this simple implementation we use a generic failure message
            message = contract.messages.on_fail_answered_directly if contract.messages else "Failed disambiguation contract"
    elif criteria == "precision_and_coverage":
        # Evaluate citation quality using the provided citations list
        args = (
            contract.detectors["precision_and_coverage"].args
            if contract.detectors and "precision_and_coverage" in contract.detectors
            else {}
        )
        result = check_citation_quality(citations, args)
        if result:
            message = contract.messages.on_pass if contract.messages else None
        else:
            message = (
                contract.messages.on_fail_precision
                if contract.messages and contract.messages.on_fail_precision
                else "Failed citations contract"
            )
    else:
        # Unknown criteria: pass by default
        result = True
        message = contract.messages.on_pass if contract.messages else None
    return {"id": contract.id, "passed": bool(result), "message": message}


def run_orchestration(
    contracts_dir: str,
    packs: str,
    prompts: str,
    model: str,
    out: str,
) -> None:
    """Run the evaluation pipeline and write results to JSONL file."""
    # Load contracts
    contracts = load_contracts(contracts_dir)
    if not contracts:
        print(f"No contracts found in {contracts_dir}", file=sys.stderr)
        return
    # Load test pack
    pack = _load_pack(packs)
    # Load prompts
    prompts_config = _load_prompts(prompts)
    system_prompt = prompts_config.get("system_prompt", "")
    prompt_version = prompts_config.get("version", "unknown")
    # Initialize retrieval and answerer
    retriever = Retriever()
    answerer = Answerer(system_prompt)
    truthlens = TruthLens()

    # Prepare output directory
    out_path = Path(out)
    out_dir = out_path.parent
    if out_dir and not out_dir.exists():
        out_dir.mkdir(parents=True, exist_ok=True)

    run_id = datetime.utcnow().isoformat()
    with open(out_path, 'w', encoding='utf-8') as f:
        for item in pack:
            query = item.get("input_query") or item.get("query") or ""
            locale = item.get("locale", "en")
            topic = item.get("topic", "general_qa")
            seed_id = item.get("id", "")
            # Generate answer and citations
            retrieved_docs = retriever.retrieve(query)
            answer, citations = answerer.answer(query, retrieved_docs)
            # Evaluate truth and citation quality (stubbed)
            # In this simple implementation we do not compute claim labels
            # Evaluate contracts
            conversation = [query, answer]
            contract_results = []
            for contract in contracts.values():
                # Check if the contract applies based on topic and locale
                if topic in contract.applies_to and locale in contract.locales:
                    res = evaluate_contract(contract, query, answer, conversation, citations)
                    contract_results.append(res)
            result_item = {
                "run_id": run_id,
                "model_version": model,
                "prompt_version": prompt_version,
                "locale": locale,
                "topic": topic,
                "seed_id": seed_id,
                "input_query": query,
                "retrieved_snippets": retrieved_docs,
                "answer": answer,
                "citations": citations,
                "contract_results": contract_results,
            }
            f.write(json.dumps(result_item) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Helmsman orchestration.")
    parser.add_argument("--contracts_dir", required=True, help="Directory containing contract YAML files")
    parser.add_argument("--packs", required=True, help="Path to JSONL test pack")
    parser.add_argument("--prompts", required=True, help="Path to prompt template (YAML/JSON)")
    parser.add_argument("--model", default="local", help="Model name/version to record in outputs")
    parser.add_argument("--out", required=True, help="Path to output JSONL file")
    args = parser.parse_args()
    run_orchestration(
        contracts_dir=args.contracts_dir,
        packs=args.packs,
        prompts=args.prompts,
        model=args.model,
        out=args.out,
    )


if __name__ == "__main__":
    main()