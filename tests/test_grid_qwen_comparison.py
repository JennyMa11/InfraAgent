import importlib

import pytest


@pytest.fixture
def comparison(monkeypatch):
    from pathlib import Path

    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / "scripts"))
    return importlib.import_module("compare_grid_qwen")


def test_schedule_rotates_models_and_keeps_raw_queries_separate(comparison):
    cases = [{"id": str(i), "dataset": "official"} for i in range(110)]
    jobs = comparison.schedule(cases)
    assert len(jobs) == 880
    assert len({(j["profile"], j["config"], j["id"], j["rep"]) for j in jobs}) == 880
    for profile, count in [("frozen_english", 660), ("raw_query", 220)]:
        selected = [j for j in jobs if j["profile"] == profile]
        assert len(selected) == count
        for a, b in zip(selected[::2], selected[1::2], strict=True):
            assert a["id"] == b["id"] and a["config"] != b["config"]
        assert {j["config"] for j in selected[::2]} == {"qwen", "bge"}


def test_vector_reuse_contract_allows_explicit_default_but_rejects_encoding_change(
    comparison, tmp_path
):
    code = """QWEN_QUERY_PROMPT = "query:"
class QwenEncoder:
    def __init__(self, model_name="qwen"):
        self.model = model_name
    def encode(self, texts):
        return texts
"""
    old, new = tmp_path / "old.py", tmp_path / "new.py"
    old.write_text(code)
    new.write_text(code.replace('model_name="qwen"', "model_name=DEFAULT_QWEN_MODEL"))
    assert comparison.qwen_contract(old) == comparison.qwen_contract(new)
    new.write_text(code.replace("return texts", "return list(reversed(texts))"))
    assert comparison.qwen_contract(old) != comparison.qwen_contract(new)
    new.write_text(code.replace('QWEN_QUERY_PROMPT = "query:"', 'QWEN_QUERY_PROMPT = "different:"'))
    assert comparison.qwen_contract(old) != comparison.qwen_contract(new)


def test_reuse_refuses_conflicting_body_vectors_or_incomplete_rows(comparison):
    chunks = [{"content": "a"}, {"content": "a"}]
    assert comparison.vector_seeds(chunks, [[1.0], [1.0]]) == {"a": [1.0]}
    with pytest.raises(ValueError, match="Conflicting"):
        comparison.vector_seeds(chunks, [[1.0], [0.0]])
    with pytest.raises(ValueError, match="count"):
        comparison.vector_seeds(chunks, [[1.0]])


def test_frozen_protocol_paths_load_after_json_serialization(comparison, tmp_path):
    path = tmp_path / "snapshot.json"
    path.write_text('{"vectors": [[1.0]]}')
    assert comparison.load(str(path)) == comparison.load(path) == {"vectors": [[1.0]]}
