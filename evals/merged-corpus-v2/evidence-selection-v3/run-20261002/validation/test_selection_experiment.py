import importlib
import json
from pathlib import Path
from types import SimpleNamespace


def test_dev_setup_never_opens_confirmation_questions(tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / "scripts"))
    benchmark = importlib.import_module("benchmark_selection_v3")
    old = tmp_path / "old"
    old.mkdir()
    prepared = tmp_path / "prepared"
    prepared.mkdir()
    (prepared / "chunks.json").write_text("[]")
    manifest = {"chunks_sha256": benchmark.digest(prepared / "chunks.json")}
    (prepared / "manifest.json").write_text(json.dumps(manifest))
    official = tmp_path / "evals/infra-official-v1-reviewed"
    repository = tmp_path / "repository"
    official.mkdir(parents=True)
    repository.mkdir()
    q = {"id": "q1", "query": "question only"}
    for dataset in (official, repository):
        (dataset / "dev.json").write_text(json.dumps([q]))
    (official / "dataset-manifest.json").write_text(
        json.dumps({"splits": {"dev": {"sha256": benchmark.digest(official / "dev.json")}}})
    )
    (old / "protocol.json").write_text(
        json.dumps(
            {
                "directory": "prepared",
                "manifest_sha256": benchmark.digest(prepared / "manifest.json"),
                "official_dev_sha256": benchmark.digest(official / "dev.json"),
                "repo_dev_sha256": benchmark.digest(repository / "dev.json"),
                "generation_ids": [],
                "coverage_ids": [],
            }
        )
    )
    rows = [
        {
            "dataset": ds,
            "arm": arm,
            "query": q["query"],
            "diagnostics": {
                "final": [{"chunk_id": "c", "rerank_score": 0.8}],
                "candidates": ["c"],
            },
        }
        for ds in ("official", "repository")
        for arm in benchmark.POOL_ARMS.values()
    ]
    (old / "rows.jsonl").write_text("\n".join(json.dumps(r) for r in rows))
    (old / "models-verified.json").write_text("{}")
    plan = tmp_path / "plan.md"
    plan.write_text("frozen plan")
    script = tmp_path / "scripts/benchmark_selection_v3.py"
    script.parent.mkdir()
    script.write_text("# fixture")
    for name in ("benchmark_corpus_v2.py", "prepare_corpus_v2.py"):
        (script.parent / name).write_text("# fixture")
    monkeypatch.setattr(benchmark, "ROOT", tmp_path)
    monkeypatch.setattr(benchmark, "OLD", old)
    monkeypatch.setattr(benchmark, "PLAN", plan)
    monkeypatch.setattr(benchmark, "__file__", str(script))
    monkeypatch.setattr(benchmark, "client", lambda _: SimpleNamespace(configuration=lambda: {}))
    monkeypatch.setattr(benchmark, "repo_questions", lambda: (repository, [q]))
    monkeypatch.setattr(benchmark, "load_rewrites", lambda *args: {})
    original = Path.read_text

    def read(path, *args, **kwargs):
        assert path.name not in {"holdout.json", "test.json"}
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", read)
    _, datasets, bundles, _, _ = benchmark.prepare_run(tmp_path / "run")
    assert datasets["official"][1] == [q]
    assert "answer_key" not in bundles["official", "P0"][q["query"]]
    assert (tmp_path / "run/protocol.json").exists()
