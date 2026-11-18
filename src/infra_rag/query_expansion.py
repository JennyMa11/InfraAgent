"""Translate retrieval queries without giving the translator answers or evidence."""

import json
import re
from collections import OrderedDict
from threading import Lock
from time import perf_counter

_PAGED_ATTENTION = re.compile(
    r"(?<![A-Za-z0-9_./-])paged?[ \t]*attention(?![A-Za-z0-9_./(-])", re.IGNORECASE
)
_LITERAL_QUERY_PARTS = re.compile(
    r"(```[\s\S]*?(?:```|\Z)|`[^`\n]*(?:`|(?=\n)|\Z)|https?://\S+)", re.IGNORECASE
)


def normalize_terms(query):
    """Resolve bounded prose aliases without rewriting code, URLs, or adjacent identifiers."""
    return "".join(
        part if index % 2 else _PAGED_ATTENTION.sub("PagedAttention", part)
        for index, part in enumerate(_LITERAL_QUERY_PARTS.split(query))
    )


TRANSLATION_PROMPT = (
    "Translate the user's technical retrieval question into English. Do not answer it. "
    "Preserve every product/version, code/API identifier, condition, negation and uncertainty. "
    "Do not add facts, evidence or an inferred answer. Return only a JSON object with one "
    'nonempty string field: {"english_query":"translated question"}.'
)

DECOMPOSITION_PROMPT = (
    "Generate 1-3 English retrieval sub-queries for the user's technical question. Do not "
    "answer it. Keep one sub-query close to the original English question; add focused "
    "sub-queries for each required fact, condition, comparison or step. Preserve every "
    "product/version and code/API identifier. Do not add facts or evidence. Return only a "
    'JSON object: {"sub_queries":["first","second"]}.'
)


def decompose_query(query, english, model):
    messages = [
        {"role": "system", "content": DECOMPOSITION_PROMPT},
        {
            "role": "user",
            "content": f"Original question: {query}\nEnglish retrieval question: {english}",
        },
    ]
    raw = model.generate(messages)
    obj = json.loads(raw)
    values = obj.get("sub_queries") if isinstance(obj, dict) else None
    if not isinstance(values, list) or not 1 <= len(values) <= 3:
        raise ValueError("Invalid sub-query list")
    result = []
    for value in values:
        if not isinstance(value, str) or not value.strip() or len(value) > 500:
            raise ValueError("Invalid sub-query")
        if value.strip() not in result:
            result.append(value.strip())
    if not result:
        raise ValueError("Empty sub-query list")
    return result


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


class QueryDecomposer:
    """Bounded sub-query cache; failures are surfaced to the caller for fallback."""

    def __init__(self, model, cache_size=128):
        if cache_size < 1:
            raise ValueError("Invalid query decomposition configuration")
        self.model, self.cache_size = model, cache_size
        self.cache = OrderedDict()
        self.lock = Lock()

    def expand(self, query, english=None):
        started = perf_counter()
        english = english or ""
        key = (query, english)
        with self.lock:
            cached = key in self.cache
            if cached:
                subqueries = self.cache.pop(key)
            else:
                subqueries = decompose_query(query, english, self.model)
            self.cache[key] = subqueries
            while len(self.cache) > self.cache_size:
                self.cache.popitem(last=False)
        return list(subqueries), {
            "step": "query_decompose",
            "original_query": query,
            "english_query": english,
            "sub_queries": list(subqueries),
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
