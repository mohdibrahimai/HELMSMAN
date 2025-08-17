"""Contract loading and validation.

Contracts define behavioural expectations for how a model should respond
to certain classes of queries. They are expressed as simple YAML files
containing fields such as `precondition`, `obligation` and `forbidden`.

This subpackage exposes utilities to load contract definitions from disk,
validate them using Pydantic models and register them for use by the
orchestrator. The `schemas` module defines the contract data structures
while `registry` contains helper functions to find and parse contract
files. Additional detector and evaluator functions live in
`helmsman/evals`.
"""

from .schemas import Contract
from .registry import load_contracts

__all__ = ["Contract", "load_contracts"]