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
    # 回答の対象にした町丁目。メッセージから読み取った場合もここで返し、画面の選択状態を合わせる。
    town_slug: str | None = None
