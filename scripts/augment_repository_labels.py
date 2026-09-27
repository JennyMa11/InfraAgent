"""Version explicitly adjudicated source evidence without altering the original benchmark."""

import hashlib
import json
import os

from index_repository_corpus import DATASET, ROOT
from operation_log import record_operation


def compact_with_positions(text):
    positions = [i for i, char in enumerate(text) if not char.isspace()]
    return "".join(text[i] for i in positions), positions


def build():
    manifest = json.loads((DATASET / "corpus-manifest.json").read_text())
    corpus = ROOT / manifest["corpus_root"]
    documents = {d["id"]: d for d in manifest["documents"]}
    decisions = json.loads((DATASET / "equivalent-evidence-decisions.json").read_text())
    output = DATASET / "annotations-v2"
    output.mkdir(exist_ok=True)
    questions = {}
    original_hashes = {}
    for split in ["dev", "test"]:
        file = DATASET / f"{split}.json"
        original_hashes[split] = hashlib.sha256(file.read_bytes()).hexdigest()
        questions[split] = json.loads(file.read_text())
        for q in questions[split]:
            for span in q["relevant_spans"]:
                span["source"] = os.path.relpath((DATASET / span["source"]).resolve(), output)
            q["evidence_alternatives"] = [{"id": "original", "spans": q["relevant_spans"]}]
    by_id = {q["id"]: q for items in questions.values() for q in items}
    ledger = []
    for number, decision in enumerate(decisions, 1):
        doc = documents[decision["document_id"]]
        source = corpus / doc["source"]
        raw = source.read_text()
        assert hashlib.sha256(source.read_bytes()).hexdigest() == doc["sha256"]
        spans = []
        for quote, (first_line, last_line) in zip(
            decision["quotes"], decision["quote_line_ranges"], strict=True
        ):
            lines = raw.splitlines(keepends=True)
            offset = sum(len(line) for line in lines[: first_line - 1])
            region = "".join(lines[first_line - 1 : last_line])
            normalized, positions = compact_with_positions(region)
            needle, _ = compact_with_positions(quote)
            within = normalized.find(needle)
            if within < 0 or len(needle) < 20:
                raise ValueError(f"quote not supported by adjudicated candidate: {quote}")
            start = offset + positions[within]
            end = offset + positions[within + len(needle) - 1] + 1
            first = raw.count("\n", 0, start) + 1
            last = raw.count("\n", 0, end - 1) + 1
            spans.append(
                {
                    "source": os.path.relpath(source, output),
                    "text": raw[start:end],
                    "repository": doc["repository"],
                    "commit": doc["commit"],
                    "document_id": doc["id"],
                    "sha256": doc["sha256"],
                    "line_start": first,
                    "line_end": last,
                    "source_url": f"{doc['url']}#L{first}-L{last}",
                }
            )
        for question_id in decision["questions"]:
            q = by_id[question_id]
            q["evidence_alternatives"].append(
                {
                    "id": f"equivalent-{number:03d}",
                    "spans": spans,
                    "reason": decision["reason"],
                    "reviewer": "AI source-content adjudication",
                    "review_status": "pending_independent_human_review",
                }
            )
            q["relevant_spans"] = [*q["relevant_spans"], *spans]
        ledger.append({**decision, "spans": spans, "reviewer": "AI", "decision": "accept"})
    for split, items in questions.items():
        (output / f"{split}.json").write_text(json.dumps(items, ensure_ascii=False, indent=2))
    (output / "adjudication-ledger.json").write_text(
        json.dumps(ledger, ensure_ascii=False, indent=2)
    )
    record = {
        "version": "infra-repos-v1-equivalent-v2",
        "corpus_sha256": manifest["corpus_sha256"],
        "original_dataset_sha256": original_hashes,
        "annotation_method": "explicit AI source-content judgments; pending human verification",
        "scope": "known equivalent evidence corrections; not exhaustive corpus relevance",
        "protocol": "fixed query IDs, queries and concept splits; original evidence retained",
        "decisions": len(decisions),
        "splits": {
            split: {
                "questions": len(items),
                "augmented_questions": sum(len(q["evidence_alternatives"]) > 1 for q in items),
                "sha256": hashlib.sha256((output / f"{split}.json").read_bytes()).hexdigest(),
            }
            for split, items in questions.items()
        },
    }
    (output / "manifest.json").write_text(json.dumps(record, ensure_ascii=False, indent=2))
    record_operation(
        "生成等价证据标注v2",
        "补正已核查的等价原文，保留原始版本与分组",
        json.dumps(record, ensure_ascii=False),
    )
    print(json.dumps(record, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        build()
    except Exception as error:
        record_operation("生成等价证据标注v2", "版本化补充正确证据", "未完成", repr(error))
        raise
