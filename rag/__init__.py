"""Retrieval and answer generation utilities for Helmsman.

The RAG (retrieval‑augmented generation) harness in this reference
implementation is intentionally lightweight. It does not query any
external APIs or models. Instead, it uses a small local corpus of
documents and a TF‑IDF vectoriser to retrieve relevant snippets. The
answerer then returns a simple summary of the top document along with
citations referencing the document IDs.
"""

from .retrieve import Retriever
from .answer import Answerer

__all__ = ["Retriever", "Answerer"]