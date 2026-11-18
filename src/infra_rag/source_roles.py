"""Conservative document-role separation; path role is not factual authority."""

import re
from pathlib import PurePosixPath

VERSION = "source-roles-v1"


def source_role(path, text="", source_type=None):
    lower = path.casefold()
    parts = PurePosixPath(lower).parts
    base = parts[-1]
    if any(p in {"interview", "interviews", "evals", "evaluations"} for p in parts) or re.search(
        r"面试|interview_qa", lower
    ):
        return "interview_or_evaluation", "explicit interview/evaluation path"
    if any(p in {"calculations", "experiments", "results"} for p in parts):
        return "experiment_or_calculation", "calculation/experiment output tree"
    if (
        re.search(
            r"editorial|revision|outline.check|审稿|修订|改写|写作|提纲|paper_skeleton|paper_writing",
            base,
        )
        or "reviews" in parts
    ):
        return "editorial_record", "editorial/revision/review/planning artifact"
    if any(p in {"archive", "draft", "drafts"} for p in parts) or re.search(
        r"(?:^|[-_])draft(?:[-_.]|$)|草稿", base
    ):
        return "draft_or_archive", "explicit archive/draft marker"
    if any(p.startswith("book-") and p != "book-zh" for p in parts) or "translations" in parts:
        return "translation_pending_review", "translation kept separate from canonical source"
    if "case-studies" in parts or re.search(
        r"教学模型|教学输入|不是训练平台实测|算子计数", text[:5000]
    ):
        return (
            "teaching_or_case_reference",
            "teaching/derived calculation/case material, not a measured product claim",
        )
    if "source-snapshots" in parts or "references" in parts or "research" in parts:
        return "reference_snapshot", "archived reference or research material"
    if base in {"readme.md", "index.md"} or re.search(r"目录|sources_overview", base):
        return "navigation_or_overview", "overview is reviewed separately, not dropped by length"
    if source_type in {"issue", "pull_request"} or re.search(r"(?:issue|pr)-\d+", base):
        return (
            "primary_issue_or_pr",
            "issue/PR snapshot, distinct from released product documentation",
        )
    if (
        lower.startswith(
            (
                "docs/guides/",
                "docs/posts/",
                "docs/source/",
                "docs/user_guide/",
                "docs/user-guide/",
                "doc/source/",
                "infra/handbook/",
                "src/content/blog/",
            )
        )
        or re.fullmatch(r"manuscripts/\d{2}-[^/]+\.md", lower)
        or lower == "infra/inference_accel_handbook_zh.md"
        or source_type in {"cuda_documentation", "documentation"}
    ):
        return (
            "technical_body_candidate",
            "recognized technical body path; not independent factual approval",
        )
    if lower.startswith("cuda-"):
        return "technical_body_candidate", "frozen CUDA documentation section"
    return "uncertain", "no safe canonical-body rule"
