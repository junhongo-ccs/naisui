"""Deterministic safety policy, applied before any LLM/template response is built.

Implements the decision table in
docs/中延二葉_段階3_Dify_LLM安全ガードレール仕様.md §3, ahead of the (currently
template-based, later Dify-backed) explanation step. Nothing here should be
bypassed by user input, RAG content, or the LLM adapter.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

# 簡易キーワードマッチ。精緻化は別タスク（docs/中延二葉_チャットUI_要件定義.md 未確定の前提）。
EMERGENCY_KEYWORDS = [
    "閉じ込め",
    "閉じこめ",
    "助けて",
    "溺れ",
    "おぼれ",
    "けがをした",
    "怪我をした",
    "動けない",
    "意識がない",
    "息ができない",
]


def detect_emergency(message: str) -> bool:
    return any(keyword in message for keyword in EMERGENCY_KEYWORDS)


def official_status_stub(town_name: str | None) -> dict[str, Any]:
    """Official-info connection is not implemented yet; always return 'unknown',
    never interpret a missing connection as 'safe'."""
    return {
        "source": "品川区（未接続・手動更新プレースホルダー）",
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "evacuation_notice": None,
        "weather_warning": None,
        "shelter_status": "unknown",
        "road_status": "unknown",
    }


def emergency_response() -> dict[str, Any]:
    return {
        "headline": "危険な状況の可能性があります",
        "status": "emergency",
        "facts": [],
        "model_context": "この状況ではモデルによる分析よりも安全確保を優先します。",
        "safe_next_steps": [
            "命に関わる危険がある場合は119番（消防・救急）または110番（警察）に通報してください。",
            "可能であれば周囲の人に助けを求めてください。",
            "安全な高い場所へ移動してください。",
        ],
        "prohibited_claim_check": {
            "route_instruction": False,
            "shelter_safety_guarantee": False,
            "ungrounded_depth_forecast": False,
        },
        "sources": [],
    }


def ambiguous_location_response() -> dict[str, Any]:
    return {
        "headline": "対象の町丁目を教えてください",
        "status": "insufficient_data",
        "facts": [],
        "model_context": "町丁目が未指定のため、推測で地点を補完していません。",
        "safe_next_steps": ["画面のボタンから対象の町丁目を選択するか、町丁目名を入力してください。"],
        "prohibited_claim_check": {
            "route_instruction": False,
            "shelter_safety_guarantee": False,
            "ungrounded_depth_forecast": False,
        },
        "sources": [],
    }
