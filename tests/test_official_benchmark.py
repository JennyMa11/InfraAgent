import json
import math
from copy import deepcopy
from dataclasses import asdict

import pytest

from infra_rag.assistant import AnswerService
from infra_rag.benchmarking import (
    automatic_answer_checks,
    bootstrap_groups,
    create_run,
    digest,
    graded_metrics,
    human_summary,
    validate_dataset,
    write_new,
)
from infra_rag.config import Settings
from infra_rag.offline_evaluation import (
    answer_review_template,
    enrich_questions,
    evaluation_rows,
    generate_answer,
    oracle_context,
    resolve_evidence,
    span_coverage,
)
from infra_rag.service import RetrievalService


@pytest.fixture
def frozen(tmp_path):
    corpus = tmp_path / "data/corpus"
    corpus.mkdir(parents=True)
    document = corpus / "cache.md"
    document.write_text("# KV Cache\n\nKV Cache 保存注意力键值。释放缓存可以回收显存。\n")
    raw = tmp_path / "data/raw.txt"
    raw.write_bytes(document.read_bytes())
    dataset = tmp_path / "evals/candidates"
    doc = {
        "id": "cache",
        "source": "cache.md",
        "sha256": digest(document),
        "raw_path": "data/raw.txt",
        "raw_sha256": digest(raw),
        "line_map": [1, 2, 3],
        "release": "fixture",
    }
    write_new(dataset / "corpus-manifest.json", {"corpus_root": "data/corpus", "documents": [doc]})
    span = {
        "document_id": "cache",
        "source": "../../data/corpus/cache.md",
        "sha256": digest(document),
        "line_start": 3,
        "line_end": 3,
        "text": "释放缓存可以回收显存。",
        "source_url": "https://example.test/source",
    }
    positive = {
        "id": "q1",
        "query": "KV缓存释放后能回收什么资源？",
        "group_id": "release",
        "question_type": "single_hop",
        "answerable": True,
        "relevant_spans": [span],
        "evidence_alternatives": [{"id": "a", "spans": [span]}],
        "answer_key": {"required_points": ["回收显存"], "forbidden_claims": ["销毁权重"]},
        "review": {"status": "pending"},
    }
    negative = {
        "id": "q2",
        "query": "这台未说明硬件的机器释放缓存要精确几毫秒？",
        "group_id": "timing",
        "question_type": "unanswerable",
        "answerable": False,
        "relevant_spans": [],
        "evidence_alternatives": [],
        "missing_information": "实测数据",
        "answer_key": {"required_points": ["缺少测量"], "forbidden_claims": ["编造时间"]},
        "review": {"status": "pending"},
    }
    splits = {"dev": [positive], "holdout": [negative]}
    for name, questions in splits.items():
        write_new(dataset / f"{name}.json", questions)
    refresh_manifest(dataset)
    return tmp_path, dataset, document, splits


def refresh_manifest(dataset):
    record = {
        "corpus_manifest_sha256": digest(dataset / "corpus-manifest.json"),
        "splits": {
            split: {
                "sha256": digest(dataset / f"{split}.json"),
                "questions": len(json.loads((dataset / f"{split}.json").read_text())),
            }
            for split in ("dev", "holdout")
        },
    }
    (dataset / "dataset-manifest.json").write_text(json.dumps(record))


def replace_questions(dataset, splits):
    for split, questions in splits.items():
        (dataset / f"{split}.json").write_text(json.dumps(questions, ensure_ascii=False))
    refresh_manifest(dataset)


def test_hashes_and_human_review_gate(frozen):
    root, dataset, source, _ = frozen
    validate_dataset(dataset, root, full_size=False)
    with pytest.raises(ValueError, match="independent review"):
        validate_dataset(dataset, root, formal=True, full_size=False)
    source.write_text("changed")
    with pytest.raises(ValueError, match="changed or unsafe source"):
        validate_dataset(dataset, root, full_size=False)


def test_corpus_rejects_unlisted_qa_files(frozen):
    root, dataset, source, _ = frozen
    (source.parent / "questions.md").write_text("benchmark question and answer")
    with pytest.raises(ValueError, match="unlisted"):
        validate_dataset(dataset, root, full_size=False)


