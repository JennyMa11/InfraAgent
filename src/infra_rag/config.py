from dataclasses import asdict, dataclass
from pathlib import Path

from .encoding import DEFAULT_BGE_MODEL, DEFAULT_QWEN_MODEL, QWEN_QUERY_PROMPT

BACKENDS = ("demo", "bge", "qwen")
CHUNK_STRATEGIES = ("semantic", "window", "window_overlap")


def default_embedding_model(backend):
    return DEFAULT_QWEN_MODEL if backend == "qwen" else DEFAULT_BGE_MODEL


@dataclass(frozen=True)
class Settings:
    data_dir: Path = Path("data/default-v2")
    backend: str = "demo"
    embedding_model: str = DEFAULT_BGE_MODEL
    embedding_revision: str | None = None
    embedding_device: str | None = None
    embedding_batch_size: int | None = None
    embedding_query_prompt: str | None = None
    embedding_max_length: int = 8192
    reranker_model: str = "BAAI/bge-reranker-base"
    rerank: bool = False
    multimodal: bool = False
    chunk_size: int = 450
    chunk_strategy: str = "semantic"
    chunk_overlap: int = 0
    refinement_threshold: float = 0.55
    image_merge_threshold: float = 0.88
    image_max_side: int = 768
    image_min_area: float = 0.005
    image_max_regions: int = 24
    clip_text_model: str = "sentence-transformers/clip-ViT-B-32-multilingual-v1"
    clip_image_model: str = "sentence-transformers/clip-ViT-B-32"
    semantic_threshold: float = 0.72
    candidate_k: int = 30
    answer_top_k: int = 5
    query_decomposition: bool = False
    rrf_constant: int = 60
    rerank_top_n: int = 90
    candidate_pool_cap: int | None = None
    neighbor_expansion: bool = True
    context_chars: int = 4000
    context_tokens: int = 1200
    context_mode: str = "neighbors"
    context_policy: str = "prefix"
    heading_context: bool = False
    fusion_candidates: str = "truncate"
    lexical_query_mode: str = "raw"
    query_language: str = "none"
    preprocessing_version: str | None = None

    def __post_init__(self):
        if self.rrf_constant < 1 or not 1 <= self.rerank_top_n <= 90:
            raise ValueError("invalid RRF constant or rerank depth (1..90)")
        if self.candidate_pool_cap is not None and not 1 <= self.candidate_pool_cap <= 90:
            raise ValueError("candidate_pool_cap must be in [1, 90]")
        if self.backend not in BACKENDS:
            raise ValueError("backend must be demo, bge or qwen")
        if self.backend == "qwen" and self.embedding_model == DEFAULT_BGE_MODEL:
            object.__setattr__(self, "embedding_model", default_embedding_model("qwen"))
        if self.embedding_batch_size is not None and self.embedding_batch_size < 1:
            raise ValueError("embedding_batch_size must be positive")
        if self.embedding_max_length < 1:
            raise ValueError("embedding_max_length must be positive")
        if self.chunk_size < 100 or self.candidate_k < 1 or self.context_chars < 100:
            raise ValueError("invalid retrieval limits")
        if not 1 <= self.answer_top_k <= 100:
            raise ValueError("answer_top_k must be in 1..100")
        if self.query_decomposition and (
            self.context_mode != "neighbors" or self.context_policy != "prefix"
        ):
            raise ValueError("query decomposition requires neighbors/prefix context")
        if self.context_tokens < 1 or self.context_mode not in {"legacy", "neighbors"}:
            raise ValueError("invalid context policy")
        if self.context_policy not in {"prefix", "complete"}:
            raise ValueError("context_policy must be prefix or complete")
        if self.context_policy == "complete" and self.context_mode != "neighbors":
            raise ValueError("complete context requires neighbors mode")
        if self.context_chars < self.chunk_size:
            raise ValueError("context_chars must be at least chunk_size")
        if self.chunk_strategy not in CHUNK_STRATEGIES:
            raise ValueError("chunk_strategy must be semantic, window or window_overlap")
        if not 0 <= self.chunk_overlap < self.chunk_size:
            raise ValueError("chunk_overlap must be nonnegative and smaller than chunk_size")
        if self.chunk_overlap and self.chunk_strategy != "window_overlap":
            raise ValueError("chunk_overlap requires window_overlap strategy")
        if self.backend != "qwen" and self.embedding_query_prompt is not None:
            raise ValueError("embedding_query_prompt requires qwen backend")
        if self.image_max_side < 64 or not 0 < self.image_min_area < 1:
            raise ValueError("invalid image geometry limits")
        if self.image_max_regions < 1:
            raise ValueError("image_max_regions must be positive")
        if not -1 <= self.refinement_threshold <= 1 or not -1 <= self.image_merge_threshold <= 1:
            raise ValueError("invalid semantic thresholds")
        if not -1 <= self.semantic_threshold <= 1:
            raise ValueError("semantic_threshold must be in [-1, 1]")
        if self.multimodal and self.backend == "demo":
            raise ValueError("multimodal requires a real backend and model dependencies")
        if self.fusion_candidates not in {"truncate", "union"}:
            raise ValueError("fusion_candidates must be truncate or union")
        if self.lexical_query_mode not in {"raw", "technical"}:
            raise ValueError("lexical_query_mode must be raw or technical")
        if self.query_language not in {"none", "english", "bilingual"}:
            raise ValueError("query_language must be none, english or bilingual")

    @property
    def uses_semantic_embeddings(self):
        return self.backend != "demo"

    def fingerprint(self):
        values = asdict(self)
        if self.preprocessing_version is None:
            values.pop("preprocessing_version")
        # Preserve compatibility with existing indexes when the new mode is disabled.
        if not self.heading_context:
            values.pop("heading_context")
        if self.embedding_revision is None:
            values.pop("embedding_revision")
        if not self.chunk_overlap:
            values.pop("chunk_overlap")
        if self.backend != "qwen":
            values.pop("embedding_query_prompt")
            values.pop("embedding_max_length")
        elif self.embedding_query_prompt is None:
            values["embedding_query_prompt"] = QWEN_QUERY_PROMPT
        excluded = {
            "data_dir",
            "rerank",
            "reranker_model",
            "candidate_k",
            "answer_top_k",
            "query_decomposition",
            "rrf_constant",
            "rerank_top_n",
            "candidate_pool_cap",
            "neighbor_expansion",
            "context_chars",
            "context_tokens",
            "context_mode",
            "context_policy",
            "fusion_candidates",
            "lexical_query_mode",
            "query_language",
            "embedding_device",
            "embedding_batch_size",
        }
        fingerprint = {key: value for key, value in values.items() if key not in excluded}
        fingerprint["schema_version"] = 2
        fingerprint["embedding_pooling"] = (
            "native-last-token-v1" if self.backend == "qwen" else "token-window-mean-v1"
        )
        if self.backend == "qwen":
            fingerprint["embedding_dimension"] = 1024
        return fingerprint
