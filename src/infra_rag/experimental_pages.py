"""Explicit opt-in page delivery and bounded extraction for the existing QA chain."""

import copy
from time import monotonic

from .chunking import stable_id
from .paged_answers import (
    final_context,
    select_within_budget,
    selection_messages,
    verify_selections,
)


class PageBudgetError(ValueError):
    pass


class RequestModel:
    def __init__(self, client, seconds=180):
        self.client = copy.copy(client)
        self.deadline = monotonic() + seconds
        self.calls = []
        self.model = client.model
        self.provider = getattr(client, "provider", "unknown")

    def generate(self, messages):
        remaining = self.deadline - monotonic()
        if remaining <= 0:
            raise PageBudgetError("Experimental request time budget exhausted")
        if hasattr(self.client, "timeout"):
            self.client.timeout = min(self.client.timeout, remaining)
        call = {"messages": copy.deepcopy(messages)}
        self.calls.append(call)
        started = monotonic()
        try:
            call["raw"] = self.client.generate(messages)
            return call["raw"]
        except Exception as exc:
            call["error"] = type(exc).__name__
            raise
        finally:
            call["duration_ms"] = (monotonic() - started) * 1000
            call["provider_response"] = getattr(self.client, "last_call", None)


def pages_from_chunks(chunks, count, token_limit, char_limit, max_pages=12):
    pages, current = [], []

    def fits(evidence):
        text = "\n\n".join(
            f"[{e['citation_id']}] 来源：{e['locator']}\n{e['content']}" for e in evidence
        )
        return len(text) <= char_limit and count(text) <= token_limit

    for chunk in chunks:
        item = {
            "citation_id": "E" + stable_id(chunk.id),
            "chunk_id": chunk.id,
            "parent_id": chunk.parent_id,
            "source": chunk.source,
            "locator": chunk.locator,
            "content": chunk.content,
            "start_line": chunk.start_line,
            "end_line": chunk.end_line,
            "metadata": copy.deepcopy(chunk.metadata),
        }
        if not fits([item]):
            raise PageBudgetError("A complete source chunk exceeds page budget; no truncation")
        if current and not fits(current + [item]):
            pages.append({"evidence": current})
            current = []
        current.append(item)
    if current:
        pages.append({"evidence": current})
    if len(pages) > max_pages:
        raise PageBudgetError("Required source pages exceed experimental page limit")
    return pages


def consume_pages(question, pages, model, counters, token_limit, char_limit, trace):
    if len(pages) > 12:
        raise PageBudgetError("Experimental page limit exceeded")
    candidates = []
    for index, page in enumerate(pages):
        evidence = page["evidence"]
        # Validate actual rendered source page, not an upstream budget assertion.
        final_context(evidence, counters, token_limit, char_limit)
        started = monotonic()
        event = {"step": "select_page", "page": index, "evidence": copy.deepcopy(evidence)}
        trace.append(event)
        try:
            raw = model.generate(selection_messages(question, evidence))
            selected = verify_selections(raw, evidence)
            candidates.extend(selected)
            event.update(status="completed", selected_units=selected)
        except Exception:
            event["status"] = "failed"
            raise
        finally:
            event["duration_ms"] = (monotonic() - started) * 1000
    context, omitted = select_within_budget(candidates, counters, token_limit, char_limit)
    trace.append(
        {
            "step": "pack_verified_quotes",
            "pages_consumed": len(pages),
            "selection_mode": "whole_units",
            "candidate_units": candidates,
            "omitted_units": omitted,
            "evidence": copy.deepcopy(context["evidence"]),
            "token_counts": context["verified_quote_tokens"],
            "characters": context["characters"],
        }
    )
    return context
