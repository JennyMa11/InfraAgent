import pytest

from infra_rag.config import Settings
from infra_rag.evaluation import evidence_metrics, resolve_alternatives, resolve_spans
from infra_rag.service import RetrievalService


def test_gold_spans_resolve_without_consulting_retrieval(tmp_path):
    service = RetrievalService(Settings(data_dir=tmp_path / "db"))
    document = tmp_path / "notes.md"
    document.write_text("# NCCL\n\nAllReduce 规约结果分发给所有 rank。")
    service.ingest(document)
    service.search = lambda *a, **k: pytest.fail("gold resolution must not call retrieval")
    dataset = [
        {
            "id": "q1",
            "query": "unrelated",
            "relevant_spans": [{"source": "notes.md", "text": "规约结果分发给所有 rank"}],
        }
    ]
    resolved = resolve_spans(service, dataset, tmp_path)
    assert resolved[0]["relevant"] == [service.chunks[0].id]
    assert resolved[0]["gold_matches"][0]["chunk_ids"] == resolved[0]["relevant"]
    dataset[0]["relevant_spans"][0]["text"] = "missing evidence"
    with pytest.raises(ValueError, match="evidence span"):
        resolve_spans(service, dataset, tmp_path)


def test_long_text_embedding_uses_all_token_windows():
    np = pytest.importorskip("numpy")
    from infra_rag.encoding import encode_segments

    class Tokenizer:
        def encode(self, text, **kwargs):
            return list(text)

        def decode(self, ids, **kwargs):
            return "".join(ids)

    class Model:
        max_seq_length = 6
        tokenizer = Tokenizer()
        seen = []

        def encode(self, windows, **kwargs):
            self.seen = windows
            return np.array([[1.0, 0.0] if "Z" not in value else [0.0, 1.0] for value in windows])

    model = Model()
    result = encode_segments(model, ["abcdefghZ"])
    assert model.seen == ["abcd", "efgh", "Z"]
    assert result[0][1] > 0
    assert sum(value**2 for value in result[0]) == pytest.approx(1.0)


def test_alternatives_require_complete_group_but_not_every_equivalent_source():
    item = {
        "evidence_alternatives": [
            {"requirements": [["a", "a-equivalent"], ["b"]]},
            {"requirements": [["c"]]},
        ]
    }
    partial = evidence_metrics(["a"], item, 5)
    assert partial["complete_evidence_hit"] == 0
    assert partial["evidence_coverage"] == 0.5
    complete = evidence_metrics(["noise", "c"], item, 5)
    assert complete["complete_evidence_hit"] == 1
    assert complete["evidence_mrr"] == 0.5
    assert evidence_metrics(["a-equivalent", "b"], item, 2)["complete_evidence_hit"] == 1


def test_equivalent_gold_resolution_is_independent_of_search(tmp_path):
    service = RetrievalService(Settings(data_dir=tmp_path / "db"))
    document = tmp_path / "notes.md"
    document.write_text("# Warp\n\nWarp 包含32个线程。\n\n# Another\n\n线程束包含32个连续线程。")
    service.ingest(document)
    service.search = lambda *a, **k: pytest.fail("annotations must resolve without retrieval")
    data = [
        {
            "id": "q",
            "evidence_alternatives": [
                {"id": "first", "spans": [{"source": "notes.md", "text": "Warp 包含32个线程"}]},
                {
                    "id": "other",
                    "spans": [{"source": "notes.md", "text": "线程束包含32个连续线程"}],
                },
            ],
        }
    ]
    resolved = resolve_alternatives(service, data, tmp_path)[0]
    assert len(resolved["relevant"]) == 2
    assert evidence_metrics(resolved["relevant"][:1], resolved, 1)["complete_evidence_hit"] == 1
