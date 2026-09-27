"""Build source-grounded questions; evidence is fixed before retrieval is run."""

import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evals" / "repository-benchmark"


def build():
    manifest = json.loads((OUT / "corpus-manifest.json").read_text())
    seeds = json.loads((OUT / "question-seeds.json").read_text())
    corpus = ROOT / manifest["corpus_root"]
    groups = defaultdict(list)
    questions = []
    for i, seed in enumerate(seeds, 1):
        repo, filename, anchor, topic, answer, direct, scenario = seed[:7]
        documents = [
            d
            for d in manifest["documents"]
            if d["repository"] == repo and Path(d["path"]).name == filename
        ]
        if len(documents) != 1:
            raise ValueError(f"ambiguous source: {repo}/{filename}")
        document = documents[0]
        source = corpus / document["source"]
        text = source.read_text()
        if hashlib.sha256(source.read_bytes()).hexdigest() != document["sha256"]:
            raise ValueError(f"source changed: {source}")
        # Anchor selects an original paragraph, without consulting search results.
        paragraphs = list(re.finditer(r"\S[\s\S]*?(?=\n\s*\n|\Z)", text))
        candidates = [p for p in paragraphs if anchor in p.group()]
        if len(candidates) != 1:
            raise ValueError(f"ambiguous anchor: {filename}: {anchor}")
        match = candidates[0]
        evidence = match.group().rstrip()
        if len(evidence) > 440:
            raise ValueError(f"evidence exceeds chunk limit: {filename}: {anchor}")
        spans = []
        for support in seed[7] if len(seed) > 7 else [evidence]:
            if support not in evidence or len(support) < 20:
                raise ValueError(f"invalid support: {filename}: {support}")
            offset = match.start() + evidence.index(support)
            start = text.count("\n", 0, offset) + 1
            end = start + support.count("\n")
            spans.append(
                {
                    "source": "../../" + str(source.relative_to(ROOT)),
                    "text": support,
                    "repository": repo,
                    "commit": document["commit"],
                    "document_id": document["id"],
                    "sha256": document["sha256"],
                    "line_start": start,
                    "line_end": end,
                    "source_url": f"{document['url']}#L{start}-L{end}",
                }
            )
        for j, (kind, query) in enumerate([("knowledge", direct), ("scenario", scenario)], 1):
            item = {
                "id": f"repo-{i:03d}-{j}",
                "query": query,
                "domain": "infra",
                "modality": "text",
                "question_type": kind,
                "group_id": topic,
                "seed_id": f"seed-{i:03d}",
                "expected_answer": answer,
                "relevant_spans": spans,
                "reference_paragraph": evidence,
                "review_status": "pending_human_review",
                "annotation_method": "AI-authored against frozen source paragraphs",
            }
            questions.append(item)
            groups[topic].append(item)
    if len({q["query"] for q in questions}) != len(questions):
        raise ValueError("duplicate question")
    # Deterministic subset sum: whole concept groups go into exactly one split.
    target = 50
    reachable = {0: []}
    for group in sorted(groups, key=lambda x: hashlib.sha256(x.encode()).hexdigest()):
        weight = len(groups[group])
        for count, selection in list(reachable.items()):
            if count + weight <= target and count + weight not in reachable:
                reachable[count + weight] = selection + [group]
    dev_groups = set(reachable[target])
    splits = {
        "dev": [q for q in questions if q["group_id"] in dev_groups],
        "test": [q for q in questions if q["group_id"] not in dev_groups],
    }
    for name, items in splits.items():
        (OUT / f"{name}.json").write_text(json.dumps(items, ensure_ascii=False, indent=2))
    record = {
        "version": "infra-repos-v1",
        "corpus_sha256": manifest["corpus_sha256"],
        "questions": len(questions),
        "evidence_units": len(seeds),
        "concept_groups": len(groups),
        "split_policy": "sha256-ordered subset sum; concept groups remain in one split",
        "annotation": "AI source-grounded, not independently human verified",
        "qrels_scope": "authored evidence paragraphs; not exhaustive relevance judgments",
        "coverage": "text retrieval only; excludes visual understanding and generated answers",
        "splits": {
            name: {
                "questions": len(items),
                "groups": len({q["group_id"] for q in items}),
                "repositories": dict(Counter(q["relevant_spans"][0]["repository"] for q in items)),
                "sha256": hashlib.sha256((OUT / f"{name}.json").read_bytes()).hexdigest(),
            }
            for name, items in splits.items()
        },
    }
    (OUT / "dataset-manifest.json").write_text(json.dumps(record, ensure_ascii=False, indent=2))
    print(json.dumps(record, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    build()
