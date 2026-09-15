from __future__ import annotations

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    scenario_id: str
    town_slug: str | None = None


class ChatResponse(BaseModel):
    display_text: str
    headline: str
    status: str
    facts: list[str]
    model_context: str
    safe_next_steps: list[str]
    prohibited_claim_check: dict[str, bool]
    sources: list[dict[str, str]]
