"""AND/OR span scoring over actual delivered bodies, not hit IDs."""

import copy

import pytest

from infra_rag.retrieval_diagnostic import fusion, intervals, score, validate_cases


def requirement(uid, start=0, end=5):
    return {"document_id": "d", "unit_id": uid, "char_range": [start, end]}


def test_and_or_and_adjacent_ranges_without_gap():
    case = {
        "evidence_alternatives": [
            {"requirements": [requirement("a"), requirement("b")]},
            {"requirements": [requirement("alternative")]},
        ]
    }
    assert not score({("d", "a"): [[0, 5]]}, case)["complete"]
    assert score({("d", "alternative"): [[0, 2], [2, 5]]}, case)["complete"]
    assert not score({("d", "alternative"): [[0, 2], [3, 5]]}, case)["complete"]
    assert score({("d", "a"): [[0, 5]], ("d", "b"): [[0, 5]]}, case)["complete"]


def test_actual_header_mapping_counts_once_not_synthetic_fences():
    child = {
        "document_id": "d",
        "fragments": [{"unit_id": "u", "unit_char_range": [20, 25]}],
        "rendering": {"prefix": "~~~~text\nHEADER", "repeated_header_source_range": [0, 10]},
    }
    case = {"evidence_alternatives": [{"requirements": [requirement("u", 0, 10)]}]}
    ranges = intervals([child, copy.deepcopy(child)])
    assert score(ranges, case) == {"complete": True, "coverage": 1.0}
    case["evidence_alternatives"][0]["requirements"] = [requirement("u", 10, 20)]
    assert not score(ranges, case)["complete"]


def test_gold_quote_hash_and_coordinate_binding():
    r = {
        **requirement("u"),
        "quote": "hello",
        "input_sha256": "hash",
        "source_lines": [1],
        "input_lines": [1, 1],
    }
    case = {"id": "q", "query": "what", "evidence_alternatives": [{"requirements": [r]}]}
    docs = [
        {
            "document_id": "d",
            "children": [{"input_sha256": "hash"}],
            "parents": [
                {
                    "units": [
                        {
                            "unit_id": "u",
                            "content": "hello source",
                            "source_lines": [1],
                            "input_lines": [1, 1],
                        }
                    ]
                }
            ],
        }
    ]
    validate_cases([case], docs)
    for key, value in [("quote", "wrong"), ("input_sha256", "wrong"), ("source_lines", [2])]:
        bad = copy.deepcopy(case)
        bad["evidence_alternatives"][0]["requirements"][0][key] = value
        with pytest.raises(ValueError):
            validate_cases([bad], docs)


def test_fusion_is_deterministic_and_keeps_union():
    a = [("a", 1), ("b", 0.5)]
    b = [("b", 1), ("c", 0.2)]
    result = fusion([a, b])
    assert result[0][0] == "b"
    assert {cid for cid, _ in result} == {"a", "b", "c"}
    assert result == fusion([b, a])
