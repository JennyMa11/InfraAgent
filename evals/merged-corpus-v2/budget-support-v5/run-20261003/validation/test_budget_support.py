import copy
import importlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from infra_rag.budget_evidence import budget_pack
from infra_rag.claim_guard import (
    STRENGTH_PROMPT,
    generate_experimental,
    guarded_response,
    parse_verdict,
    verify_answer,
)
from infra_rag.config import Settings
from infra_rag.models import Chunk, Hit


def hit(cid, text, score=0.8, parent="p", source="notes.md", heading=False):
    c = Chunk(
        cid,
        parent,
        source,
        text,
        "infra",
        heading="Evidence",
        metadata={"body_type": "heading" if heading else "explanation"},
    )
    return Hit(c, 0.1, rerank_score=score)


def test_budget_selection_keeps_full_code_and_respects_both_budgets():
    hits = [
        hit("first", "A short fact."),
        hit("code", "```cpp\n" + "x" * 800 + "\n```"),
        hit("late", "Necessary independent fact.", 0.7),
    ]
    selected, context, _ = budget_pack(
        hits, {"evidence": []}, {}, "independent fact", len, token_budget=180, char_budget=120
    )
    assert [h.chunk.id for h in selected] == ["first", "late"]
    assert context["used_characters"] <= 120 and context["used_tokens"] <= 180
    assert all(not e["truncated"] for e in context["evidence"])


def test_budget_neighbor_prior_never_crosses_source_or_parent():
    h = hit("anchor", "Anchor fact.")
    neighbors = [
        hit("good", "Required supporting condition."),
        hit("other", "Other source.", source="other.md"),
        hit("parent", "Other parent.", parent="other"),
    ]
    chunks = {h.chunk.id: h.chunk for h in neighbors}
    original = copy.deepcopy([h] + neighbors)
    selected, _, trace = budget_pack(
        [h], {"evidence": [{"chunk_id": c} for c in chunks]}, chunks, "condition", len
    )
    assert [h.chunk.id for h in selected] == ["anchor", "good"]
    assert list(trace["neighbor_priors"]) == ["good"]
    assert [h] + neighbors == original


def test_coverage_rewards_new_query_information_over_repetition():
    hits = [
        hit("a", "alpha fact"),
        hit("repeat", "alpha fact", 0.8),
        hit("new", "beta detail", 0.75),
    ]
    a = budget_pack(hits, {"evidence": []}, {}, "alpha beta", len)[2]
    b = budget_pack(hits, {"evidence": []}, {}, "alpha beta", len, coverage=True)[2]
    assert a["selection_trace"][1]["chunk_id"] == "repeat"
    assert b["selection_trace"][1]["chunk_id"] == "new"


def test_budget_skips_headings_and_rejects_duplicate_or_nan():
    h = hit("body", "Real fact.")
    selected, _, _ = budget_pack(
        [hit("heading", "# Heading", heading=True), h], {"evidence": []}, {}, "query", len
    )
    assert [x.chunk.id for x in selected] == ["body"]
    for hits in ([h, h], [hit("bad", "bad", float("nan"))]):
        with pytest.raises(ValueError):
            budget_pack(hits, {"evidence": []}, {}, "query", len)


@pytest.mark.parametrize(
    "value",
    [
        {"verdict": "supported", "issues": [{"claim": "actual"}]},
        {"verdict": "unsupported", "issues": []},
        {
            "verdict": "unsupported",
            "issues": [
                {"claim": "invented", "citation_ids": ["E1"], "type": "scope", "reason": "scope"}
            ],
        },
        {
            "verdict": "unsupported",
            "issues": [
                {"claim": "actual", "citation_ids": ["unknown"], "type": "scope", "reason": "scope"}
            ],
        },
        {"verdict": "pass", "issues": []},
    ],
)
def test_verifier_never_passes_invalid_or_unanchored_output(value):
    parsed, error = parse_verdict(json.dumps(value), "actual claim", {"E1"})
    assert parsed["verdict"] == "uncertain" and error


def test_verifier_accepts_anchored_issue_and_guard_preserves_original():
    value = {
        "verdict": "unsupported",
        "issues": [
            {"claim": "actual", "citation_ids": ["E1"], "type": "strength", "reason": "too strong"}
        ],
    }
    parsed, error = parse_verdict(json.dumps(value), "actual claim", {"E1"})
    assert error is None
    g = {"response": {"status": "answered", "answer": "actual claim", "citations": ["E1"]}}
    saved = copy.deepcopy(g)
    assert guarded_response(g, parsed)["status"] == "no_evidence"
    assert guarded_response(g, {"verdict": "supported"}) == g["response"]
    assert g == saved


def test_verifier_refusal_skips_model_and_only_sees_actually_cited_context():
    class Model:
        model = "fake"

        def generate(self, messages):
            self.messages = messages
            return '{"verdict":"supported","issues":[]}'

    model = Model()
    g = {"response": {"status": "no_evidence"}}
    assert not verify_answer({"query": "q"}, g, {}, model)["calls"]
    evidence = [
        {"citation_id": "E1", "content": "cited fact"},
        {"citation_id": "E2", "content": "uncited fact"},
    ]
    g = {"response": {"status": "answered", "answer": "cited fact", "citations": evidence[:1]}}
    result = verify_answer({"query": "q"}, g, {"evidence": evidence}, model)
    assert result["verdict"] == "supported"
    assert "uncited fact" not in model.messages[1]["content"]


