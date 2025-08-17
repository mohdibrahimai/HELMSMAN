"""Simple TF‑IDF retrieval for Helmsman.

The Retriever class uses scikit‑learn's TfidfVectorizer to build a
term‑frequency matrix over a small local corpus and computes cosine
similarity against incoming queries. It returns the top documents as
snippets (dicts containing the text and document id). This
implementation is deliberately minimal and does not handle large
datasets or sophisticated ranking algorithms.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Dict

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel


class Retriever:
    def __init__(self, corpus_path: str | None = None, max_docs: int = 3) -> None:
        """Initialise the Retriever.

        :param corpus_path: Path to a JSONL file containing documents. Each
            line should be a JSON object with at least an `id` and `text`
            field. If omitted, uses a built‑in small corpus shipped with
            Helmsman under `data/corpus.jsonl`.
        :param max_docs: maximum number of snippets to return per query
        """
        if corpus_path is None:
            corpus_path = str(Path(__file__).resolve().parent.parent / "data" / "corpus.jsonl")
        self.corpus_path = corpus_path
        self.max_docs = max_docs
        self.docs: List[Dict[str, str]] = []
        self._load_corpus()
        # Build TF-IDF matrix
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.doc_term_matrix = self.vectorizer.fit_transform([doc['text'] for doc in self.docs])

    def _load_corpus(self) -> None:
        """Load documents from the corpus file."""
        if not os.path.exists(self.corpus_path):
            raise FileNotFoundError(f"Corpus not found at {self.corpus_path}")
        with open(self.corpus_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    if 'id' in obj and 'text' in obj:
                        self.docs.append({'id': obj['id'], 'text': obj['text']})
                except json.JSONDecodeError:
                    continue

    def retrieve(self, query: str) -> List[Dict[str, str]]:
        """Retrieve the top documents for a query.

        Returns a list of dictionaries each containing `id` and `text`
        keys. If the query is empty, returns an empty list.
        """
        query = (query or "").strip()
        if not query:
            return []
        q_vec = self.vectorizer.transform([query])
        cosine_similarities = linear_kernel(q_vec, self.doc_term_matrix).flatten()
        # Get indices of top scores
        top_idx = cosine_similarities.argsort()[-self.max_docs:][::-1]
        snippets: List[Dict[str, str]] = []
        for idx in top_idx:
            score = cosine_similarities[idx]
            if score <= 0:
                continue
            doc = self.docs[idx]
            snippets.append({'id': doc['id'], 'text': doc['text'], 'score': float(score)})
        return snippets