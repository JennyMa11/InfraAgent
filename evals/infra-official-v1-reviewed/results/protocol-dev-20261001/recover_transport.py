"""Audit-only recovery of every failed HTTP call in the frozen full dev run.

Original rankings, outputs and failures remain immutable. No semantic result is retried.
This artifact is separate from the measured implementation and records post-run recovery.
"""
# ruff: noqa: E402
# This archived artifact resolves the repository scripts before importing their helpers.

import json
import sys
import urllib.error
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts"))

from benchmark_official import LocalClient, implementation_hash, ollama_identity, verify_snapshot
from operation_log import record_operation

from infra_rag.benchmarking import (
    canonical_hash,
    create_run,
    digest,
    human_summary,
    load_json,
    validate_dataset,
    write_new,
)
from infra_rag.config import Settings
from infra_rag.offline_evaluation import (
    answer_review_template,
    generate_answer,
    report_markdown,
    review_markdown,
    summarize,
)


class ErrorDetailsClient(LocalClient):
    def _request(self, payload):
        try:
            return super()._request(payload)
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {exc.code}: {body}") from exc


def main():
    protocol_path = Path(__file__).with_name("protocol.json")
    protocol = load_json(protocol_path)
    dataset = Path(protocol["dataset"])
    assert protocol["implementation_sha256"] == implementation_hash()
    assert digest(dataset / "dataset-manifest.json") == protocol["dataset_manifest_sha256"]
    assert digest(dataset / "corpus-manifest.json") == protocol["corpus_manifest_sha256"]
    for model in protocol["models"].values():
        verify_snapshot(model)
    _, splits = validate_dataset(dataset, ROOT, formal=True)
    primary = dataset / "results/dev-20261001"
    summary = load_json(primary / "summary.json")
    assert load_json(primary / "manifest.json")["protocol_sha256"] == digest(protocol_path)
    rows = [json.loads(line) for line in (primary / "rows.jsonl").read_text().splitlines()]
    expected = {(q["id"], v) for q in splits["dev"] for v in ["oracle", *protocol["variants"]]}
    assert len(rows) == len(expected) == 300
    assert {(r["id"], r["variant"]) for r in rows} == expected
    failures = [r for r in rows if r["generation"]["error"]]
    assert failures and all("HTTP Error 500" in r["generation"]["error"] for r in failures), (
        "Recovery is limited to recorded HTTP 500 failures, not semantic/format rejections"
    )
    identity = protocol["generation"]["identity"]
    assert ollama_identity(protocol["generation"]["base_url"], identity["model"]) == identity
    assert protocol["generation"]["options"] == {
        "temperature": 0,
        "num_predict": 650,
        "num_ctx": 8192,
    }
    client = ErrorDetailsClient(
        model=identity["model"], base_url=protocol["generation"]["base_url"]
    )
    settings = Settings(
        **protocol["settings"], data_dir=ROOT / "data/official-evals/recovery-unused"
    )
    questions = {q["id"]: q for q in splits["dev"]}
    source_hash = digest(primary / "rows.jsonl")
    output = create_run(
        dataset / "results/dev-20261001-transport-recovery",
        {
            "kind": "post_run_transport_recovery_view",
            "protocol_sha256": digest(protocol_path),
            "primary_run": str(primary.relative_to(ROOT)),
            "primary_rows_sha256": source_hash,
            "recovery_script_sha256": digest(Path(__file__)),
            "policy": "one replay of every original HTTP 500; no other outputs retried",
            "post_run_policy": True,
            "split": "dev",
            "diagnostic": False,
        },
    )
    with (output / "rows.jsonl").open("x", encoding="utf-8") as stream:
        for row in rows:
            if row["generation"]["error"]:
                original = row["generation"]
                question = questions[row["id"]]
                assert question["query"] == row["query"]
                recovered = generate_answer(question, row["context"], settings, client)
                assert recovered["calls"][0]["messages"] == original["calls"][0]["messages"]
                row["generation_attempts"] = [original, recovered]
                row["generation"] = recovered
                row["transport_recovery"] = {
                    "original_generation_sha256": canonical_hash(original),
                    "recovered_generation_sha256": canonical_hash(recovered),
                }
                print(
                    row["review_key"],
                    recovered["error"] or recovered["response"]["status"],
                    flush=True,
                )
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
            stream.flush()
    assert digest(primary / "rows.jsonl") == source_hash
    assert not settings.data_dir.exists()
    errors = sum(bool(r["generation"]["error"]) for r in rows)
    summary.update(
        status="human_reviewed_questions_with_post_run_transport_recovery",
        summaries=summarize(rows),
        by_type={
            kind: summarize([r for r in rows if r["question_type"] == kind])
            for kind in sorted({r["question_type"] for r in rows})
        },
        human_answers=human_summary(rows, []),
        recovery={
            "original_service_errors": len(failures),
            "replayed_keys": [r["review_key"] for r in failures],
            "remaining_service_errors": errors,
            "semantic_outputs_retried": 0,
            "timing_note": (
                "Latest-answer view combines the original run and post-run transport replays; "
                "not a single uninterrupted performance run"
            ),
        },
    )
    write_new(output / "summary.json", summary)
    write_new(output / "answer-review.json", answer_review_template(rows))
    for name, content in (
        ("answer-review.md", review_markdown(rows)),
        (
            "report.md",
            report_markdown(summary)
            + "\n\n原始服务错误与重放政策见summary.json的recovery；原始结果未覆盖。"
            "恢复视图不是一次连续性能运行。\n",
        ),
    ):
        with (output / name).open("x", encoding="utf-8") as stream:
            stream.write(content)
    write_new(
        output / "output-statuses.json",
        {
            v: dict(
                Counter(
                    (r["generation"]["response"] or {}).get("status", "error")
                    for r in rows
                    if r["variant"] == v
                )
            )
            for v in ["oracle", *protocol["variants"]]
        },
    )
    if not errors:
        write_new(
            protocol_path.parent / "dev-completed.json",
            {
                "protocol_sha256": digest(protocol_path),
                "run": str(output.resolve()),
                "summary_sha256": digest(output / "summary.json"),
                "completion_mode": "full_frozen_dev_plus_audited_transport_error_replays",
                "primary_rows_sha256": source_hash,
                "original_service_errors": len(failures),
                "human_answers_reviewed": 0,
            },
        )
    record_operation(
        "正式dev传输错误恢复",
        "只恢复主运行的HTTP500，不选择性重跑拒答或内容答案",
        f"原始{len(failures)}条服务错误；仅重放这些请求；恢复视图300条，剩余服务错误{errors}；保留全部原始尝试",
        "重放政策为运行后制定，延迟不是单次连续性能成绩；生成答案仍待人工审核，holdout未运行",
    )
    print(output, flush=True)


if __name__ == "__main__":
    main()
