"""Naive answer generator for Helmsman.

The `Answerer` class produces a response by selecting the first
retrieved document and returning its first sentence as the answer.
This implementation is intentionally simplistic and is intended as a
placeholder for a real language model. Citations returned by the
answerer are the identifiers of the retrieved documents.
"""

from __future__ import annotations

import re
from typing import List, Dict, Tuple


class Answerer:
    def __init__(self, system_prompt: str = "") -> None:
        """
        :param system_prompt: A system prompt string (unused in this naive implementation)
        """
        self.system_prompt = system_prompt

    def answer(self, query: str, retrieved_docs: List[Dict[str, str]]) -> Tuple[str, List[str]]:
        """Generate an answer and citations for a query.

        This simplistic implementation takes the first retrieved document,
        splits its text into sentences using a naive period delimiter and
        returns the first sentence as the answer. Citations are the
        identifiers of all retrieved documents.

        :param query: the user query
        :param retrieved_docs: list of retrieved document dicts with `id` and `text`
        :returns: a tuple of (answer string, list of citation ids)
        """
        if not retrieved_docs:
            return "I'm sorry, I couldn't find any relevant information.", []
        doc = retrieved_docs[0]
        text = doc['text']
        # Split into sentences (very naive)
        sentences = re.split(r'(?<=[.?!])\s+', text.strip())
        answer = sentences[0] if sentences else text
        citations = [d['id'] for d in retrieved_docs]
        return answer, citations