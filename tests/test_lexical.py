import random

import pytest

from infra_rag.config import Settings
from infra_rag.lexical import BM25Index, query_terms
from infra_rag.models import Chunk
from infra_rag.service import bm25, lexical_statistics


def test_sparse_bm25_matches_scan_with_mixed_language_and_ties():
    rng = random.Random(20260926)
    terms = ["Warp", "cache", "KV Cache", "显存管理", "AllReduce", "a.b", "x_y", "32"]
    chunks = [
        Chunk(str(i), str(i), "fixture", " ".join(rng.choices(terms, k=i % 17)), "infra")
        for i in range(180)
    ]
    chunks += [Chunk("duplicate", "duplicate", "fixture", chunks[4].content, "infra")]
    stats = lexical_statistics(chunks)
    index = BM25Index(chunks, statistics=stats)
    for query in ["unknownterm", "", *terms] + [
        " ".join(rng.choices(terms, k=5)) for _ in range(25)
    ]:
        expected = bm25(query, chunks, stats)
        actual = index.search(query)
        assert [doc for doc, _ in actual] == [doc for doc, _ in expected]
        assert [score for _, score in actual] == pytest.approx([score for _, score in expected])
        assert index.search(query, top_k=5) == actual[:5]


def test_sparse_bm25_empty_corpus():
    assert BM25Index([], statistics=lexical_statistics([])).search("Warp") == []


def test_technical_query_keeps_identifiers_chinese_and_numeric_conditions():
    terms = query_terms("How can I use local_rank with KV Cache 显存管理 32?", "technical")
    assert {"local_rank", "kv", "cache", "32", "显存管理"} <= terms
    assert not {"how", "can", "i", "with", "?"} & terms
    assert Settings().fingerprint() == Settings(lexical_query_mode="technical").fingerprint()


def test_bm25_scores_are_identical_across_hash_seeds():
    import os
    import subprocess
    import sys

    code = """
import json
from infra_rag.models import Chunk
from infra_rag.service import lexical_statistics, bm25
from infra_rag.lexical import BM25Index
text='alpha beta gamma delta epsilon zeta '
chunks=[Chunk(str(i),'p','s',text*(i+1)+'alpha '*i,'infra') for i in range(5)]
stats=lexical_statistics(chunks)
q='alpha beta gamma delta epsilon zeta'
print(json.dumps([BM25Index(chunks,statistics=stats).search(q),bm25(q,chunks,stats)]))
"""
    outputs = [
        subprocess.check_output(
            [sys.executable, "-c", code], env={**os.environ, "PYTHONHASHSEED": seed}, text=True
        )
        for seed in ("1", "17", "42")
    ]
    assert outputs[0] == outputs[1] == outputs[2]