def test_strength_prompt_is_opt_in_and_recorded_without_changing_default(tmp_path):
    from infra_rag.assistant import SYSTEM_PROMPT

    cid = "E" + "a" * 24

    class Model:
        model = "fake"

        def generate(self, messages):
            return json.dumps({"supported": True, "answer": f"A fact [{cid}]", "citations": [cid]})

    q = {"query": "q"}
    context = {"evidence": [{"citation_id": cid, "content": "A fact", "locator": "notes.md"}]}
    settings = Settings(data_dir=tmp_path)
    before = copy.deepcopy(context)
    baseline = generate_experimental(q, context, settings, Model())
    guarded = generate_experimental(q, context, settings, Model(), strength=True)
    assert baseline["calls"][0]["messages"][0]["content"] == SYSTEM_PROMPT
    assert guarded["calls"][0]["messages"][0]["content"] == SYSTEM_PROMPT + STRENGTH_PROMPT
    assert baseline["calls"][0]["messages"][1] == guarded["calls"][0]["messages"][1]
    assert context == before and baseline["error"] is None and guarded["error"] is None


def test_verifier_call_error_is_uncertain():
    class Model:
        model = "fake"

        def generate(self, messages):
            raise RuntimeError("offline")

    g = {"response": {"status": "answered", "answer": "a", "citations": []}}
    result = verify_answer({"query": "q"}, g, {"evidence": []}, Model())
    assert result["verdict"] == "uncertain" and len(result["calls"]) == 1
    assert result["error"]


def test_dev_setup_freezes_tokenizer_options_and_both_sample_lists(tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / "scripts"))
    benchmark = importlib.import_module("benchmark_budget_v5")
    old, output, data, model = [tmp_path / n for n in ("old", "output", "data", "model")]
    for directory in (old, output, data, model, tmp_path / "scripts"):
        directory.mkdir()
    (data / "chunks.json").write_text("[]")
    (data / "manifest.json").write_text(
        json.dumps({"chunks_sha256": benchmark.digest(data / "chunks.json")})
    )
    (model / "sentence_bert_config.json").write_text('{"do_lower_case":true}')
    dev_hashes = {}
    for ds, name in (
        ("official", "infra-official-v1-reviewed"),
        ("repository", "repository-benchmark"),
    ):
        directory = tmp_path / "evals" / name
        directory.mkdir(parents=True)
        (directory / "dev.json").write_text("[]")
        dev_hashes[ds] = benchmark.digest(directory / "dev.json")
    prior = {
        "directory": "data",
        "manifest_sha256": benchmark.digest(data / "manifest.json"),
        "models": {"embedding": {"path": str(model), "files": {}}},
        "dev_hashes": dev_hashes,
        "generation_ids": ["official-a"],
        "coverage_ids": ["repo-b"],
    }
    (old / "protocol.json").write_text(json.dumps(prior))
    records = [
        {"dataset": ds, "id": str(i), "arm": arm}
        for ds, n in (("official", 60), ("repository", 50))
        for i in range(n)
        for arm in range(7)
    ]
    (old / "rows.jsonl").write_text("\n".join(json.dumps(r) for r in records))
    (old / "answers.jsonl").write_text("")
    (old / "source-audit.json").write_text('{"source_files":[]}')
    files = {
        name: benchmark.digest(old / name)
        for name in ("protocol.json", "rows.jsonl", "answers.jsonl", "source-audit.json")
    }
    (old / "artifacts-manifest.json").write_text(json.dumps({"files": files}))
    (output / "experiment-plan.md").write_text("frozen plan")
    script = tmp_path / "scripts" / "benchmark_budget_v5.py"
    for name in (script.name, "benchmark_selection_v3.py", "prepare_corpus_v2.py"):
        (script.parent / name).write_text("# fixture")
    options = []

    class Tokenizer:
        @staticmethod
        def from_pretrained(path, **kwargs):
            options.append(kwargs)
            return SimpleNamespace(encode=lambda text, **kw: list(text))

    monkeypatch.setitem(sys.modules, "transformers", SimpleNamespace(AutoTokenizer=Tokenizer))
    monkeypatch.setattr(benchmark, "ROOT", tmp_path)
    monkeypatch.setattr(benchmark, "OLD", old)
    monkeypatch.setattr(benchmark, "OUT", output)
    monkeypatch.setattr(benchmark, "__file__", str(script))
    monkeypatch.setattr(benchmark, "client", lambda _: SimpleNamespace(configuration=lambda: {}))
    read = Path.read_text

    def dev_only(path, *args, **kwargs):
        assert path.name not in {"holdout.json", "test.json"}
        return read(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", dev_only)
    run = output / "run"
    protocol, *_ = benchmark.setup(run)
    assert protocol["generation_ids"] == ["official-a", "repo-b"]
    assert options == [{"local_files_only": True, "do_lower_case": True}]
    assert benchmark.setup(run)[0] == protocol
    (model / "sentence_bert_config.json").write_text('{"do_lower_case":false}')
    with pytest.raises(AssertionError):
        benchmark.setup(run)