@pytest.mark.parametrize("failure", ["locator", "group", "duplicate", "empty_gold", "ai_approval"])
def test_reject_invalid_provenance_and_split_leakage(frozen, failure):
    root, dataset, _, original = frozen
    splits = deepcopy(original)
    q = splits["dev"][0]
    if failure == "locator":
        q["relevant_spans"][0]["line_start"] = 99
    elif failure == "group":
        splits["holdout"][0]["group_id"] = q["group_id"]
    elif failure == "duplicate":
        splits["holdout"][0]["query"] = q["query"]
    elif failure == "empty_gold":
        q["relevant_spans"] = []
        q["evidence_alternatives"] = []
    else:
        q["review"] = {
            "status": "approved",
            "reviewer": "AI",
            "reviewed_at": "today",
            "notes": "checked",
            "method": "AI",
        }
    replace_questions(dataset, splits)
    with pytest.raises(ValueError):
        validate_dataset(dataset, root, full_size=False)


def test_duplicate_evidence_across_groups_is_rejected(frozen):
    root, dataset, _, splits = frozen
    clone = deepcopy(splits["dev"][0])
    clone.update(id="q3", query="本例释放键值缓存会降低哪一种存储占用？", group_id="other")
    splits["holdout"] = [clone]
    replace_questions(dataset, splits)
    with pytest.raises(ValueError, match="shared evidence"):
        validate_dataset(dataset, root, full_size=False)


def test_document_metrics_with_graded_relevance_and_duplicate_ids():
    result = graded_metrics(["irrelevant", "b", "b", "a"], {"a": 3, "b": 1, "c": 0}, 3)
    assert result["recall"] == 1
    assert result["precision"] == pytest.approx(2 / 3)
    assert result["mrr"] == 0.5
    assert result["ndcg"] == pytest.approx((1 / math.log2(3) + 3 / 2) / (3 + 1 / math.log2(3)))
    with pytest.raises(ValueError):
        graded_metrics(["a"], {"a": 0}, 5)


def test_context_coverage_checks_truncated_text_and_or_and(frozen):
    _, dataset, _, splits = frozen
    q = enrich_questions(splits["dev"], dataset)[0]
    span = q["evidence_alternatives"][0]["spans"][0]
    second = {**span, "text": "保存注意力键值"}
    q["evidence_alternatives"][0]["spans"].append(second)
    evidence = [{"source": span["absolute_source"], "content": span["text"]}]
    assert span_coverage(evidence, q) == {"coverage": 0.5, "complete": 0}
    q["evidence_alternatives"].append({"id": "alternative", "spans": [span]})
    assert span_coverage(evidence, q)["complete"] == 1
    evidence[0]["content"] = "释放缓存可以"
    assert span_coverage(evidence, q)["complete"] == 0


def test_evidence_crossing_children_requires_both_in_source_order():
    from types import SimpleNamespace

    from infra_rag.evaluation import evidence_metrics
    from infra_rag.models import Chunk

    chunks = [
        Chunk("left", "parent", "source", "计算仍执行，", "infra"),
        Chunk("right", "parent", "source", "仅减少访存。", "infra"),
    ]
    q = {
        "id": "q",
        "answerable": True,
        "evidence_alternatives": [
            {
                "id": "a",
                "spans": [
                    {
                        "absolute_source": "source",
                        "text": "计算仍执行，仅减少访存。",
                        "document_id": "doc",
                    }
                ],
            }
        ],
    }
    resolved = resolve_evidence(SimpleNamespace(chunks=chunks), [q])["q"]
    assert evidence_metrics(["left"], resolved, 5)["complete_evidence_hit"] == 0
    assert evidence_metrics(["left", "right"], resolved, 5)["complete_evidence_hit"] == 1
    context = [
        {"source": "source", "parent_id": "parent", "content": c.content, "source_position": i}
        for i, c in enumerate(chunks)
    ]
    assert span_coverage(list(reversed(context)), q)["complete"] == 1
    context[1]["source_position"] = 2
    assert span_coverage(context, q)["complete"] == 0


