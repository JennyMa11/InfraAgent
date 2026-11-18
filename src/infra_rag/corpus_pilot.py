"""Model-free, source-preserving document preparation; never used by serving code."""

import hashlib
import re
from collections import defaultdict

VERSION = "corpus-pilot-v1"
QUOTAS = {
    "official": {"vllm": 7, "sglang": 7, "cuda": 6},
    "repository": {"AIInfraGuide": 10, "JennyMa11.github.io": 5, "ai-infra-book": 5},
    "new_official": {
        "pytorch/pytorch": 4,
        "NVIDIA/TensorRT-LLM": 4,
        "triton-inference-server/server": 3,
        "NVIDIA/Megatron-LM": 3,
        "huggingface/accelerate": 3,
        "ray-project/ray": 3,
    },
}


def identity(collection, repo, path, commit, raw_hash):
    import json

    return hashlib.sha256(
        json.dumps([collection, repo, path, commit, raw_hash], ensure_ascii=False).encode()
    ).hexdigest()[:32]


def language(text):
    cjk = len(re.findall(r"[\u3400-\u9fff]", text))
    latin = len(re.findall(r"[a-zA-Z]", text))
    if cjk > 50 and latin > 50:
        return "mixed"
    return "zh" if cjk > 10 else "en" if latin > 10 else "unknown"


def classify(path):
    lower = path.casefold()
    parts = lower.split("/")
    if any(
        p
        in {
            "interview",
            "interviews",
            "evals",
            "evaluations",
            "experiments",
            "calculations",
            "reviews",
        }
        for p in parts
    ) or re.search(r"interview_qa|面试|评测问答", lower):
        return "exclude", "non_corpus", "interview_evaluation_or_generated_artifact"
    if any(
        p
        in {
            "archive",
            "draft",
            "drafts",
            "references",
            "research",
            "book-en",
            "book-zh-tw",
            "book-ru",
        }
        for p in parts
    ):
        return "review", "draft_translation_reference", "requires_document_review"
    if parts[-1] in {"readme.md", "index.md"} or re.search(r"目录|outline|附录.*资料", lower):
        return "review", "navigation_or_overview", "readme_or_directory_requires_review"
    if (
        lower.startswith(
            ("docs/guides/", "docs/posts/", "infra/handbook/", "manuscripts/", "src/content/blog/")
        )
        or lower == "infra/inference_accel_handbook_zh.md"
    ):
        return "retain", "candidate_technical_body", "candidate_body_path"
    return "review", "unclassified", "no_safe_automatic_role"


def protected_blocks(lines):
    """Return exact protected ranges; only standalone display-math delimiters are parsed."""
    blocks, errors = [], []
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        fence = re.match(r"^(`{3,}|~{3,})(.*)$", stripped)
        # Backticks in a backtick fence's info string make this an inline span.
        if fence and fence[1][0] == "`" and "`" in fence[2]:
            fence = None
        math = re.match(r"^\\begin\{(equation\*?|align\*?|gather\*?|displaymath)\}", stripped)
        if fence or stripped in {"$$", r"\["} or math:
            start = i
            if fence:
                marker = fence[1]

                def closer(s, marker=marker):
                    return bool(
                        re.fullmatch(
                            re.escape(marker[0]) + "{" + str(len(marker)) + r",}\s*", s.strip()
                        )
                    )

                kind = "code"
            else:
                end = r"\end{" + math[1] + "}" if math else "$$" if stripped == "$$" else r"\]"

                def closer(s, end=end):
                    return s.strip() == end

                kind = "formula"
            i += 1
            while i < len(lines) and not closer(lines[i]):
                i += 1
            if i == len(lines):
                errors.append({"reason": "unclosed_" + kind, "line": start + 1})
            else:
                i += 1
            blocks.append({"kind": kind, "start": start + 1, "end": i})
        elif (
            i + 1 < len(lines) and "|" in lines[i] and re.match(r"^\s*\|?\s*:?-{3,}", lines[i + 1])
        ):
            start = i
            i += 2
            while i < len(lines) and lines[i].strip() and "|" in lines[i]:
                i += 1
            blocks.append({"kind": "table", "start": start + 1, "end": i})
        else:
            i += 1
    return blocks, errors


