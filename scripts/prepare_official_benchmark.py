"""Freeze official sources, preserving raw snapshots and normalized-to-source line maps."""

import argparse
import hashlib
import json
import re
import urllib.request
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path

from operation_log import ROOT, record_operation

from infra_rag.benchmarking import canonical_hash, digest, load_json, write_new

DATASET = ROOT / "evals/infra-official-v1"
DATA = ROOT / "data/official-evals/infra-official-v1"
REPOS = {
    "vllm": ("vllm-project/vllm", "v0.10.2", "01efc7ef781391e744ed08c3292817a773d654e6"),
    "sglang": ("sgl-project/sglang", "v0.5.2", "b0d25e72c401f37b55d689ddbf05b8c583afe854"),
}
PATHS = {
    "vllm": [
        "features/automatic_prefix_caching.md",
        "design/prefix_caching.md",
        "design/paged_attention.md",
        "configuration/conserving_memory.md",
        "configuration/optimization.md",
        "features/quantization/fp8.md",
        "features/quantization/quantized_kvcache.md",
        "features/spec_decode.md",
        "features/sleep_mode.md",
        "features/disagg_prefill.md",
        "serving/parallelism_scaling.md",
        "serving/distributed_troubleshooting.md",
        "features/lora.md",
        "features/structured_outputs.md",
        "deployment/docker.md",
    ],
    "sglang": [
        "advanced_features/hyperparameter_tuning.md",
        "advanced_features/attention_backend.md",
        "advanced_features/quantization.md",
        "advanced_features/pd_disaggregation.md",
        "advanced_features/server_arguments.md",
        "advanced_features/router.md",
        "basic_usage/sampling_params.md",
        "references/faq.md",
        "references/environment_variables.md",
        "references/torch_compile_cache.md",
        "platforms/amd_gpu.md",
        "get_started/install.md",
    ],
}
CUDA_SECTIONS = [
    "thread-hierarchy",
    "memory-hierarchy",
    "device-memory",
    "shared-memory",
    "page-locked-host-memory",
    "asynchronous-concurrent-execution",
    "streams",
    "cuda-graphs",
    "unified-memory-programming",
    "maximize-utilization",
]
CUDA_URL = "https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html"


def download(url):
    request = urllib.request.Request(url, headers={"User-Agent": "InfraAgent-evaluation/0.2"})
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


