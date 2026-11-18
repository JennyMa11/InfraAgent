from infra_rag.preprocessing import clean_lines, units


def test_same_line_fence_does_not_swallow_following_code_or_prose():
    text = (
        "```log entry```\n\nexport navigation\n\n```\nimport torch\n```\n\n"
        "# Details\n\nConditions apply."
    )
    lines, changes = clean_lines(text)
    parsed = units(lines)
    assert [(u["start"], u["end"]) for u in parsed if u["kind"] == "code"] == [(1, 1), (5, 7)]
    assert lines[5] == "import torch" and lines[2] == ""
    assert changes == [{"line": 3, "reason": "render_only"}]
    assert parsed[-1]["content"] == "Conditions apply."


def test_fence_requires_matching_marker_and_length():
    text = "````python\n```\n~~~\nexport protected\n````\nexport navigation"
    lines, _ = clean_lines(text)
    assert lines[3] == "export protected" and lines[5] == ""
    code = units(lines)[0]
    assert code["start"] == 1 and code["end"] == 5


def test_real_source_regression_without_external_corpus_dependency():
    lines = [
        "```Decode batch. requests: 233```",
        "",
        "## KV pool",
        "",
        "```",
        "available_gpu_mem=13.50 GB",
        "```",
        "",
        "Use the observed free memory.",
    ]
    parsed = units(lines)
    assert [u["content"] for u in parsed if u["kind"] == "code"] == [
        lines[0],
        "\n".join(lines[4:7]),
    ]
    assert parsed[-1]["start"] == 9


def test_list_indented_fence_preserves_imports():
    lines, _ = clean_lines("1. Example\n\n    ```python\n    import torch\n    ```\n\nDone.")
    assert lines[3] == "    import torch"
    assert [(u["start"], u["end"]) for u in units(lines) if u["kind"] == "code"] == [(3, 5)]
