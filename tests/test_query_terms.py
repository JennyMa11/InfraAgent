import pytest

from infra_rag.query_expansion import normalize_terms


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        ("Page Attention是什么", "PagedAttention是什么"),
        ("PageAttention是什么", "PagedAttention是什么"),
        ("paged attention 是什么？", "PagedAttention 是什么？"),
        ("PAGE\tATTENTION v0.10.2 --dtype=fp16", "PagedAttention v0.10.2 --dtype=fp16"),
        (
            "Page Attention 与 FlashAttention 有什么区别？",
            "PagedAttention 与 FlashAttention 有什么区别？",
        ),
    ],
)
def test_bounded_term_aliases_and_idempotence(query, expected):
    assert normalize_terms(query) == expected
    assert normalize_terms(expected) == expected


@pytest.mark.parametrize(
    "query",
    [
        "PagedAttention是什么",
        "FlashAttention是什么",
        "Attention 是什么",
        "Page Rank 是什么",
        "MyPageAttentionKernel PageAttentionCache",
        "lib.PageAttention PageAttention() PageAttention.md /docs/PageAttention",
        "https://example.test/PageAttention?q=PageAttention",
        "变量 `PageAttention` 不要改名",
        "```python\nclass PageAttention:\n    pass\n```",
        "```python\nPageAttention",
        "`PageAttention\nFlashAttention",
    ],
)
def test_alias_normalization_preserves_literals_and_other_mechanisms(query):
    assert normalize_terms(query) == query
