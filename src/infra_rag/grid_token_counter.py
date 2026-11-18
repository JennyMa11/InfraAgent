"""Exact memoization for a verified BERT WordPiece tokenizer, quality replay only."""

import json
from functools import lru_cache


def quality_counter(tokenizer):
    """BertPreTokenizer separates whitespace, so blank-line blocks are independent.

    Fail closed to ordinary whole-string counting for other tokenizer recipes or
    added tokens that could span the separator. No truncation/padding state is changed.
    The timed production path must continue to use the ordinary encoder counter.
    """
    backend = getattr(tokenizer, "backend_tokenizer", None)
    if backend is None:
        backend = getattr(tokenizer, "_tokenizer", None)
    config = json.loads(backend.to_str()) if backend is not None else {}
    additive = (
        config.get("model", {}).get("type") == "WordPiece"
        and config.get("pre_tokenizer", {}).get("type") == "BertPreTokenizer"
        and config.get("normalizer", {}).get("type") == "BertNormalizer"
        and not any("\n\n" in t["content"] for t in config.get("added_tokens", []))
    )

    @lru_cache(maxsize=32768)
    def block(text):
        return len(tokenizer.encode(text, add_special_tokens=False))

    @lru_cache(maxsize=4096)
    def count(text):
        return sum(block(part) for part in text.split("\n\n")) if additive else block(text)

    count.method = "bert-blankline-additive-memoized" if additive else "whole-string-memoized"
    return count
