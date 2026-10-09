"""Content-addressed encoding cache; cache writes never publish an active index."""

import hashlib
import json
import math
import sqlite3
from contextlib import closing
from pathlib import Path


def content_hash(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


class VectorCache:
    def __init__(self, path):
        self.path = path

    def key(self, namespace, content):
        payload = json.dumps([namespace, content], ensure_ascii=False, sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()

    def encode(self, namespace, inputs, encode, identities=None, seeds=None):
        if not inputs:
            return [], {"encoded": 0, "reused": 0}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        identities = inputs if identities is None else identities
        if len(identities) != len(inputs):
            raise ValueError("cache identity count differs from input count")
        keys = [self.key(namespace, value) for value in identities]
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute("CREATE TABLE IF NOT EXISTS vectors (key TEXT PRIMARY KEY, value TEXT)")
            found, seeded = {}, set()
            for key in set(keys):
                row = db.execute("SELECT value FROM vectors WHERE key = ?", (key,)).fetchone()
                if row:
                    found[key] = json.loads(row[0])
                elif seeds and key in seeds:
                    found[key] = seeds[key]
                    seeded.add(key)
            missing = list(dict.fromkeys(key for key in keys if key not in found))
            by_key = dict(zip(keys, inputs, strict=True))
            if missing:
                vectors = encode([by_key[key] for key in missing])
                if len(vectors) != len(missing):
                    raise ValueError("encoder returned an incorrect vector count")
                for key, vector in zip(missing, vectors, strict=True):
                    if not vector or not all(math.isfinite(v) for v in vector):
                        raise ValueError("encoder returned an invalid vector")
                    found[key] = vector
            if any(not found[key] or not all(math.isfinite(v) for v in found[key]) for key in keys):
                raise ValueError("cache contains an invalid vector")
            dimensions = {len(found[key]) for key in keys}
            if len(dimensions) != 1:
                raise ValueError("cached and encoded vector dimensions differ")
            db.executemany(
                "INSERT OR REPLACE INTO vectors VALUES (?, ?)",
                [(key, json.dumps(found[key])) for key in set(missing) | seeded],
            )
        return [found[key] for key in keys], {
            "encoded": len(missing),
            "reused": len(keys) - len(missing),
        }

    def prune(self, active_keys, apply=False):
        if not self.path.exists():
            return {"unused": 0, "retained": 0}
        with closing(sqlite3.connect(self.path)) as db, db:
            stored = {row[0] for row in db.execute("SELECT key FROM vectors")}
            unused = stored - active_keys
            if apply:
                db.executemany("DELETE FROM vectors WHERE key = ?", [(key,) for key in unused])
                db.commit()
                db.execute("VACUUM")
        return {"unused": len(unused), "retained": len(stored & active_keys)}


class CachedEncoder:
    """Reuse document encodings during parsing; query encoding remains unchanged."""

    def __init__(self, encoder, cache, namespace):
        self.encoder, self.cache, self.namespace = encoder, cache, namespace
        self.counts = {"encoded": 0, "reused": 0}

    def __getattr__(self, name):
        return getattr(self.encoder, name)

    def encode(self, texts, *, query=False):
        if query:
            return self.encoder.encode(texts, query=True)
        vectors, counts = self.cache.encode(self.namespace, texts, self.encoder.encode)
        for key in self.counts:
            self.counts[key] += counts[key]
        return vectors
