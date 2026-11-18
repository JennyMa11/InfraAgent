import json

import pytest

from infra_rag.grid_packet_cache import PacketReranker


class Model:
    def __init__(self):
        self.calls = []

    def predict(self, pairs):
        self.calls.append(pairs)
        return [len(body) / 100 for _, body in pairs]


def test_exact_packets_reuse_but_order_and_model_identity_do_not(tmp_path):
    model = Model()
    cache = PacketReranker(model, tmp_path, {"weights": "a"})
    pairs = [("q", "first"), ("q", "second")]
    assert cache.predict(pairs) == [0.05, 0.06]
    assert cache.predict(pairs) == [0.05, 0.06] and len(model.calls) == 1
    assert cache.predict(pairs[::-1]) == [0.06, 0.05] and len(model.calls) == 2
    other = PacketReranker(model, tmp_path, {"weights": "b"})
    other.predict(pairs)
    assert len(model.calls) == 3


def test_timed_mode_never_uses_packet_results_and_logs_attempts(tmp_path):
    model = Model()
    cache = PacketReranker(model, tmp_path, {"weights": "a"})
    pairs = [("q", "body")]
    cache.seed(pairs, [0.9], {"source": "frozen"})
    cache.enabled = False
    assert cache.predict(pairs) == [0.04]
    assert cache.predict(pairs) == [0.04] and len(model.calls) == 2
    events = [json.loads(s) for s in (tmp_path / "events.jsonl").read_text().splitlines()]
    assert sum(e.get("actual_pairs", 0) for e in events) == 2
    assert all(e.get("cache_enabled") is False for e in events)


def test_invalid_or_corrupt_packets_and_pair_overflow_are_rejected(tmp_path):
    cache = PacketReranker(Model(), tmp_path, {"weights": "a"})
    with pytest.raises(ValueError, match="Invalid"):
        cache.seed([("q", "x")], [float("nan")], {})
    with pytest.raises(ValueError, match="90"):
        cache.predict([("q", "x")] * 91)
    key = cache.seed([("q", "x")], [0.1], {})
    (tmp_path / (key + ".json")).write_text("{}")
    with pytest.raises(ValueError, match="hash"):
        cache.predict([("q", "x")])


def test_native_input_overflow_is_rejected_before_model_prediction(tmp_path):
    class Tokenizer:
        def encode(self, q, body, *, truncation):
            assert truncation is False
            return list(range(len(q) + len(body)))

    model = Model()
    model.tokenizer = Tokenizer()
    model.max_length = 8
    cache = PacketReranker(model, tmp_path, {"weights": "a"})
    cache.enabled = False
    with pytest.raises(ValueError, match="model limit"):
        cache.predict([("query", "too long body")])
    assert model.calls == []
    events = [json.loads(s) for s in (tmp_path / "events.jsonl").read_text().splitlines()]
    assert events[0]["status"] == "input_rejected" and events[0]["actual_pairs"] == 0
