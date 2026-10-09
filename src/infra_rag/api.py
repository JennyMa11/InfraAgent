from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .assistant import AnswerService, ConversationNotFound, ModelUnavailable
from .context import response_payload
from .service import RetrievalService


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=8000)
    top_k: int = Field(default=5, ge=1, le=100)
    domain: str | None = None
    modality: str | None = None
    strategy: str = "hybrid"
    debug: bool = False


class IngestRequest(BaseModel):
    path: str
    domain: str = "general"


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    conversation_id: str | None = None
    domain: str | None = None


def create_app(service: RetrievalService, assistant: AnswerService | None = None):
    app = FastAPI(title="Infra Knowledge Assistant", version="0.2.0")
    assistant = assistant or AnswerService(service)

    @app.get("/health")
    def health():
        return {**service.status(), "assistant": assistant.status()}

    @app.post("/chat")
    def chat(request: ChatRequest):
        if not request.message.strip():
            raise HTTPException(422, "message must not be blank")
        try:
            return assistant.answer(
                request.message.strip(), request.conversation_id, request.domain
            )
        except (ValueError, TypeError) as exc:
            raise HTTPException(422, str(exc)) from exc
        except ConversationNotFound as exc:
            raise HTTPException(404, "conversation not found") from exc
        except ModelUnavailable as exc:
            raise HTTPException(503, str(exc)) from exc

    @app.post("/warmup")
    def warmup():
        try:
            return assistant.warmup()
        except ModelUnavailable as exc:
            raise HTTPException(503, str(exc)) from exc

    @app.get("/conversations/{conversation_id}")
    def conversation(conversation_id: str):
        try:
            return assistant.conversation(conversation_id)
        except ValueError as exc:
            raise HTTPException(422, "invalid conversation ID") from exc
        except ConversationNotFound as exc:
            raise HTTPException(404, "conversation not found") from exc

    @app.post("/search")
    def search(request: SearchRequest):
        try:
            parameters = request.model_dump(exclude={"debug"})
            diagnostics = {} if request.debug else None
            context = {}
            hits = service.search(**parameters, diagnostics=diagnostics, context_pack=context)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
        return {
            "query": request.query,
            "configuration": service.status(),
            **response_payload(hits, diagnostics, context),
        }

    @app.post("/ingest")
    def ingest(request: IngestRequest):
        try:
            return service.ingest(Path(request.path), request.domain)
        except (ValueError, OSError) as exc:
            raise HTTPException(422, str(exc)) from exc

    @app.get("/parents/{parent_id}")
    def parent(parent_id: str):
        chunks = service.get_parent(parent_id)
        if not chunks:
            raise HTTPException(404, "parent not found")
        return {"parent_id": parent_id, "chunks": [asdict(c) for c in chunks]}

    @app.get("/sources")
    def sources():
        with service.lock:
            return {"sources": sorted({c.source for c in service.chunks})}

    @app.delete("/sources")
    def delete(source: str):
        try:
            return {"deleted_chunks": service.delete(source)}
        except ValueError as exc:
            raise HTTPException(409, str(exc)) from exc

    return app
