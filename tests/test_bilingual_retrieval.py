import copy

import pytest

from infra_rag.bilingual_retrieval import link_preceding_explanations, supplement


def test_supplement_preserves_baseline_and_cap():
    base = [("a", 2), ("b", 1)]
    assert supplement(base, [[("b", 3), ("c", 2)]], [[("d", 1)]], cap=4) == ["a", "b", "c", "d"]
    assert supplement(base, [[("c", 2)]], cap=2) == ["a", "b"]
    with pytest.raises(ValueError):
        supplement(base, [], cap=1)


def test_context_links_are_local_and_leave_source_and_ids_intact():
    docs = [
        {
            "parents": [
                {
                    "units": [
                        {"unit_id": "intro", "kind": "paragraph"},
                        {"unit_id": "rule", "kind": "condition"},
                    ]
                },
                {"units": [{"unit_id": "other", "kind": "code"}]},
            ],
            "children": [
                {
                    "chunk_id": "c",
                    "fragments": [{"unit_id": "rule"}],
                    "context_unit_ids": [],
                    "content": "original",
                },
                {"chunk_id": "d", "fragments": [{"unit_id": "other"}], "context_unit_ids": []},
            ],
        }
    ]
    before = copy.deepcopy(docs)
    linked, links = link_preceding_explanations(docs)
    assert docs == before
    assert linked[0]["children"][0]["context_unit_ids"] == ["intro"]
    assert linked[0]["children"][0]["content"] == "original"
    assert linked[0]["children"][1]["context_unit_ids"] == []
    assert len(links) == 1
