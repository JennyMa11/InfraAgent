"""Translate retrieval queries without giving the translator answers or evidence."""

import json
from collections import OrderedDict
from threading import Lock
from time import perf_counter

TRANSLATION_PROMPT = (
    "Translate the user's technical retrieval question into English. Do not answer it. "
    "Preserve every product/version, code/API identifier, condition, negation and uncertainty. "
    "Do not add facts, evidence or an inferred answer. Return only a JSON object with one "
    'nonempty string field: {"english_query":"translated question"}.'
)


def translate_query(query, model):
    messages = [
        {"role": "system", "content": TRANSLATION_PROMPT},
        {"role": "user", "content": query},
    ]
    raw = model.generate(messages)
    obj = json.loads(raw)
    english = obj.get("english_query") if isinstance(obj, dict) else None
    if not isinstance(english, str) or not english.strip() or len(english) > 2000:
        raise ValueError("Invalid English retrieval query")
    return english.strip()


def expanded_query(query, english, mode):
    if mode not in {"english", "bilingual"}:
        raise ValueError("Query language must be english or bilingual")
    return english if mode == "english" else f"{query}\n{english}"


def load_rewrites(path, questions):
    records = [json.loads(line) for line in path.read_text().splitlines()]
    by_id = {record["id"]: record for record in records}
    if len(records) != len(by_id) or set(by_id) != {q["id"] for q in questions}:
        raise ValueError(
            "Rewrites must cover exactly the selected dev questions, without duplicates"
        )
    for question in questions:
        record = by_id[question["id"]]
        english = record.get("english_query")
        if record["original_query"] != question["query"]:
            raise ValueError("Rewrite original does not match the fixed question")
        if not isinstance(english, str) or not english.strip() or len(english) > 2000:
            raise ValueError("Invalid English retrieval query")
    return {r["original_query"]: r["english_query"].strip() for r in records}


class QueryTranslator:
    """Bounded per-client cache; serialize calls to keep response metadata consistent."""

    def __init__(self, model, mode="english", cache_size=128):
        if mode not in {"english", "bilingual"} or cache_size < 1:
            raise ValueError("Invalid query translation configuration")
        self.model, self.mode, self.cache_size = model, mode, cache_size
        self.cache = OrderedDict()
        self.lock = Lock()

    def expand(self, query):
        started = perf_counter()
        with self.lock:
            cached = query in self.cache
            if cached:
                english = self.cache.pop(query)
            else:
                english = translate_query(query, self.model)
            self.cache[query] = english
            while len(self.cache) > self.cache_size:
                self.cache.popitem(last=False)
        return expanded_query(query, english, self.mode), {
            "step": "query_translate",
            "original_query": query,
            "english_query": english,
            "mode": self.mode,
            "cached": cached,
            "duration_ms": round((perf_counter() - started) * 1000, 1),
        }


class ExpandedRetrieval:
    """Offline replay of frozen translations; original evaluation questions stay intact."""

    def __init__(self, service, rewrites, mode):
        self.service, self.rewrites, self.mode = service, rewrites, mode

    def __getattr__(self, name):
        return getattr(self.service, name)

    @property
    def settings(self):
        return self.service.settings

    @settings.setter
    def settings(self, settings):
        self.service.settings = settings

    def search(self, query, **kwargs):
        english = self.rewrites.get(query)
        actual = expanded_query(query, english, self.mode) if english else query
        result = self.service.search(actual, **kwargs)
        if kwargs.get("diagnostics") is not None:
            kwargs["diagnostics"]["query_expansion"] = {
                "original": query,
                "actual": actual,
                "mode": self.mode,
            }
        return result
