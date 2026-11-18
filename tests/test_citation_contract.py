import json

from infra_rag.assistant import AnswerService
from infra_rag.config import Settings
from infra_rag.offline_evaluation import generate_answer


def test_long_source_ids_use_short_aliases_and_resolve_exactly():
    cid = "E" + "a" * 32

    class Model:
        model = "fixture"

        def generate(self, messages):
            assert "[E1]" in messages[-1]["content"]
            assert cid not in messages[-1]["content"]
            return json.dumps({"supported": True, "answer": "有证据。[E1]", "citations": ["E1"]})

    context = {"evidence": [{"citation_id": cid, "content": "source", "locator": "url"}]}
    r = generate_answer({"query": "question"}, context, Settings(), Model())
    assert r["error"] is None
    assert r["checks"]["citation_ids_valid"] is True
    assert r["raw_model_checks"]["citation_ids_valid"] is False
    assert r["response"]["answer"] == "有证据。[" + cid + "]"
    assert r["response"]["citations"][0]["citation_id"] == cid


def test_unknown_or_unlisted_inline_citations_rejected_at_any_length():
    for cid in ["E1", "E" + "b" * 24, "E" + "b" * 28, "E" + "b" * 32]:
        assert not AnswerService._valid(
            {"supported": True, "answer": f"x[{cid}]", "citations": ["Eok"]}, {"Eok": {}}
        )
    assert not AnswerService._valid(
        {"supported": False, "answer": "no", "citations": ["Eunknown"]}, {"E1": {}}
    )


def test_retry_lists_exact_allowed_ids_without_fuzzy_repair():
    class Model:
        model = "fixture"

        def __init__(self):
            self.calls = 0

        def generate(self, messages):
            self.calls += 1
            if self.calls == 1:
                return json.dumps({"supported": True, "answer": "x[Ebad]", "citations": ["Ebad"]})
            assert "E1" in messages[-1]["content"]
            return json.dumps({"supported": True, "answer": "x[E1]", "citations": ["E1"]})

    model = Model()
    context = {"evidence": [{"citation_id": "E" + "c" * 32, "content": "source", "locator": "url"}]}
    result = generate_answer({"query": "q"}, context, Settings(), model)
    assert model.calls == 2 and result["response"]["status"] == "answered"
