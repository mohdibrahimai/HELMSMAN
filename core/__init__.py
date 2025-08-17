"""Core orchestration and utility functions.

The core package glues together the contract definitions, the retrieval
harness, truth checking and metrics into a cohesive workflow. It
contains the orchestrator script which can be invoked from the command
line to run a set of queries through the system and record results.
"""

from .orchestrator import run_orchestration

__all__ = ["run_orchestration"]