def features(text, suffix=".md"):
    lines = text.splitlines()
    blocks, errors = protected_blocks(lines)
    flags = {b["kind"] for b in blocks}
    if suffix.casefold() == ".mdx" or re.search(r"<[A-Z][\w.]*\b", text):
        flags.add("mdx_component")
    if re.search(r"!\[.*?\]\(|<img\b|\{image\}|\.\. image::", text):
        flags.add("image_dependency")
    if re.search(r"(?:literalinclude|include)::|\{(?:literalinclude|include)\}", text):
        flags.add("include_dependency")
    if len(text) < 600:
        flags.add("short_document")
    if len(text) >= 20000:
        flags.add("long_document")
    flags.update(e["reason"] for e in errors)
    return sorted(flags)


def ensure_corpus_allowed(record, blocked_hashes=(), blocked_paths=()):
    if (
        record["collection"] not in QUOTAS
        or record.get("status") == "exclude"
        or record["input_sha256"] in blocked_hashes
        or record.get("original_path") in blocked_paths
    ):
        raise ValueError("Known non-corpus or evaluation source cannot enter pilot")


def select_pilot(records):
    chosen = []
    for collection, quotas in QUOTAS.items():
        for repo, count in quotas.items():
            pool = [r for r in records if r["collection"] == collection and r["repository"] == repo]
            covered = set()
            for _ in range(count):
                if not pool:
                    raise ValueError(f"Insufficient source quota: {collection}/{repo}")
                candidate = min(
                    pool,
                    key=lambda r: (
                        -len(set(r["features"]) - covered),
                        hashlib.sha256(("42:" + r["document_id"]).encode()).hexdigest(),
                    ),
                )
                chosen.append(candidate)
                covered.update(candidate["features"])
                pool.remove(candidate)
    return chosen


