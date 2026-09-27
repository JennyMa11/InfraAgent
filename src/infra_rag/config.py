from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    data_dir: Path = Path("data/default-v2")
    backend: str = "demo"
    embedding_model: str = "BAAI/bge-small-zh-v1.5"
    reranker_model: str = "BAAI/bge-reranker-base"
    rerank: bool = False
    multimodal: bool = False
    chunk_size: int = 450
    chunk_strategy: str = "semantic"
    refinement_threshold: float = 0.55
    image_merge_threshold: float = 0.88
    image_max_side: int = 768
    image_min_area: float = 0.005
    image_max_regions: int = 24
    clip_text_model: str = "sentence-transformers/clip-ViT-B-32-multilingual-v1"
    clip_image_model: str = "sentence-transformers/clip-ViT-B-32"
    semantic_threshold: float = 0.72
    candidate_k: int = 30
    context_chars: int = 4000
    context_tokens: int = 1200
    context_mode: str = "neighbors"
    heading_context: bool = False
    fusion_candidates: str = "truncate"
    lexical_query_mode: str = "raw"

    def __post_init__(self):
        if self.backend not in {"demo", "bge"}:
            raise ValueError("backend must be demo or bge")
        if self.chunk_size < 100 or self.candidate_k < 1 or self.context_chars < 100:
            raise ValueError("invalid retrieval limits")
        if self.context_tokens < 1 or self.context_mode not in {"legacy", "neighbors"}:
            raise ValueError("invalid context policy")
        if self.context_chars < self.chunk_size:
            raise ValueError("context_chars must be at least chunk_size")
        if self.chunk_strategy not in {"semantic", "window"}:
            raise ValueError("chunk_strategy must be semantic or window")
        if self.image_max_side < 64 or not 0 < self.image_min_area < 1:
            raise ValueError("invalid image geometry limits")
        if self.image_max_regions < 1:
            raise ValueError("image_max_regions must be positive")
        if not -1 <= self.refinement_threshold <= 1 or not -1 <= self.image_merge_threshold <= 1:
            raise ValueError("invalid semantic thresholds")
        if not -1 <= self.semantic_threshold <= 1:
            raise ValueError("semantic_threshold must be in [-1, 1]")
        if self.multimodal and self.backend != "bge":
            raise ValueError("multimodal requires bge backend and model dependencies")
        if self.fusion_candidates not in {"truncate", "union"}:
            raise ValueError("fusion_candidates must be truncate or union")
        if self.lexical_query_mode not in {"raw", "technical"}:
            raise ValueError("lexical_query_mode must be raw or technical")

    def fingerprint(self):
        values = asdict(self)
        # Preserve compatibility with existing indexes when the new mode is disabled.
        if not self.heading_context:
            values.pop("heading_context")
        return {
            k: v
            for k, v in values.items()
            if k
            not in {
                "data_dir",
                "rerank",
                "reranker_model",
                "candidate_k",
                "context_chars",
                "context_tokens",
                "context_mode",
                "fusion_candidates",
                "lexical_query_mode",
            }
        } | {"schema_version": 2, "embedding_pooling": "token-window-mean-v1"}
