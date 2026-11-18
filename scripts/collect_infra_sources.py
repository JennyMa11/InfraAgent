"""Download a pinned official-document catalog without indexing or authoring questions."""

import argparse
import hashlib
import json
import re
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from urllib.parse import quote

from operation_log import ROOT, record_operation
from prepare_official_benchmark import markdown

from infra_rag.benchmarking import digest


def save_new(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != raw:
            raise ValueError(f"Existing snapshot differs: {path}")
    else:
        with path.open("xb") as stream:
            stream.write(raw)


def save_json(path, value):
    save_new(path, (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode())


def verify_blob(raw, expected):
    actual = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    if actual != expected:
        raise ValueError("Downloaded bytes do not match pinned Git blob")
    return actual


def validate_entry(repo, commit, path):
    if not re.fullmatch(r"[\w.-]+/[\w.-]+", repo):
        raise ValueError("Invalid repository")
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("Commit must be immutable full SHA")
    parts = PurePosixPath(path)
    if parts.is_absolute() or ".." in parts.parts or not path or "\\" in path:
        raise ValueError("Invalid repository path")


def fetch(repo, commit, entry, raw_root):
    path = entry["path"]
    validate_entry(repo, commit, path)
    url = f"https://raw.githubusercontent.com/{repo}/{commit}/{quote(path)}"
    target = raw_root / repo / path
    error = None
    for _attempt in range(2):
        try:
            if target.exists():
                raw = target.read_bytes()
            else:
                request = urllib.request.Request(
                    url, headers={"User-Agent": "InfraAgent-corpus/0.2"}
                )
                with urllib.request.urlopen(request, timeout=25) as response:
                    raw = response.read()
            verify_blob(raw, entry["blob_sha1"])
            save_new(target, raw)
            return raw, url
        except Exception as exc:
            error = exc
    raise RuntimeError(f"{repo}/{path}: {error}") from error


def shingles(text):
    words = re.findall(r"\w+", text.casefold())
    return {tuple(words[i : i + 5]) for i in range(max(0, len(words) - 4))}


def collect(catalog_path, output, data):
    catalog = json.loads(catalog_path.read_text())
    if (output / "corpus-manifest.json").exists():
        manifest = json.loads((output / "corpus-manifest.json").read_text())
        if manifest["catalog_sha256"] != digest(catalog_path):
            raise ValueError("Catalog changed; use a new batch")
        for doc in manifest["documents"]:
            for key, sha in (("raw_path", "raw_sha256"), ("corpus_path", "sha256")):
                if digest(ROOT / doc[key]) != doc[sha]:
                    raise ValueError(f"Frozen batch changed: {doc[key]}")
        print(f"Verified {len(manifest['documents'])} documents")
        return
    started = datetime.now(UTC).isoformat()
    old_hashes = {}
    for name in ("infra-official-v1-reviewed", "repository-benchmark"):
        path = ROOT / "evals" / name / "corpus-manifest.json"
        for doc in json.loads(path.read_text())["documents"]:
            old_hashes.setdefault(doc["sha256"], []).append(doc.get("id", doc["source"]))
    tasks = [(repo, entry) for repo in catalog["repositories"] for entry in repo["files"]]
    documents, exclusions, failures, licenses, seen = [], [], [], [], {}
    sets = {}

    def download(task):
        repo, entry = task
        try:
            raw, url = fetch(repo["repo"], repo["commit"], entry, data / "raw")
            return repo, entry, raw, url, None
        except Exception as exc:
            return repo, entry, None, None, str(exc)

    with ThreadPoolExecutor(max_workers=4) as pool:
        for repo, entry, raw, url, error in pool.map(download, tasks):
            if error:
                failures.append({"repo": repo["repo"], "path": entry["path"], "error": error})
                continue
            text, line_map = markdown(raw)
            sha = hashlib.sha256(text.encode()).hexdigest()
            identity = f"{repo['repo']}/{entry['path']}"
            duplicate = seen.get(sha) or old_hashes.get(sha)
            if len(text.strip()) < 600 or duplicate:
                exclusions.append(
                    {
                        "source": identity,
                        "duplicate_of": duplicate,
                        "reason": "exact_duplicate" if duplicate else "too_short",
                    }
                )
                continue
            target = data / "corpus" / repo["repo"] / entry["path"]
            save_new(target, text.encode())
            headings = [
                {"line": i, "text": line.strip()}
                for i, line in enumerate(text.splitlines(), 1)
                if re.match(r"^#{1,6}\s", line)
            ]
            documents.append(
                {
                    "id": hashlib.sha256(identity.encode()).hexdigest()[:24],
                    "repo": repo["repo"],
                    "commit": repo["commit"],
                    "version_kind": repo["version_kind"],
                    "source_path": entry["path"],
                    "source": target.relative_to(data / "corpus").as_posix(),
                    "source_url": f"https://github.com/{repo['repo']}/blob/{repo['commit']}/{entry['path']}",
                    "download_url": url,
                    "blob_sha1": entry["blob_sha1"],
                    "raw_path": str(
                        (data / "raw" / repo["repo"] / entry["path"]).relative_to(ROOT)
                    ),
                    "raw_sha256": hashlib.sha256(raw).hexdigest(),
                    "corpus_path": str(target.relative_to(ROOT)),
                    "sha256": sha,
                    "characters": len(text),
                    "lines": len(line_map),
                    "line_map": line_map,
                    "title": headings[0]["text"].lstrip("# ")
                    if headings
                    else Path(entry["path"]).stem,
                    "headings": headings,
                    "language": "en",
                    "review_status": "pending_human_review",
                    "image_reference_count": len(re.findall(r"!\[[^\]]*\]\(", text)),
                    "includes_unexpanded": bool(
                        re.search(r"(?:literalinclude|include)::|\{include\}", text)
                    ),
                    "modality": "source_text_only",
                    "downloaded_at": started,
                }
            )
            seen[sha] = identity
            sets[identity] = shingles(text)
            print("collected", len(documents), identity, flush=True)
    for repo in catalog["repositories"]:
        raw, url = fetch(repo["repo"], repo["commit"], repo["license"], data / "raw")
        licenses.append(
            {
                "repo": repo["repo"],
                "path": repo["license"]["path"],
                "url": url,
                "sha256": hashlib.sha256(raw).hexdigest(),
                "scope": "root license snapshot; per-file terms not independently reviewed",
            }
        )
    near = []
    items = list(sets.items())
    for i, (left, a) in enumerate(items):
        for right, b in items[i + 1 :]:
            score = len(a & b) / len(a | b) if a or b else 0
            if score >= 0.8:
                near.append({"left": left, "right": right, "jaccard": score})
    manifest = {
        "version": catalog["version"],
        "created_at": started,
        "catalog_sha256": digest(catalog_path),
        "collector_sha256": digest(Path(__file__)),
        "corpus_root": str((data / "corpus").relative_to(ROOT)),
        "documents": documents,
        "licenses": licenses,
        "exclusions": exclusions,
        "failed_downloads": failures,
        "near_duplicate_candidates": near,
        "dedup_scope": (
            "exact against two existing source manifests and batch; 5-word Jaccard within batch"
        ),
        "counts_by_repository": dict(Counter(d["repo"] for d in documents)),
        "total_characters": sum(d["characters"] for d in documents),
        "questions_authored": 0,
        "split": "unassigned",
        "indexed": False,
        "status": "partial" if failures else "collected_pending_review",
    }
    save_json(output / "corpus-manifest.json", manifest)
    save_json(
        output / "review-queue.json",
        [
            {
                "id": d["id"],
                "source_url": d["source_url"],
                "status": "pending",
                "checks": {
                    "technical_scope": None,
                    "standalone_evidence": None,
                    "image_dependencies": None,
                    "license_scope": None,
                },
            }
            for d in documents
        ],
    )
    save_new(output / "collector-snapshot.py", Path(__file__).read_bytes())
    lines = [
        "# AI Infra 首批候选语料",
        "",
        "官方项目固定commit快照，仅资料收集，尚未人工审核。",
        "",
        "|来源|文档数|",
        "|---|---:|",
    ]
    lines.extend(f"|{repo}|{n}|" for repo, n in manifest["counts_by_repository"].items())
    lines += [
        "",
        f"合计{len(documents)}份，{manifest['total_characters']:,}字符。",
        f"失败{len(failures)}份；排除{len(exclusions)}份；近重复候选{len(near)}对。",
        "",
        f"正文目录：`{manifest['corpus_root']}`。",
        "原始字节快照、Git blob SHA1及正文SHA256、提交和行号映射均已保存。",
        "Markdown仅将frontmatter置空以保留源行坐标；未翻译、未生成摘要或问题。",
        "图片与include依赖未下载/展开，引用数量与依赖标记供人工复核。",
        "根LICENSE快照保留；未完成逐文件授权审核。",
        "尚未指定dev/test、未读取旧holdout/test题目、未改现有语料或索引。",
        "下一步从review-queue.json审核正文独立性及场景覆盖，再编写和冻结评测证据。",
    ]
    save_new(output / "README.md", ("\n".join(lines) + "\n").encode())
    save_json(
        output / "artifacts-manifest.json",
        {
            str(p.relative_to(ROOT)): digest(p)
            for folder in (output, data)
            for p in sorted(folder.rglob("*"))
            if p.is_file() and p.name != "artifacts-manifest.json"
        },
    )
    record_operation(
        "收集AI Infra官方技术资料首批",
        "扩充独立来源并保留原文溯源，不生成评测题",
        f"{len(documents)}份；{manifest['total_characters']}字符；清单{output}",
        str(failures) if failures else "无；人工审核待完成，图片/include依赖未展开",
    )
    print(
        json.dumps(
            {
                "documents": len(documents),
                "characters": manifest["total_characters"],
                "failures": len(failures),
            },
            ensure_ascii=False,
        )
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--data", type=Path, required=True)
    args = parser.parse_args()
    collect(args.catalog.resolve(), args.output.resolve(), args.data.resolve())


if __name__ == "__main__":
    main()