def prepare_document(raw, source_map=None, *, mdx=False):
    text = raw.decode("utf-8-sig", errors="strict")
    # split on line terminators only: do not reinterpret Unicode separators inside code.
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = text.split("\n")
    if lines[-1:] == [""]:
        lines.pop()
    blocks, errors = protected_blocks(lines)
    if lines and lines[0].strip() == "---":
        end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
        if end is None:
            errors.append({"reason": "unclosed_frontmatter", "line": 1})
    else:
        end = None
    if source_map is not None and len(source_map) != len(lines):
        errors.append({"reason": "source_map_length_mismatch", "line": None})
    if errors:
        return {"status": "error", "errors": errors, "changes": []}
    protected = {i for b in blocks for i in range(b["start"] - 1, b["end"])}
    changes, cleaned = [], list(lines)

    def blank(i, reason):
        if cleaned[i]:
            changes.append(
                {
                    "input_line": i + 1,
                    "source_line": (source_map or list(range(1, len(lines) + 1)))[i],
                    "before": lines[i],
                    "after": "",
                    "reason": reason,
                }
            )
            cleaned[i] = ""

    if end is not None:
        for i in range(end + 1):
            blank(i, "frontmatter")
    for i, line in enumerate(lines):
        if i in protected or end is not None and i <= end:
            continue
        heading = re.match(r"^(#{1,6})\s+(目录|Table of Contents)\s*$", line, re.I)
        if heading:
            last = next(
                (j for j in range(i + 1, len(lines)) if re.match(r"^#{1,6}\s", lines[j])),
                len(lines),
            )
            if all(
                not s.strip() or re.fullmatch(r"\s*(?:[-*+] |\d+\. )?\[[^\]]+\]\([^)]*\)\s*", s)
                for s in lines[i + 1 : last]
            ):
                for j in range(i, last):
                    if j not in protected:
                        blank(j, "navigation")
        elif (
            re.fullmatch(
                r"\s*<!--\s*(?:/?TOC|more|prettier-ignore|markdownlint-(?:disable|enable)[^>]*)\s*-->\s*",
                line,
                re.I,
            )
            or mdx
            and re.fullmatch(r"\s*import .+ from ['\"].+['\"];?\s*", line)
        ):
            blank(i, "render_only")
    for block in blocks:
        a, b = block["start"] - 1, block["end"]
        if lines[a:b] != cleaned[a:b]:
            raise ValueError("Protected content modified")
    mapping = source_map if source_map is not None else list(range(1, len(lines) + 1))
    structural, stack, previous = [], [], None
    starts = {b["start"] - 1: b for b in blocks}
    i = 0
    while i < len(cleaned):
        if not cleaned[i].strip():
            i += 1
            continue
        start = i
        heading = re.match(r"^(#{1,6})\s+(.+)", cleaned[i])
        if heading and i not in starts:
            level = len(heading[1])
            stack = [(n, t) for n, t in stack if n < level] + [(level, heading[2])]
            kind = "heading"
            i += 1
            previous = None
        elif i in starts:
            block = starts[i]
            kind, i = block["kind"], block["end"]
        else:
            i += 1
            while (
                i < len(cleaned)
                and cleaned[i].strip()
                and i not in starts
                and not re.match(r"^#{1,6}\s", cleaned[i])
            ):
                i += 1
            kind = (
                "condition"
                if re.search(
                    r"\b(?:if|unless|only|not|except|requires?)\b|如果|仅|不得|不能|不应|条件|限制",
                    "\n".join(cleaned[start:i]),
                    re.I,
                )
                else "paragraph"
            )
        unit = {
            "kind": kind,
            "input_lines": [start + 1, i],
            "source_lines": mapping[start:i],
            "heading_path": [t for _, t in stack],
            "content": "\n".join(cleaned[start:i]),
            "description_unit": previous if kind in {"code", "table", "formula"} else None,
        }
        structural.append(unit)
        if kind in {"paragraph", "condition"}:
            previous = len(structural) - 1
    output = "\n".join(cleaned) + ("\n" if lines else "")
    risks = features(text)
    removed = 1 - len(output) / max(1, len(text))
    if removed > 0.2:
        risks.append("length_reduction_over_20pct")
    return {
        "status": "review"
        if set(risks)
        & {"image_dependency", "include_dependency", "mdx_component", "length_reduction_over_20pct"}
        else "auto_pass",
        "errors": [],
        "text": output,
        "changes": changes,
        "line_map": mapping,
        "units": structural,
        "features": risks,
        "reduction_fraction": removed,
        "normalization": {
            "bom_removed": raw.startswith(b"\xef\xbb\xbf"),
            "crlf_count": raw.count(b"\r\n"),
            "cr_count": raw.count(b"\r"),
        },
    }


def duplicate_report(records, texts=None):
    groups = defaultdict(list)
    for row in records:
        groups[
            (row["input_sha256"], row["repository"], row["release"] or row["document_id"])
        ].append(row["document_id"])
    raw = defaultdict(list)
    normalized = defaultdict(list)
    for row in records:
        raw[row["raw_sha256"]].append(row["document_id"])
        normalized[row["whitespace_sha256"]].append(row["document_id"])
    near = []
    if texts:
        grams = {}
        for cid, text in texts.items():
            text = "".join(text.split())
            if len(text) >= 100:
                grams[cid] = {text[i : i + 20] for i in range(len(text) - 19)}
        for i, (left, a) in enumerate(grams.items()):
            for right, b in list(grams.items())[i + 1 :]:
                score = len(a & b) / max(1, len(a | b))
                if score >= 0.8:
                    near.append({"left": left, "right": right, "jaccard": score})
    return {
        "raw_exact": [v for v in raw.values() if len(v) > 1],
        "whitespace_exact": [v for v in normalized.values() if len(v) > 1],
        "same_known_version_alias_candidates": [v for v in groups.values() if len(v) > 1],
        "near_pilot_only": near,
        "deleted_documents": 0,
    }
