"""Sparse BM25 scoring with the same tokenization and formula as the scan baseline."""

import heapq
import math
from collections import defaultdict

from .encoding import tokenize

ENGLISH_STOPWORDS = frozenset(
    "a an the and or of to in on at by for from with as is are was were be been being "
    "i me my we us our you your he she it its they them their this that these those "
    "do does did doing have has had can could would should will shall may might "
    "what which who why how when where if then than so but not also just very "
    "there here some any all each both into about out up down more most please thanks".split()
)


def query_terms(query, mode="raw"):
    terms = set(tokenize(query))
    if mode == "technical":
        return {
            term
            for term in terms
            if term not in ENGLISH_STOPWORDS and any(character.isalnum() for character in term)
        }
    return terms


class BM25Index:
    def __init__(self, chunks, *, statistics, query_mode="raw"):
        if query_mode not in {"raw", "technical"}:
            raise ValueError("unknown lexical query mode")
        self.query_mode = query_mode
        documents, frequencies, lengths, average = statistics
        self.ids = [chunk.id for chunk in chunks]
        self.postings = defaultdict(list)
        self.normalizers = [1.5 * (0.25 + 0.75 * length / average) for length in lengths]
        count = len(documents)
        self.idf = {
            term: math.log(1 + (count - frequency + 0.5) / (frequency + 0.5))
            for term, frequency in frequencies.items()
        }
        for index, document in enumerate(documents):
            for term, frequency in document.items():
                self.postings[term].append((index, frequency))

    def search(self, query, top_k=None):
        scores = defaultdict(float)
        for term in sorted(query_terms(query, self.query_mode)):
            for index, frequency in self.postings.get(term, ()):
                scores[index] += (
                    self.idf[term] * frequency * 2.5 / (frequency + self.normalizers[index])
                )
        results = [(self.ids[index], score) for index, score in scores.items() if score > 0]

        def key(item):
            return -item[1], item[0]

        return (
            sorted(results, key=key) if top_k is None else heapq.nsmallest(top_k, results, key=key)
        )