class Sections(HTMLParser):
    """Extract selected Sphinx sections; skip navigation and preserve code text and HTML lines."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.rows = {name: [] for name in CUDA_SECTIONS}
        self.skip = 0
        self.buffer = ""
        self.buffer_section = None
        self.buffer_line = 1

    def flush(self):
        if self.buffer_section and self.buffer.strip():
            lines = self.buffer.strip("\n").splitlines()
            self.rows[self.buffer_section].extend(
                (line.rstrip(), self.buffer_line + i) for i, line in enumerate(lines)
            )
            self.rows[self.buffer_section].append(("", self.buffer_line))
        self.buffer = ""
        self.buffer_section = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "section":
            self.flush()
            self.stack.append(attrs.get("id"))
        if tag in {"p", "li", "pre", "tr", "h1", "h2", "h3", "h4", "h5", "h6"}:
            self.flush()
        if tag in {"script", "style"}:
            self.skip += 1

    def handle_endtag(self, tag):
        if tag == "section" and self.stack:
            self.flush()
            self.stack.pop()
        if tag in {"p", "li", "pre", "tr", "h1", "h2", "h3", "h4", "h5", "h6"}:
            self.flush()
        if tag in {"script", "style"}:
            self.skip = max(0, self.skip - 1)

    def handle_data(self, data):
        if self.skip or data.strip() == "":
            return
        section = next((s for s in reversed(self.stack) if s in CUDA_SECTIONS), None)
        if section:
            if self.buffer_section != section:
                self.flush()
                self.buffer_section, self.buffer_line = section, self.getpos()[0]
            self.buffer += data


def markdown(raw):
    # Blank rather than remove frontmatter/navigation, retaining line coordinates.
    lines = raw.decode("utf-8").splitlines()
    if lines and lines[0] == "---":
        end = next((i for i in range(1, len(lines)) if lines[i] == "---"), None)
        if end is not None:
            lines[: end + 1] = [""] * (end + 1)
    return "\n".join(lines) + "\n", list(range(1, len(lines) + 1))


def prepare():
    manifest_path = DATASET / "corpus-manifest.json"
    if manifest_path.exists():
        manifest = load_json(manifest_path)
        for doc in manifest["documents"]:
            for path_key, hash_key in (("raw_path", "raw_sha256"),):
                path = ROOT / doc[path_key]
                if not path.exists():
                    raw = download(doc["download_url"])
                    if hashlib.sha256(raw).hexdigest() != doc[hash_key]:
                        raise ValueError("upstream snapshot changed; preserve a new version")
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(raw)
            target = DATA / "corpus" / doc["source"]
            if not target.exists():
                raw = (ROOT / doc["raw_path"]).read_bytes()
                if doc["source_type"] == "cuda_documentation":
                    parser = Sections()
                    parser.feed(raw.decode())
                    text = "\n".join(row[0] for row in parser.rows[doc["section"]]) + "\n"
                elif doc["source_type"] == "pull_request":
                    obj = json.loads(raw)
                    text = "# " + obj["title"] + "\n\n" + (obj["body"] or "") + "\n"
                elif doc["source_type"] == "issue":
                    obj = json.loads(raw)
                    text = (
                        "# "
                        + obj["issue"]["title"]
                        + "\n\n"
                        + (obj["issue"]["body"] or "")
                        + "\n\n"
                        + "\n\n".join(c["body"] for c in obj["comments"])
                        + "\n"
                    )
                else:
                    text, _ = markdown(raw)
                if hashlib.sha256(text.encode()).hexdigest() != doc["sha256"]:
                    raise ValueError("normalization differs from frozen manifest")
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(text)
            if digest(target) != doc["sha256"]:
                raise ValueError("normalized source changed")
        print(f"Verified frozen corpus: {len(manifest['documents'])} documents")
        return

    docs, excluded, seen = [], [], {}
    DATA.mkdir(parents=True, exist_ok=True)

    def add(doc_id, raw, text, line_map, **metadata):
        sha = hashlib.sha256(text.encode()).hexdigest()
        if sha in seen:
            excluded.append({"id": doc_id, "duplicate_of": seen[sha]})
            return
        # Near-duplicate comparison uses 5-word shingles, without a heavy dependency.
        words = re.findall(r"\w+", text.casefold())
        shingles = {tuple(words[i : i + 5]) for i in range(max(0, len(words) - 4))}
        for prior in docs:
            previous = prior.pop("_shingles", None)
            if previous is not None:
                prior["_shingles"] = previous
                if shingles and len(shingles & previous) / len(shingles | previous) >= 0.95:
                    excluded.append({"id": doc_id, "near_duplicate_of": prior["id"]})
                    return
        raw_path = DATA / "raw" / (doc_id + ".snapshot")
        target = DATA / "corpus" / (doc_id + ".md")
        for path, value in ((raw_path, raw), (target, text.encode())):
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("xb") as stream:
                stream.write(value)
        docs.append(
            {
                "id": doc_id,
                "source": target.name,
                "raw_path": str(raw_path.relative_to(ROOT)),
                "sha256": sha,
                "raw_sha256": digest(raw_path),
                "line_map": line_map,
                "downloaded_at": datetime.now(UTC).isoformat(),
                "_shingles": shingles,
                **metadata,
            }
        )
        seen[sha] = doc_id
        print("Frozen", doc_id, flush=True)

    for project, paths in PATHS.items():
        repo, release, commit = REPOS[project]
        for path in paths:
            url = f"https://raw.githubusercontent.com/{repo}/{commit}/docs/{path}"
            raw = download(url)
            text, line_map = markdown(raw)
            doc_id = project + "-" + Path(path).stem
            add(
                doc_id,
                raw,
                text,
                line_map,
                project=project,
                source_type="documentation",
                release=release,
                commit=commit,
                download_url=url,
                url=f"https://github.com/{repo}/blob/{commit}/docs/{path}",
            )
    raw = download(CUDA_URL)
    parser = Sections()
    parser.feed(raw.decode("utf-8"))
    for section in CUDA_SECTIONS:
        rows = parser.rows[section]
        if not rows:
            raise ValueError(f"CUDA section not found: {section}")
        add(
            "cuda-" + section,
            raw,
            "\n".join(row[0] for row in rows) + "\n",
            [row[1] for row in rows],
            project="cuda",
            source_type="cuda_documentation",
            release="13.0.1",
            commit=None,
            section=section,
            download_url=CUDA_URL,
            url=CUDA_URL + "#" + section,
            line_coordinate="normalized text; line_map points to raw HTML lines",
        )
    for project, number in (("vllm", 21611), ("sglang", 2601)):
        repo = REPOS[project][0]
        url = f"https://api.github.com/repos/{repo}/pulls/{number}"
        raw = download(url)
        obj = json.loads(raw)
        if not obj.get("merged_at") or not obj.get("merge_commit_sha"):
            raise ValueError("PR must have an explicit merged fix")
        text = "# " + obj["title"] + "\n\n" + (obj["body"] or "") + "\n"
        add(
            f"{project}-pr-{number}",
            raw,
            text,
            [1] * len(text.splitlines()),
            project=project,
            source_type="pull_request",
            release="historical fix",
            commit=obj["merge_commit_sha"],
            download_url=url,
            url=obj["html_url"],
            merged_at=obj["merged_at"],
            line_coordinate="normalized PR snapshot",
            limitations="Merged PR description; deployment applicability requires review",
        )
    repo = REPOS["vllm"][0]
    issue_url = f"https://api.github.com/repos/{repo}/issues/21175"
    issue = json.loads(download(issue_url))
    # This specific issue is linked by merged fix PR 21611; closure alone is not a fix label.
    comments = []
    for page in range(1, 100):
        batch = json.loads(download(issue_url + f"/comments?per_page=100&page={page}"))
        comments.extend(batch)
        if len(batch) < 100:
            break
    raw = json.dumps(
        {"issue": issue, "comments": comments}, ensure_ascii=False, sort_keys=True
    ).encode()
    text = (
        "# "
        + issue["title"]
        + "\n\n"
        + (issue["body"] or "")
        + "\n\n"
        + ("\n\n".join(c["body"] for c in comments))
        + "\n"
    )
    add(
        "vllm-issue-21175",
        raw,
        text,
        [1] * len(text.splitlines()),
        project="vllm",
        source_type="issue",
        release="historical bug",
        commit=None,
        download_url=issue_url,
        url=issue["html_url"],
        fix_document_id="vllm-pr-21611",
        line_coordinate="normalized issue-and-comments snapshot",
        limitations="Mutable API source; exact restoration requires archived snapshot",
    )
    for doc in docs:
        doc.pop("_shingles", None)
    write_new(
        manifest_path,
        {
            "version": "infra-official-v1",
            "corpus_root": str((DATA / "corpus").relative_to(ROOT)),
            "documents": docs,
            "excluded": excluded,
            "corpus_sha256": canonical_hash([[doc["id"], doc["sha256"]] for doc in docs]),
            "annotation_method": "official frozen sources; not QA data",
        },
    )
    record_operation(
        "冻结官方技术语料",
        "为独立领域评测提供可追溯正文",
        f"{len(docs)}篇文档；未更改线上索引",
        "题集仍需独立人工审核",
    )


if __name__ == "__main__":
    argparse.ArgumentParser(description=__doc__).parse_args()
    prepare()
