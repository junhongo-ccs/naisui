"""Stand-in for the Dify LLM call.

Dify itself is not wired up yet (docs/02_仕様・要件/中延二葉_チャットUI_要件定義.md §5: 作らないもの).
This module builds the same response contract
(docs/02_仕様・要件/中延二葉_段階3_Dify_LLM安全ガードレール仕様.md §6) from a deterministic
template so the frontend and API contract can be built/tested now. Swap this
module's `generate` function for a real Dify call later; callers should not
need to change.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

# 実績照合レビュー(docs/03_モデル検証/中延二葉_モデル実績照合レビュー.md 第2章)のtied-rank Spearman ρ。
# UIでは実績を主張の根拠にせず、モデル推定が過去傾向とどれだけ整合するかの参考値として示す
# （docs/02_仕様・要件/中延二葉_チャットUI_要件定義.md 第6章「モデルと浸水実績データの提示方針」）。
SCENARIO_META = {
    "sc_153mmh_24h_690mm_official": {
        "label": "想定最大規模降雨 (1時間153mm・24時間690mm)",
        "rainfall_condition": "最大の連続1時間を153mm、残り23時間を均等配分した暫定24時間ハイエトグラフ",
        "history_correlation_note": "区の想定最大規模降雨に条件を合わせた比較用シナリオです。公式の時間分布図を入手後に置き換えます。",
    },
}


def generate(
    *,
    town_name: str,
    scenario_id: str,
    town_risk: dict[str, Any],
    official_status: dict[str, Any],
    run_metadata: dict[str, Any],
) -> dict[str, Any]:
    meta = SCENARIO_META.get(scenario_id, {})
    risk_level = town_risk.get("risk_level", "不明")
    area_ratio_pct = round(town_risk.get("area_over_threshold_ratio", 0.0) * 100, 2)

    facts = [
        f"{town_name}: シナリオ「{meta.get('label', scenario_id)}」における推定リスクレベルは「{risk_level}」。",
        f"20cm以上の湛水が推定される面積の割合は約{area_ratio_pct}%（町丁目内のセル単位集計）。",
        meta.get("history_correlation_note", ""),
    ]
    facts = [f for f in facts if f]

    return {
        "headline": f"{town_name}のシナリオ別リスク推定: {risk_level}",
        "status": "caution" if risk_level != "湛水なし（本簡易モデル上）" else "official_notice",
        "facts": facts,
        "model_context": (
            "この結果は校正前のスクリーニングモデルによる試行的なシナリオ結果であり、"
            "実際の浸水予報ではありません。個別地点の浸水深予報・避難判断には使用しないでください。"
        ),
        "safe_next_steps": [
            "最新の公式な避難情報・気象警報を確認してください。",
            "不安な場合は品川区の公式情報を確認してください。",
        ],
        "prohibited_claim_check": {
            "route_instruction": False,
            "shelter_safety_guarantee": False,
            "ungrounded_depth_forecast": False,
        },
        "sources": [
            {
                "name": "naisui PoC モデル (pysheds_surface_routing, 校正前)",
                "retrieved_at": run_metadata.get("generated_at", datetime.now(timezone.utc).isoformat()),
            },
            {
                "name": official_status["source"],
                "retrieved_at": official_status["retrieved_at"],
            },
        ],
    }
