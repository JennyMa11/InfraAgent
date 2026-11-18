"""Snapshot integrity checks for the source-only collection tool."""

import hashlib
import runpy
from pathlib import Path

import pytest


@pytest.fixture
def collector(monkeypatch):
    scripts = Path(__file__).resolve().parents[1] / "scripts"
    monkeypatch.syspath_prepend(str(scripts))
    return runpy.run_path(str(scripts / "collect_infra_sources.py"))


def test_blob_integrity_rejects_different_bytes(collector):
    raw = b"official source\n"
    sha = hashlib.sha1(b"blob 16\0" + raw).hexdigest()
    assert collector["verify_blob"](raw, sha) == sha
    with pytest.raises(ValueError, match="pinned Git blob"):
        collector["verify_blob"](raw + b"changed", sha)


def test_snapshot_is_idempotent_but_never_overwrites(collector, tmp_path):
    path = tmp_path / "source.md"
    collector["save_new"](path, b"original")
    collector["save_new"](path, b"original")
    with pytest.raises(ValueError, match="differs"):
        collector["save_new"](path, b"replacement")
    assert path.read_bytes() == b"original"


def test_rejects_mutable_refs_and_path_escape(collector):
    validate = collector["validate_entry"]
    validate("official/repo", "a" * 40, "docs/guide.md")
    for commit, path in [
        ("main", "docs/guide.md"),
        ("a" * 40, "../outside"),
        ("a" * 40, "/absolute"),
    ]:
        with pytest.raises(ValueError):
            validate("official/repo", commit, path)


def test_frontmatter_normalization_keeps_source_lines_and_code(collector):
    raw = b"---\ntitle: example\n---\n# Guide\n```python\nprint(1)\n```\n"
    text, line_map = collector["markdown"](raw)
    assert text.splitlines()[3] == "# Guide"
    assert text.splitlines()[4:] == ["```python", "print(1)", "```"]
    assert line_map == list(range(1, 8))
