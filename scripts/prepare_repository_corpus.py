"""Fetch pinned public repositories and materialize only canonical Infra text documents."""

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "evals" / "repository-benchmark"
CORPUS = ROOT / "data" / "datasets" / "infra-repos-v1" / "corpus"
REPOSITORIES = [
    {
        "id": "AIInfraGuide",
        "url": "https://github.com/caomaolufei/AIInfraGuide",
        "commit": "a3b63eeb81d6d36a3c42c8cfc5a1bdd96e36bab1",
        "license": "not_found_at_root",
    },
    {
        "id": "JennyMa11.github.io",
        "url": "https://github.com/JennyMa11/JennyMa11.github.io",
        "commit": "188467456afaff48887869462951a1b5457c0387",
        "license": "not_found_at_root",
    },
    {
        "id": "ai-infra-book",
        "url": "https://github.com/bojieli/ai-infra-book",
        "commit": "56ecb425b07ea6d16e891cba87bf7db416927d09",
        "license": "Apache-2.0",
    },
]


def git(directory, *args, binary=False):
    result = subprocess.check_output(["git", "-C", str(directory), *args])
    return result if binary else result.decode("utf-8").strip()


def eligible(repo_id, path):
    if repo_id == "AIInfraGuide":
        return path.startswith("docs/guides/") and path.endswith(".md")
    if repo_id == "JennyMa11.github.io":
        return path == "infra/inference_accel_handbook_zh.md" or path in {
            "src/content/blog/attention-is-all-you-need-explained.mdx",
            "src/content/blog/multi-head-attention-intuition.mdx",
            "src/content/blog/transformer-positional-encoding.mdx",
            "src/content/blog/speculative-decoding-methods.mdx",
        }
    return bool(re.fullmatch(r"manuscripts/(?:0[1-9]|1[0-2])-[^/]+\.md", path))


def normalize_document(text):
    """Keep source line positions; blank frontmatter/navigation/render-only syntax."""
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for index in range(1, len(lines)):
            if lines[index].strip() == "---":
                lines[: index + 1] = [""] * (index + 1)
                break
    in_fence, in_toc = False, False
    for index, line in enumerate(lines):
        if line.strip().startswith("```"):
            in_fence = not in_fence
        if in_fence:
            continue
        if re.match(r"^#{1,6}\s+", line):
            in_toc = bool(
                re.match(r"^#{1,6}\s+(?:📑\s*)?(?:目录|Table of Contents)\s*$", line, re.I)
            )
        if in_toc or re.match(r"^\s*(?:import |export |<!--.*-->\s*$)", line):
            lines[index] = ""
        elif "<img" in line:
            alt = re.search(r'alt="([^"]+)"', line)
            lines[index] = "[图示说明] " + alt[1] if alt else ""
    return "\n".join(lines) + "\n"


def materialize(fetch=True):
    DATASET.mkdir(parents=True, exist_ok=True)
    CORPUS.mkdir(parents=True, exist_ok=True)
    documents, excluded, seen = [], [], {}
    for repo in REPOSITORIES:
        directory = ROOT / "data" / "upstream" / repo["id"]
        if not directory.exists():
            if not fetch:
                raise ValueError(f"missing repository: {directory}")
            directory.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(
                [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    "--filter=blob:none",
                    "--no-checkout",
                    repo["url"] + ".git",
                    str(directory),
                ],
                check=True,
            )
        try:
            git(directory, "cat-file", "-e", repo["commit"] + "^{commit}")
        except subprocess.CalledProcessError:
            if not fetch:
                raise
            subprocess.run(
                ["git", "-C", str(directory), "fetch", "--depth", "1", "origin", repo["commit"]],
                check=True,
            )
        paths = git(directory, "ls-tree", "-rz", "--name-only", repo["commit"]).split("\0")
        selected = sorted(path for path in paths if eligible(repo["id"], path))
        for path in selected:
            raw = git(directory, "show", f"{repo['commit']}:{path}", binary=True)
            normalized = normalize_document(raw.decode("utf-8"))
            digest = hashlib.sha256(normalized.encode()).hexdigest()
            logical = repo["id"] + "/" + path
            if len(normalized.strip()) < 600:
                excluded.append({"document": logical, "reason": "short_navigation_or_stub"})
                continue
            if digest in seen:
                excluded.append(
                    {"document": logical, "reason": "exact_duplicate", "canonical": seen[digest]}
                )
                continue
            seen[digest] = logical
            target = CORPUS / logical
            if target.suffix == ".mdx":
                target = target.with_suffix(".md")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(normalized, encoding="utf-8")
            documents.append(
                {
                    "id": logical,
                    "repository": repo["id"],
                    "commit": repo["commit"],
                    "path": path,
                    "source": str(target.relative_to(CORPUS)),
                    "url": repo["url"] + "/blob/" + repo["commit"] + "/" + quote(path, safe="/"),
                    "raw_sha256": hashlib.sha256(raw).hexdigest(),
                    "sha256": digest,
                    "git_blob": git(directory, "rev-parse", f"{repo['commit']}:{path}"),
                    "characters": len(normalized),
                    "lines": len(normalized.splitlines()),
                    "license": repo["license"],
                }
            )
        print(
            repo["id"],
            len([d for d in documents if d["repository"] == repo["id"]]),
            "documents",
            flush=True,
        )
    manifest = {
        "version": "infra-repos-v1",
        "repositories": REPOSITORIES,
        "corpus_root": str(CORPUS.relative_to(ROOT)),
        "normalization": "line-preserving frontmatter/toc/render-tag cleanup v1",
        "documents": documents,
        "excluded": excluded,
        "corpus_sha256": hashlib.sha256(json.dumps(documents, sort_keys=True).encode()).hexdigest(),
        "scope": "canonical text; excludes interview questions, drafts, translations, experiments",
    }
    (DATASET / "corpus-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2)
    )
    print(
        "Total", len(documents), "documents;", sum(d["characters"] for d in documents), "characters"
    )
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    materialize(fetch=not args.offline)
