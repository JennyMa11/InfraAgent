"""Frozen offline evaluation protocols; human labels are never inferred from model output."""

import hashlib
import json
import math
import random
import re
import statistics
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path

QUESTION_COUNTS = {
    "single_hop": 30,
    "conditional": 24,
    "code_api": 18,
    "debugging": 24,
    "multi_hop": 12,
    "unanswerable": 12,
}
VARIANTS = ("bm25", "dense", "hybrid", "hybrid_rerank")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_hash(value):
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True).encode()
    ).hexdigest()


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_new(path, value):
    """Never replace an existing frozen artifact, even with identical content."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def create_run(path, manifest):
    path = Path(path)
    path.mkdir(parents=True, exist_ok=False)
    write_new(path / "manifest.json", {"created_at": datetime.now(UTC).isoformat(), **manifest})
    return path


def normalized(text):
    return "".join(re.findall(r"\w+", text.casefold()))


def validate_dataset(dataset_dir, root, *, formal=False, full_size=True):
    dataset_dir, root = Path(dataset_dir), Path(root)
    manifest = load_json(dataset_dir / "corpus-manifest.json")
    record = load_json(dataset_dir / "dataset-manifest.json")
    if record["corpus_manifest_sha256"] != digest(dataset_dir / "corpus-manifest.json"):
        raise ValueError("corpus manifest changed")
    documents = {doc["id"]: doc for doc in manifest["documents"]}
    if len(documents) != len(manifest["documents"]):
        raise ValueError("duplicate document IDs")
    texts = {}
    corpus = (root / manifest["corpus_root"]).resolve()
    for doc in documents.values():
        path = (corpus / doc["source"]).resolve()
        if not path.is_relative_to(corpus) or digest(path) != doc["sha256"]:
            raise ValueError(f"changed or unsafe source: {doc['id']}")
        raw = (root / doc["raw_path"]).resolve()
        if not raw.is_relative_to(root / "data") or digest(raw) != doc["raw_sha256"]:
            raise ValueError(f"raw snapshot changed: {doc['id']}")
        if len(doc["line_map"]) != len(path.read_text().splitlines()):
            raise ValueError(f"invalid source line map: {doc['id']}")
        texts[doc["id"]] = path.read_text(encoding="utf-8")
    expected_files = {(corpus / doc["source"]).resolve() for doc in documents.values()}
    actual_files = {p.resolve() for p in corpus.rglob("*") if p.is_file()}
    if actual_files != expected_files:
        raise ValueError("corpus contains unlisted or missing files; ingest only frozen documents")
    splits, seen, groups, counts = {}, {}, {}, Counter()
    query_families = []
    for split in ("dev", "holdout"):
        file = dataset_dir / f"{split}.json"
        if digest(file) != record["splits"][split]["sha256"]:
            raise ValueError(f"{split} questions changed")
        questions = load_json(file)
        if len(questions) != record["splits"][split]["questions"]:
            raise ValueError("question count changed")
        splits[split] = questions
        for q in questions:
            query_key = normalized(q["query"])
            if len(query_key) < 8 or q["id"] in seen or query_key in seen:
                raise ValueError(f"empty or duplicate question: {q['id']}")
            shingles = {query_key[i : i + 6] for i in range(max(0, len(query_key) - 5))}
            for previous, previous_split in query_families:
                union = shingles | previous
                if (
                    union
                    and previous_split != split
                    and len(shingles & previous) / len(union) >= 0.9
                ):
                    raise ValueError("near-duplicate question crosses splits")
            query_families.append((shingles, split))
            seen[q["id"]] = seen[query_key] = split
            group = q["group_id"]
            if group in groups and groups[group] != split:
                raise ValueError(f"scenario group crosses splits: {group}")
            groups[group] = split
            if q["question_type"] not in QUESTION_COUNTS:
                raise ValueError("unknown question type")
            counts[q["question_type"]] += 1
            if not isinstance(q["answerable"], bool):
                raise ValueError("answerable must be boolean")
            if (q["question_type"] == "unanswerable") != (not q["answerable"]):
                raise ValueError("unanswerable type mismatch")
            review = q["review"]
            if review["status"] not in {"pending", "approved", "rejected", "disputed"}:
                raise ValueError("unknown review status")
            if review["status"] == "approved" and not (
                review.get("reviewer")
                and review.get("reviewed_at")
                and review.get("method") == "independent_human"
                and review.get("notes")
            ):
                raise ValueError("human approval requires named reviewer, time and notes")
            if formal and review["status"] != "approved":
                raise ValueError(f"independent review required: {q['id']}")
            if not q["answer_key"]["required_points"] or not q["answer_key"]["forbidden_claims"]:
                raise ValueError("answer rubric must include points and forbidden claims")
            alternatives = q["evidence_alternatives"]
            if not q["answerable"]:
                if alternatives or q["relevant_spans"] or not q.get("missing_information"):
                    raise ValueError("unanswerable requires missing-information rationale, no gold")
            elif not alternatives or any(not g["spans"] for g in alternatives):
                raise ValueError("answerable question requires nonempty evidence alternatives")
            spans = [s for g in alternatives for s in g["spans"]]
            if len({g["id"] for g in alternatives}) != len(alternatives):
                raise ValueError("duplicate alternative IDs")
            if {canonical_hash(s) for s in spans} != {
                canonical_hash(s) for s in q["relevant_spans"]
            }:
                raise ValueError("flat evidence and alternatives differ")
            for span in spans:
                doc = documents[span["document_id"]]
                text = texts[doc["id"]]
                first, last = span["line_start"], span["line_end"]
                if not (1 <= first <= last <= len(text.splitlines())):
                    raise ValueError("invalid evidence line range")
                located = "\n".join(text.splitlines()[first - 1 : last])
                source = (dataset_dir / span["source"]).resolve()
                if (
                    span["sha256"] != doc["sha256"]
                    or source != (corpus / doc["source"]).resolve()
                    or not span["text"].strip()
                    or span["text"] not in located
                ):
                    raise ValueError(f"invalid evidence: {q['id']}")
                key = canonical_hash([doc["id"], normalized(span["text"])])
                if key in seen and seen[key] != split:
                    raise ValueError("shared evidence crosses splits")
                seen[key] = split
            if q["question_type"] == "multi_hop" and (
                not q.get("reasoning_steps") or any(len(g["spans"]) < 2 for g in alternatives)
            ):
                raise ValueError("multi-hop requires intermediate steps and multiple spans")
            if any(q["query"] in text for text in texts.values()):
                raise ValueError("authored query leaked into corpus")
    if full_size:
        if counts != Counter(QUESTION_COUNTS) or len(groups) < 30:
            raise ValueError("expected 120 questions, specified type quotas and >=30 groups")
        for split, questions in splits.items():
            if len(questions) != 60 or sum(not q["answerable"] for q in questions) != 6:
                raise ValueError(f"expected 60 questions and 6 unanswerable in {split}")
    return manifest, splits


def graded_metrics(retrieved, qrels, k):
    """TREC-style document metrics, with linear relevance gains for nDCG (BEIR convention)."""
    if k < 1 or not qrels or any(not math.isfinite(v) or v < 0 for v in qrels.values()):
        raise ValueError("positive k and finite nonnegative qrels required")
    relevant = {doc for doc, value in qrels.items() if value > 0}
    if not relevant:
        raise ValueError("at least one positive judgment required")
    ids = list(dict.fromkeys(retrieved))[:k]
    hits = [doc in relevant for doc in ids]
    dcg = sum(qrels.get(doc, 0) / math.log2(i + 2) for i, doc in enumerate(ids))
    ideal = sum(
        v / math.log2(i + 2) for i, v in enumerate(sorted(qrels.values(), reverse=True)[:k])
    )
    return {
        "recall": sum(hits) / len(relevant),
        "precision": sum(hits) / k,
        "mrr": next((1 / (i + 1) for i, hit in enumerate(hits) if hit), 0.0),
        "ndcg": dcg / ideal,
    }


def span_coverage(evidence, question):
    """Check delivered text, including truncation; a retrieved ID alone is insufficient."""
    if not question["answerable"]:
        return None
    delivered_texts = [(row.get("source"), normalized(row["content"])) for row in evidence]
    for row in evidence:
        delivered_texts.extend(
            (alias["source"], normalized(row["content"]))
            for alias in row.get("metadata", {}).get("source_aliases", [])
        )
    parents = defaultdict(list)
    for row in evidence:
        if "source_position" in row:
            parents[(row.get("source"), row.get("parent_id"))].append(row)
    for (source, _), rows in parents.items():
        rows.sort(key=lambda row: row["source_position"])
        current, previous = "", None
        for row in rows:
            if previous is not None and row["source_position"] != previous + 1:
                delivered_texts.append((source, current))
                current = ""
            current += normalized(row["content"])
            previous = row["source_position"]
        delivered_texts.append((source, current))
    coverage = []
    for group in question["evidence_alternatives"]:
        found = sum(
            any(
                source == span["absolute_source"] and normalized(span["text"]) in text
                for source, text in delivered_texts
            )
            for span in group["spans"]
        )
        coverage.append(found / len(group["spans"]))
    return {"coverage": max(coverage), "complete": float(max(coverage) == 1)}


def automatic_answer_checks(raw, evidence):
    try:
        obj = json.loads(raw)
    except (ValueError, TypeError):
        obj = None
    fmt = bool(
        isinstance(obj, dict)
        and isinstance(obj.get("supported"), bool)
        and isinstance(obj.get("answer"), str)
        and obj["answer"].strip()
        and isinstance(obj.get("citations"), list)
        and all(isinstance(cid, str) for cid in obj["citations"])
    )
    allowed = {row["citation_id"] for row in evidence}
    cited = bool(fmt and obj["supported"] and obj["citations"] and set(obj["citations"]) <= allowed)
    if cited:
        mentioned = set(re.findall(r"\[(E[a-f0-9]{24})\]", obj["answer"]))
        cited = mentioned <= set(obj["citations"])
    return {
        "format_valid": fmt,
        "citation_ids_valid": cited,
        "refused": bool(fmt and not obj["supported"]),
        "parsed": obj if fmt else None,
        "fact_correct": None,
    }


def human_summary(rows, reviews):
    """Only explicit independent human judgments enter semantic metrics."""
    by_key = {row["review_key"]: row for row in rows}
    approved = []
    seen = set()
    for review in reviews:
        key = review["review_key"]
        if key not in by_key or key in seen:
            raise ValueError("unknown or duplicate answer review")
        seen.add(key)
        if review.get("status") != "approved":
            continue
        row = by_key[key]
        if (
            review.get("method") != "independent_human"
            or not review.get("reviewer")
            or not review.get("reviewed_at")
            or not review.get("notes")
            or review.get("answer_sha256") != canonical_hash(row["generation"])
        ):
            raise ValueError("answer review identity or hash mismatch")
        for field in ("fact_correct", "contradiction", "unsupported_claim", "refusal_appropriate"):
            if not isinstance(review.get(field), bool):
                raise ValueError(f"explicit boolean judgment required: {field}")
        if not (
            isinstance(review.get("points_total"), int)
            and isinstance(review.get("points_supported"), int)
            and review["points_total"] == len(row["required_points"])
            and 0 <= review["points_supported"] <= review["points_total"]
        ):
            raise ValueError("invalid required-point counts")
        claims, supported = review.get("citation_claims"), review.get("citation_supported")
        if (
            not isinstance(claims, int)
            or not isinstance(supported, int)
            or not 0 <= supported <= claims
        ):
            raise ValueError("invalid citation-support counts")
        if row["generation"].get("error"):
            raise ValueError("generation failures cannot be marked reviewed answers")
        approved.append((row, review))
    answered = [(row, rev) for row, rev in approved if row["answerable"]]
    negatives = [(row, rev) for row, rev in approved if not row["answerable"]]

    def mean(values):
        return statistics.mean(values) if values else None

    citation_total = sum(rev["citation_claims"] for _, rev in approved)
    return {
        "total_outputs": len(rows),
        "human_reviewed": len(approved),
        "review_coverage": len(approved) / len(rows) if rows else 0,
        "answer_correctness": mean([float(rev["fact_correct"]) for _, rev in answered]),
        "point_coverage": mean(
            [rev["points_supported"] / rev["points_total"] for _, rev in answered]
        ),
        "contradiction_rate": mean([float(rev["contradiction"]) for _, rev in approved]),
        "unsupported_claim_rate": mean([float(rev["unsupported_claim"]) for _, rev in approved]),
        "citation_support_rate": sum(rev["citation_supported"] for _, rev in approved)
        / citation_total
        if citation_total
        else None,
        "correct_refusal_rate": mean(
            [
                float(row["generation"]["checks"]["refused"] and rev["refusal_appropriate"])
                for row, rev in negatives
            ]
        ),
        "false_refusal_rate": mean(
            [float(row["generation"]["checks"]["refused"]) for row, _ in answered]
        ),
    }


def bootstrap_groups(rows, field, *, samples=2000, seed=42):
    groups = defaultdict(list)
    for row in rows:
        if row.get(field) is not None:
            groups[row["group_id"]].append(row[field])
    if not groups:
        return None
    values = list(groups.values())
    rng = random.Random(seed)
    means = sorted(
        statistics.mean([v for group in rng.choices(values, k=len(values)) for v in group])
        for _ in range(samples)
    )
    return {
        "mean": statistics.mean([v for group in values for v in group]),
        "ci95": [means[int(samples * 0.025)], means[min(samples - 1, int(samples * 0.975))]],
        "groups": len(groups),
        "samples": samples,
        "seed": seed,
    }
