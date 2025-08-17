"""Basic unit tests for contract loading and evaluation.

These tests use the built‑in corpus and contracts to verify that the
loader correctly parses YAML files and that the detectors and evaluators
behave as expected on simple inputs. They can be run with pytest.
"""

from helmsman.contracts import load_contracts
from helmsman.evals.disambiguation import detect_ambiguity, check_asked_then_answered
from helmsman.evals.citation_precision import detect_claims, check_citation_quality


def test_load_contracts():
    contracts = load_contracts('helmsman/contracts/builtin')
    assert 'disambiguate_before_answer' in contracts
    assert 'citations_minimum_and_precision' in contracts


def test_detect_ambiguity():
    assert detect_ambiguity('Tell me about Jordan')
    assert detect_ambiguity('What happened last week?')
    assert not detect_ambiguity('Tell me about computers')


def test_check_asked_then_answered():
    # Response contains question mark -> passes
    conv = ['Who is Jordan?', 'Do you mean the basketball player or the country?']
    assert check_asked_then_answered(conv, {'clarify_interrogatives': ['who', 'what']})
    # Response contains interrogative phrase -> passes
    conv2 = ['Tell me about Apple', 'Which Apple do you mean, the fruit or the company?']
    assert check_asked_then_answered(conv2, {'clarify_interrogatives': ['which']})
    # No clarification -> fails
    conv3 = ['Tell me about Jordan', 'Jordan is a country in the Middle East.']
    assert not check_asked_then_answered(conv3, {'clarify_interrogatives': ['which']})


def test_detect_claims():
    assert detect_claims('The population of Jordan is about 10 million.')
    assert detect_claims('Apple was founded in 1976 by Steve Jobs.')
    assert not detect_claims('Hello world.')


def test_check_citation_quality():
    # With 2 citations -> passes
    assert check_citation_quality(['doc1', 'doc2'], {'min_citations': 2, 'require_independent_domains': True})
    # With 1 citation -> fails
    assert not check_citation_quality(['doc1'], {'min_citations': 2})
    # Duplicate citations with independence required -> fails
    assert not check_citation_quality(['doc1', 'doc1'], {'min_citations': 2, 'require_independent_domains': True})