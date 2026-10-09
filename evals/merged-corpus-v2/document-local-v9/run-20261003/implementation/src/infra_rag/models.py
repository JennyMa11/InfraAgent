from dataclasses import dataclass, field


@dataclass
class Chunk:
    id: str
    parent_id: str
    source: str
    content: str
    domain: str
    heading: str = ""
    modality: str = "text"
    locator: str = ""
    page: int | None = None
    start_line: int | None = None
    end_line: int | None = None
    image_path: str | None = None
    bbox: list[float] | None = None
    chunk_type: str = "paragraph"
    coordinate_space: str | None = None
    parent_bbox: list[float] | None = None
    caption_source: str | None = None
    caption_locator: str | None = None
    visual_features: dict[str, float] = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)


@dataclass
class Hit:
    chunk: Chunk
    score: float
    channels: list[str] = field(default_factory=list)
    rerank_score: float | None = None
    context: str = ""
    sibling_ids: list[str] = field(default_factory=list)
    context_ref: str | None = None
    evidence: list[dict] = field(default_factory=list)
