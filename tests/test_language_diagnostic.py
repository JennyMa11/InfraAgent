"""Identity, failure denominators and conservative source separation."""

import copy

import pytest

from infra_rag.language_diagnostic import FIELDS, schedule, summarize, validate_pairs
from infra_rag.source_roles import source_role


@pytest.mark.parametrize(
    ("path", "text", "expected"),
    [
        ("manuscripts/ch04/editorial-revision.md", "", "editorial_record"),
        ("docs/source/drafts/api.md", "", "draft_or_archive"),
        ("docs/source/api.md", "", "technical_body_candidate"),
        ("README.md", "", "navigation_or_overview"),
        ("manuscripts/ch03/source-snapshots/case-studies/x.md", "", "teaching_or_case_reference"),
        ("manuscripts/03-attention.md", "教学模型", "teaching_or_case_reference"),
        ("book-en/chapter.md", "", "translation_pending_review"),
        ("docs/guides/interviews/x.md", "", "interview_or_evaluation"),
        ("other.md", "", "uncertain"),
    ],
)
def test_roles_precede_formal_body_allowlist(path, text, expected):
    assert source_role(path, text)[0] == expected


def cases():
    return [
        {"id": f"q{i}", "query": f"中文{i}", "query_en": f"English{i}", "group_id": "shared"}
        for i in range(2)
    ]


def test_bilingual_pairs_preserve_original_and_reject_missing_translations():
    original = cases()
    validate_pairs(cases(), original)
    for field, value in [("query", "changed"), ("group_id", "other"), ("query_en", " ")]:
        edited = cases()
        edited[0][field] = value
        with pytest.raises(ValueError):
            validate_pairs(edited, original)
    with pytest.raises(ValueError, match="duplicate"):
        validate_pairs([original[0], original[0]], original)


def rows_for_cases():
    by_id = {c["id"]: c for c in cases()}
    return [
        {
            **entry,
            "query": by_id[entry["id"]]["query" if entry["query_language"] == "zh" else "query_en"],
            "group_id": "shared",
            "status": "completed",
            "source_language": "en",
            "source_role": "technical_body_candidate",
            "kind": "single_document",
            **{f: {"complete": entry["query_language"] == "en"} for f in FIELDS},
        }
        for entry in schedule(cases())
    ]


def test_schedule_is_complete_and_alternates_order():
    plan = schedule(cases())
    assert len(plan) == 12
    assert [r["query_language"] for r in plan[:2]] == ["zh", "en"]
    assert [r["query_language"] for r in plan[6:8]] == ["en", "zh"]


def test_paired_stats_keep_failed_runs_and_source_clusters():
    rows = rows_for_cases()
    # Failed run has no score and remains in denominator.
    failed = next(r for r in rows if r["arm"] == "bm25" and r["query_language"] == "en")
    failed["status"] = "failed"
    for field in FIELDS:
        failed.pop(field)
    result = summarize(rows, cases())
    bm = result["results"]["bm25"]["en"]
    assert bm["first_page"] == {"numerator": 1, "denominator": 2, "value": 0.5}
    assert bm["failures"] == 1
    comparison = result["paired_comparisons"]["bm25:first_page"]
    assert comparison["n"] == 2
    assert comparison["clusters"] == 1
    assert comparison["delta_count"] == 1
    assert comparison["recovered_ids"] == ["q1"]
    assert len(result["paired_comparisons"]) == 6


def test_summary_rejects_missing_duplicate_and_changed_queries():
    rows = rows_for_cases()
    for altered in (rows[:-1], rows[:-1] + [rows[0]]):
        with pytest.raises(ValueError, match="outputs"):
            summarize(altered, cases())
    altered = copy.deepcopy(rows)
    altered[0]["query"] = "expanded with answer"
    with pytest.raises(ValueError, match="identity"):
        summarize(altered, cases())
