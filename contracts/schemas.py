"""Pydantic models for Helmsman contract definitions.

Contracts are defined declaratively in YAML files. They capture the
behavioural expectations for a model when handling a particular class of
inputs. Each contract specifies a precondition (a named detector
function), obligations (things the model must do), forbidden actions
(things the model must not do), metrics for scoring and metadata such as
the topics and locales to which the contract applies.

This module defines the Python data structures used to represent those
contracts. It deliberately does not enforce the semantics of the fields
at load time; downstream components such as the orchestrator are
responsible for dispatching to detector and evaluator functions based on
the names provided in the contract definitions.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, validator


class ContractMetrics(BaseModel):
    """Scoring configuration for a contract.

    A contract can define how its pass/fail outcomes should be aggregated
    across a test pack and the target thresholds it must meet. The
    orchestrator uses these settings to compute summary statistics.
    """

    weight: float = Field(1.0, description="Relative importance of this contract")
    pass_criteria: str = Field(
        ..., description="Name of the function used to determine pass/fail"
    )
    scoring: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional parameters passed to the scoring function",
    )


class ContractMessages(BaseModel):
    """Messages associated with contract outcomes and guidance."""

    on_pass: Optional[str] = None
    on_fail_count: Optional[str] = None
    on_fail_independence: Optional[str] = None
    on_fail_precision: Optional[str] = None
    on_fail_coverage: Optional[str] = None
    on_fail_answered_directly: Optional[str] = None
    on_fail_no_wait: Optional[str] = None
    guidance: Optional[List[str]] = None


class ContractDetector(BaseModel):
    """Definition of a detector or evaluator function for a contract.

    A detector checks whether a precondition holds for a given query and
    conversation. An evaluator computes whether the contract's
    obligations have been met and can return additional diagnostic
    information.
    """

    fn: str
    args: Dict[str, Any] = Field(default_factory=dict)


class Contract(BaseModel):
    """Root model representing a single contract definition."""

    id: str = Field(..., description="Unique identifier for this contract")
    version: str = Field("0.1.0", description="Semantic version of the contract definition")
    description: Optional[str] = Field(None, description="Long form description")
    applies_to: List[str] = Field(
        ..., description="List of topic tags to which the contract applies"
    )
    locales: List[str] = Field(
        ..., description="List of locale codes supported by this contract"
    )
    precondition: Optional[str] = Field(
        None, description="Name of detector function to test if this contract applies"
    )
    obligation: Dict[str, Any] = Field(
        default_factory=dict,
        description="Key/value pairs describing what the model must do",
    )
    forbidden: Dict[str, Any] = Field(
        default_factory=dict,
        description="Key/value pairs describing what the model must not do",
    )
    metrics: Optional[ContractMetrics] = None
    detectors: Optional[Dict[str, ContractDetector]] = None
    messages: Optional[ContractMessages] = None
    examples: Optional[List[Dict[str, Any]]] = None

    @validator("applies_to", "locales", pre=True)
    def _ensure_list(cls, v):  # type: ignore[no-self-argument]
        # YAML loaders sometimes load single strings as scalars rather than lists.
        if isinstance(v, str):
            return [v]
        return v