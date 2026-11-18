"""Regression checks for conservative, model-free corpus preparation."""

import copy

import pytest

from infra_rag.corpus_pilot import (
    QUOTAS,
    classify,
    duplicate_report,
    identity,
    prepare_document,
    select_pilot,
)


def test_unclosed_syntax_quarantines_without_changes():
    for text in ["---\ntitle: nope\n# Body", "```python\nprint(1)", "$$\nx=1"]:
        result = prepare_document(text.encode())
        assert result["status"] == "error"
        assert result["changes"] == []
        assert "text" not in result


def test_frontmatter_code_table_formula_and_mapped_positions():
    text = (
        "---\ntitle: example\n---\n# Memory\n\nOnly if enabled; not on older hardware.\n"
        "\n````python\nimport x\n```\n````\n\n| a | b |\n|---|---|\n| 1 | 2 |\n"
        "\n$$\nx = 2\n$$\n"
    )
    mapping = list(range(100, 100 + len(text.splitlines())))
    r = prepare_document(b"\xef\xbb\xbf" + text.replace("\n", "\r\n").encode(), mapping)
    assert r["status"] == "auto_pass"
    assert r["line_map"] == mapping
    assert r["normalization"]["bom_removed"]
    assert all(c["source_line"] == mapping[c["input_line"] - 1] for c in r["changes"])
    for unit in r["units"]:
        start, end = unit["input_lines"]
        assert unit["source_lines"] == mapping[start - 1 : end]
        if unit["kind"] in {"code", "table", "formula"}:
            assert unit["content"] == "\n".join(text.splitlines()[start - 1 : end])
            assert unit["description_unit"] is not None
    assert "not on older hardware" in r["text"]


def test_navigation_only_removed_if_entire_section_is_links():
    safe = "# Table of Contents\n- [A](#a)\n# A\ncontent\n"
    assert prepare_document(safe.encode())["text"].startswith("\n\n# A")
    unsafe = "# 目录\n- [A](#a)\n不能删除的重要条件。\n# A\n"
    assert "不能删除" in prepare_document(unsafe.encode())["text"]
    assert "# 目录" in prepare_document(unsafe.encode())["text"]


def test_dependencies_are_preserved_and_marked():
    text = "# Guide\n<Component x={1}/>\n![diagram](x.png)\n```{include} x.md\n```\n"
    r = prepare_document(text.encode())
    assert r["text"] == text
    assert r["status"] == "review"
    assert {"image_dependency", "include_dependency", "mdx_component"} <= set(r["features"])


def test_bad_mapping_and_decoding_are_not_silently_repaired():
    assert prepare_document(b"# A\nbody", [99])["status"] == "error"
    with pytest.raises(UnicodeDecodeError):
        prepare_document(b"\xff")


def test_classification_and_no_length_based_exclusion():
    assert classify("docs/interview/kv.md")[0] == "exclude"
    assert classify("calculations/results/run.md")[0] == "exclude"
    assert classify("book-en/kv.md")[0] == "review"
    assert classify("docs/guides/README.md")[0] == "review"
    assert classify("infra/handbook/ch01/small.md")[0] == "retain"
    assert classify("unknown.md")[0] == "review"


def test_selection_exact_quotas_order_independent_and_no_label_dependency():
    rows = []
    for collection, repos in QUOTAS.items():
        for repo, count in repos.items():
            for i in range(count + 2):
                rows.append(
                    {
                        "document_id": f"{collection}/{repo}/{i}",
                        "collection": collection,
                        "repository": repo,
                        "features": ["table"] if i == 0 else [],
                        "gold": "must not affect sampling",
                    }
                )
    before = copy.deepcopy(rows)
    a = select_pilot(rows)
    assert rows == before
    assert len(a) == len({r["document_id"] for r in a}) == 60
    assert a == select_pilot(list(reversed(rows)))
    for collection, repos in QUOTAS.items():
        for repo, count in repos.items():
            assert (
                sum(r["collection"] == collection and r["repository"] == repo for r in a) == count
            )


def test_identity_not_machine_path_and_versions_are_distinct():
    a = identity("x", "repo", "docs/a.md", "commit1", "hash")
    assert a == identity("x", "repo", "docs/a.md", "commit1", "hash")
    assert a != identity("x", "repo", "docs/a.md", "commit2", "hash")


def test_duplicate_audit_never_deletes_or_merges_unknown_versions():
    rows = [
        {
            "document_id": str(i),
            "input_sha256": "same",
            "repository": "repo",
            "release": version,
            "raw_sha256": "same",
            "whitespace_sha256": "same",
        }
        for i, version in enumerate(["v1", "v2", None, None])
    ]
    report = duplicate_report(rows, {"a": "technical body " * 20, "b": "technical body " * 20})
    assert report["same_known_version_alias_candidates"] == []
    assert report["deleted_documents"] == 0
    assert len(report["raw_exact"][0]) == 4
    assert report["near_pilot_only"][0]["jaccard"] == 1


def test_known_evaluation_hash_path_and_collection_are_blocked():
    from infra_rag.corpus_pilot import ensure_corpus_allowed

    row = {
        "collection": "official",
        "status": "retain",
        "input_sha256": "hash",
        "original_path": "data/body.md",
    }
    ensure_corpus_allowed(row)
    for hashes, paths in [({"hash"}, ()), ((), {"data/body.md"})]:
        with pytest.raises(ValueError, match="evaluation source"):
            ensure_corpus_allowed(row, hashes, paths)
    row["collection"] = "agent_fixture"
    with pytest.raises(ValueError):
        ensure_corpus_allowed(row)


def test_snapshot_save_rejects_mutation_and_process_continues_on_decode_failure(
    tmp_path, monkeypatch
):
    import runpy
    from pathlib import Path

    scripts = Path(__file__).resolve().parents[1] / "scripts"
    monkeypatch.syspath_prepend(str(scripts))
    runner = runpy.run_path(str(scripts / "prepare_corpus_pilot.py"))
    artifact = tmp_path / "frozen.json"
    runner["save"](artifact, {"frozen": True})
    runner["save"](artifact, {"frozen": True})
    with pytest.raises(ValueError, match="Frozen artifact changed"):
        runner["save"](artifact, {"frozen": False})
    body = tmp_path / "bad.md"
    body.write_bytes(b"\xff")
    result = runner["process"](
        {
            "input_path": str(body),
            "upstream_line_map": None,
            "document_id": "bad",
            "input_sha256": "hash",
            "coordinate_type": "source_markdown_lines",
        }
    )
    assert result["status"] == "error"
    assert result["errors"][0]["reason"] == "invalid_utf8"


def test_inline_triple_backticks_do_not_open_a_fence():
    body = (
        "```inline span``` followed by explanation.\n\n"
        "  ```version_policy: { all: {}}```\n\n"
        "```\nreal code\n```\n"
    )
    result = prepare_document(body.encode())
    assert result["status"] == "auto_pass"
    assert result["text"] == body
    assert sum(u["kind"] == "code" for u in result["units"]) == 1


def test_semantic_comments_and_unconfirmed_imports_are_preserved():
    body = '<!-- Only supported on H100; never on A100. -->\nimport Widget from "./x";\n'
    assert prepare_document(body.encode())["text"] == body
    mdx = prepare_document(body.encode(), mdx=True)
    assert "<!-- Only supported on H100; never on A100. -->" in mdx["text"]
    assert "import Widget" not in mdx["text"]
    assert prepare_document(b"<!-- TOC -->\n# Body\n")["text"].startswith("\n# Body")
