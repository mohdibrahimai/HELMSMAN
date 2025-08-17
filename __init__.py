"""
HELMSMAN package root.

This package provides tools for specifying, testing and evaluating prompt
behaviour for retrieval‑augmented generation (RAG) systems. It includes a
simple contract DSL, a tiny retrieval harness, evaluation utilities and
rudimentary orchestration logic to run packs of queries against a model.

The implementation in this repository is intentionally kept minimal and
educational rather than production grade. It demonstrates how to load
contracts written in YAML, apply them to a set of test cases and collect
basic metrics. Many of the more advanced features described in the project
proposal (e.g. behavioural fuzzing, token attribution, fancy CI gates and
multilingual support) are stubbed out with placeholders to make the code
easy to read and extend.

To run a simple evaluation on your own machine, invoke the orchestrator via

    python -m helmsman.orchestrator --contracts_dir=contracts/builtin \
        --packs=helmsman/packs/smoke_ambiguous_en.jsonl \
        --prompts=helmsman/prompts/v1.yaml \
        --out=run.jsonl

This will load the contracts, read the test pack and prompt template,
generate answers using a naive retrieval‑based answerer, apply the
contract checks and write a JSON Lines file with the results.

"""

__all__ = [
    "contracts",
    "core",
    "packs",
    "rag",
    "truth",
    "evals",
]