def test_citation_validity_never_implies_fact_correctness():
    raw = json.dumps({"supported": True, "answer": "KV释放会销毁模型权重。", "citations": ["E1"]})
    flags = automatic_answer_checks(raw, [{"citation_id": "E1"}])
    assert flags["citation_ids_valid"] is True
    assert flags["fact_correct"] is None
    assert AnswerService._valid(json.loads(raw), {"E1": {}})
    row = {
        "review_key": "q1:oracle",
        "group_id": "g",
        "answerable": True,
        "required_points": ["只释放缓存"],
        "generation": {"checks": flags, "error": None},
    }
    reviews = answer_review_template([row])
    assert human_summary([row], reviews)["answer_correctness"] is None
    reviews[0].update(
        status="approved",
        reviewer="independent reviewer",
        reviewed_at="2026-10-01",
        notes="答案与证据矛盾",
        fact_correct=False,
        contradiction=True,
        unsupported_claim=True,
        refusal_appropriate=False,
        points_supported=0,
        citation_claims=1,
        citation_supported=0,
    )
    result = human_summary([row], reviews)
    assert result["answer_correctness"] == 0
    assert result["contradiction_rate"] == 1
    reviews[0]["answer_sha256"] = "old"
    with pytest.raises(ValueError, match="hash mismatch"):
        human_summary([row], reviews)


def test_runs_and_artifacts_are_never_overwritten(tmp_path):
    directory = create_run(tmp_path / "run", {"kind": "test"})
    original = digest(directory / "manifest.json")
    with pytest.raises(FileExistsError):
        create_run(directory, {"kind": "other"})
    with pytest.raises(FileExistsError):
        write_new(directory / "manifest.json", {})
    assert digest(directory / "manifest.json") == original


class EchoModel:
    model = "fixture"

    def __init__(self):
        self.inputs = []

    def generate(self, messages):
        import re

        self.inputs.append(deepcopy(messages))
        cid = re.search(r"\[(E[a-f0-9]{24})\]", messages[-1]["content"])[1]
        return json.dumps({"supported": True, "answer": "可以回收显存。", "citations": [cid]})


def test_generation_isolated_and_failures_are_preserved(frozen):
    _, dataset, _, splits = frozen
    q = enrich_questions(splits["dev"], dataset)[0]
    context = oracle_context(q)
    settings = Settings(data_dir=dataset / "unused")
    model = EchoModel()
    first = generate_answer(q, context, settings, model)
    second = generate_answer(q, context, settings, model)
    assert first["checks"]["citation_ids_valid"]
    assert model.inputs[0] == model.inputs[1]
    assert len(model.inputs[0]) == 2
    assert first["response"]["conversation_id"] != second["response"]["conversation_id"]
    assert not settings.data_dir.exists()

    class Broken(EchoModel):
        def generate(self, messages):
            raise RuntimeError("offline")

    failure = generate_answer(q, context, settings, Broken())
    assert failure["error"] == "RuntimeError: offline"
    assert failure["calls"][0]["error"] == "RuntimeError: offline"


def test_retrieval_excludes_negative_labels_and_tracks_delivered_evidence(frozen):
    root, dataset, source, splits = frozen
    service = RetrievalService(Settings(data_dir=root / "data/test-index", chunk_size=100))
    service.ingest(source, "infra")
    original = asdict(service.settings)
    model = EchoModel()
    rows = list(
        evaluation_rows(
            service, splits["dev"] + splits["holdout"], dataset, client=model, variants=["bm25"]
        )
    )
    assert len(rows) == 4
    positive = next(r for r in rows if r["variant"] == "bm25" and r["answerable"])
    negative = next(r for r in rows if r["variant"] == "bm25" and not r["answerable"])
    assert positive["delivered"]["complete"] == 1
    assert positive["at_k"]["5"]["complete_evidence_hit"] == 1
    assert positive["resolved_gold"]["relevant"] == positive["retrieved"]
    assert positive["resolved_gold"]["evidence_alternatives"][0]["requirements"]
    assert negative["at_k"] is None
    assert negative["resolved_gold"] is None
    assert negative["delivered"] is None
    assert asdict(service.settings) == original


