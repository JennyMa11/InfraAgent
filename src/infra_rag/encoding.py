import hashlib
import math
import re
from collections import Counter

import jieba

DEFAULT_BGE_MODEL = "BAAI/bge-small-zh-v1.5"
DEFAULT_QWEN_MODEL = "Qwen/Qwen3-Embedding-0.6B"
QWEN_QUERY_PROMPT = (
    "Instruct: Given a web search query, retrieve relevant passages that answer the query\nQuery:"
)

INFRA_TERMS = (
    "张量并行",
    "流水线并行",
    "数据并行",
    "键值缓存",
    "分页注意力",
    "连续批处理",
    "梯度同步",
    "算子融合",
    "显存管理",
)
for term in INFRA_TERMS:
    jieba.add_word(term, tag="n")


def tokenize(text: str) -> list[str]:
    tokens = re.findall(r"[a-zA-Z0-9_]+(?:[.+/-][a-zA-Z0-9_]+)*", text.lower())
    for run in re.findall(r"[\u3400-\u9fff]+", text):
        tokens.extend(run)
        tokens.extend(run[i : i + 2] for i in range(len(run) - 1))
    tokens.extend(word for word in jieba.cut(text.lower()) if word.strip() and len(word) > 1)
    return tokens


def dot(a, b):
    return sum(x * y for x, y in zip(a, b, strict=True))


class DemoEncoder:
    """Deterministic lexical hashing; NOT a semantic embedding model."""

    def encode(self, texts, *, query=False):
        vectors = []
        for text in texts:
            vector = [0.0] * 384
            for token, count in Counter(tokenize(text)).items():
                digest = hashlib.sha256(token.encode()).digest()
                index = int.from_bytes(digest[:4], "big") % len(vector)
                vector[index] += count * (1 if digest[4] % 2 else -1)
            norm = math.sqrt(dot(vector, vector)) or 1
            vectors.append([v / norm for v in vector])
        return vectors


class BGEEncoder:
    def __init__(self, model_name, *, revision=None, device=None, batch_size=None):
        from sentence_transformers import SentenceTransformer

        options = {k: v for k, v in {"revision": revision, "device": device}.items() if v}
        self.model = SentenceTransformer(model_name, **options)
        self.batch_size = batch_size
        self.instruction = "为这个句子生成表示以用于检索相关文章：" if "-zh" in model_name else ""

    @property
    def token_limit(self):
        return self.model.max_seq_length - 2

    def token_length(self, text):
        return len(self.model.tokenizer.encode(text, add_special_tokens=False))

    def encode(self, texts, *, query=False):
        inputs = [self.instruction + text for text in texts] if query else texts
        return encode_segments(self.model, inputs, batch_size=self.batch_size)


class QwenEncoder:
    """Official Qwen3 sentence-transformers pooling; no silent input truncation."""

    def __init__(
        self,
        model_name=DEFAULT_QWEN_MODEL,
        *,
        revision=None,
        device=None,
        batch_size=2,
        query_prompt=QWEN_QUERY_PROMPT,
        max_length=8192,
    ):
        import torch
        from sentence_transformers import SentenceTransformer

        if batch_size < 1 or max_length < 1 or not query_prompt:
            raise ValueError("positive limits and a nonempty query prompt are required")
        options = {k: v for k, v in {"revision": revision, "device": device}.items() if v}
        self.model = SentenceTransformer(
            model_name, model_kwargs={"torch_dtype": torch.float32}, **options
        )
        pooling = self.model[1]
        if not (
            getattr(pooling, "pooling_mode_lasttoken", False)
            or getattr(pooling, "pooling_mode", None) == "lasttoken"
        ):
            raise ValueError("Qwen embedding requires the official last-token pooling module")
        if max_length > self.model.max_seq_length:
            raise ValueError("requested max_length exceeds the model context limit")
        self.model.max_seq_length = max_length
        self.model.tokenizer.padding_side = "left"
        self.batch_size, self.query_prompt = batch_size, query_prompt

    @property
    def token_limit(self):
        return self.model.max_seq_length - 2

    def token_length(self, text):
        return len(self.model.tokenizer.encode(text, add_special_tokens=False))

    def encode(self, texts, *, query=False):
        if not texts:
            return []
        prompt = self.query_prompt if query else ""
        for text in texts:
            length = len(self.model.tokenizer.encode(prompt + text, add_special_tokens=True))
            if length > self.model.max_seq_length:
                raise ValueError(f"Qwen input has {length} tokens; refusing silent truncation")
        vectors = self.model.encode(
            texts,
            prompt=prompt,
            batch_size=self.batch_size,
            normalize_embeddings=True,
            show_progress_bar=False,
        ).tolist()
        for vector in vectors:
            if len(vector) != 1024 or not all(math.isfinite(v) for v in vector):
                raise ValueError("Qwen must return finite, native 1024-dimensional embeddings")
            norm = math.sqrt(dot(vector, vector))
            if not math.isclose(norm, 1, abs_tol=1e-4):
                raise ValueError("Qwen returned an unnormalized embedding")
        return vectors


class CLIPEncoder:
    """Paired image encoder and multilingual text encoder in the same CLIP space."""

    def __init__(
        self,
        image_model="sentence-transformers/clip-ViT-B-32",
        text_model="sentence-transformers/clip-ViT-B-32-multilingual-v1",
    ):
        from sentence_transformers import SentenceTransformer

        self.image = SentenceTransformer(image_model)
        self.text = SentenceTransformer(text_model)

    def encode_images(self, paths):
        from PIL import Image

        images = []
        for path in paths:
            with Image.open(path) as image:
                images.append(image.convert("RGB"))
        return self.image.encode(images, normalize_embeddings=True).tolist()

    def encode_query(self, query):
        return self.encode_texts([query])

    def encode_texts(self, texts):
        return encode_segments(self.text, texts)


def encode_segments(model, texts, *, batch_size=None):
    """Pool full-text token windows in the model's native space instead of truncating."""
    windows, ranges = [], []
    limit = model.max_seq_length - 2
    for text in texts:
        ids = model.tokenizer.encode(text, add_special_tokens=False)
        start = len(windows)
        if len(ids) <= limit:
            windows.append(text)
        else:
            windows.extend(
                model.tokenizer.decode(ids[offset : offset + limit], skip_special_tokens=True)
                for offset in range(0, len(ids), limit)
            )
        ranges.append((start, len(windows)))
    if not windows:
        return []
    options = {"batch_size": batch_size} if batch_size is not None else {}
    embeddings = model.encode(windows, normalize_embeddings=True, **options)
    result = []
    for start, end in ranges:
        pooled = embeddings[start:end].mean(axis=0)
        norm = math.sqrt(float((pooled * pooled).sum())) or 1
        result.append((pooled / norm).tolist())
    return result
