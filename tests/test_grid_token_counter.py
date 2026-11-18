import json

from infra_rag.grid_token_counter import quality_counter


class Tokenizer:
    def __init__(self, recipe):
        self.recipe = recipe
        self.backend_tokenizer = self
        self.calls = 0

    def to_str(self):
        return json.dumps(self.recipe)

    def encode(self, text, *, add_special_tokens):
        assert not add_special_tokens
        self.calls += 1
        return list(text.split())


def test_block_reuse_preserves_whitespace_counts():
    tokenizer = Tokenizer(
        {
            "model": {"type": "WordPiece"},
            "pre_tokenizer": {"type": "BertPreTokenizer"},
            "normalizer": {"type": "BertNormalizer"},
        }
    )
    count = quality_counter(tokenizer)
    assert count("First block\n\nSecond block") == 4
    before = tokenizer.calls
    assert count("First block\n\nDifferent block") == 4
    assert tokenizer.calls == before + 1
    assert count("\n\n\n\n") == 0


def test_unknown_tokenizer_and_separator_spanning_added_tokens_use_whole_string():
    for recipe in [
        {"model": {"type": "BPE"}},
        {
            "model": {"type": "WordPiece"},
            "pre_tokenizer": {"type": "BertPreTokenizer"},
            "normalizer": {"type": "BertNormalizer"},
            "added_tokens": [{"content": "a\n\nb"}],
        },
    ]:
        tokenizer = Tokenizer(recipe)
        count = quality_counter(tokenizer)
        assert count("one\n\ntwo") == 2
        assert count.method == "whole-string-memoized" and tokenizer.calls == 1