def test_bootstrap_resamples_groups_deterministically():
    rows = [
        {"group_id": "a", "score": 1},
        {"group_id": "a", "score": 1},
        {"group_id": "b", "score": 0},
    ]
    result = bootstrap_groups(rows, "score", samples=100)
    assert result == bootstrap_groups(rows, "score", samples=100)
    assert result["groups"] == 2
    assert result["mean"] == pytest.approx(2 / 3)


def test_candidate_holdout_is_denied_before_any_model_or_run_creation(frozen, monkeypatch):
    from pathlib import Path
    from types import SimpleNamespace

    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / "scripts"))
    import benchmark_official as runner

    root, dataset, _, _ = frozen
    monkeypatch.setattr(runner, "ROOT", root)
    monkeypatch.setattr(runner, "implementation_hash", lambda: "fixture")
    monkeypatch.setattr(
        runner,
        "validate_dataset",
        lambda path, base, formal: validate_dataset(path, base, formal=formal, full_size=False),
    )
    protocol = root / "protocol.json"
    write_new(
        protocol,
        {
            "dataset": str(dataset),
            "diagnostic": True,
            "implementation_sha256": "fixture",
            "dataset_manifest_sha256": digest(dataset / "dataset-manifest.json"),
            "corpus_manifest_sha256": digest(dataset / "corpus-manifest.json"),
        },
    )
    args = SimpleNamespace(
        protocol=protocol, split="holdout", output=root / "forbidden", limit=None, variant=None
    )
    with pytest.raises(ValueError, match="cannot evaluate holdout"):
        runner.run(args)
    assert not args.output.exists()


def test_near_duplicate_queries_cannot_cross_splits(frozen):
    root, dataset, _, splits = frozen
    shared = "在同一模型同一硬件同一配置条件下，需要依照固定版本文档确认前缀缓存的作用与适用限制"
    splits["dev"][0]["query"] = shared + "？"
    splits["holdout"][0]["query"] = shared + "吗？"
    replace_questions(dataset, splits)
    with pytest.raises(ValueError, match="near-duplicate"):
        validate_dataset(dataset, root, full_size=False)


@pytest.mark.parametrize("status", ["approved", "rejected", "disputed"])
def test_question_review_import_preserves_all_decisions_and_original_ledger(
    frozen, monkeypatch, status
):
    from pathlib import Path
    from types import SimpleNamespace

    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / "scripts"))
    import build_official_dataset as builder

    root, dataset, _, splits = frozen
    monkeypatch.setattr(builder, "ROOT", root)
    for questions in splits.values():
        for question in questions:
            question["conditions"] = {"release": "fixture"}
    replace_questions(dataset, splits)
    monkeypatch.setattr(
        builder,
        "validate_dataset",
        lambda path, base: validate_dataset(path, base, full_size=False),
    )
    ledger = builder.question_review_template([q for rows in splits.values() for q in rows])
    ledger[0].update(
        status=status,
        reviewer="fixture reviewer",
        reviewed_at="2026-10-01T00:00:00Z",
        notes="Fixture decision; not approval of project candidates",
    )
    reviews = root / "reviews.json"
    write_new(reviews, ledger)
    output = dataset.with_name("reviewed")
    builder.review(SimpleNamespace(dataset=dataset, output=output, reviews=reviews))
    _, imported = validate_dataset(output, root, full_size=False)
    assert imported["dev"][0]["review"]["status"] == status
    assert imported["dev"][0]["review"]["notes"] == ledger[0]["notes"]
    assert imported["holdout"][0]["review"]["status"] == "pending"
    assert (output / "imported-question-review.json").read_bytes() == reviews.read_bytes()
    assert json.loads((output / "question-review.json").read_text()) == ledger
    assert json.loads((output / "dataset-manifest.json").read_text())[
        "imported_reviews_sha256"
    ] == (digest(output / "imported-question-review.json"))
