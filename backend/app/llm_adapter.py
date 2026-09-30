"""Dify LLM call, with the deterministic template as fallback.

Builds the response contract
(docs/02_仕様・要件/中延二葉_段階3_Dify_LLM安全ガードレール仕様.md §6) by calling the Dify
chatflow (prompt: data/naisui_poc/04_llm_knowledge/dify_llm_prompt.md, setup notes:
dify_chatflow_setup.md in the same folder, knowledge:
naisui-knowledge). The deterministic policy checks in main.py/policy.py run before
this module and are never delegated to Dify. If Dify is not configured, times out,
or returns something that breaks the contract, the template response is returned.
"""

from __future__ import annotations

import json
import logging
import os
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from .data import MODEL_INFO

logger = logging.getLogger(__name__)

# backend/.env（コミットしない）。起動方法に関係なく読み込む。既に設定済みの環境変数は上書きしない。
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

KNOWLEDGE_NAME = "naisui-knowledge"
STATUSES = {"caution", "insufficient_data", "emergency", "official_notice"}
PROHIBITED_KEYS = ("route_instruction", "shelter_safety_guarantee", "ungrounded_depth_forecast")

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
    message: str,
    town_name: str,
    scenario_id: str,
    town_risk: dict[str, Any],
    official_status: dict[str, Any],
    run_metadata: dict[str, Any],
) -> dict[str, Any]:
    if os.environ.get("DIFY_API_KEY"):
        try:
            contract = _dify_contract(
                message=message,
                town_name=town_name,
                scenario_id=scenario_id,
                town_risk=town_risk,
                official_status=official_status,
            )
            contract["sources"] = _sources(run_metadata, official_status, knowledge=True)
            return contract
        except Exception as exc:  # タイムアウト・通信エラー・契約違反はすべてテンプレートに戻す
            logger.warning("Dify response rejected, falling back to template: %s", exc)
    return _template(
        town_name=town_name,
        scenario_id=scenario_id,
        town_risk=town_risk,
        official_status=official_status,
        run_metadata=run_metadata,
    )


def _dify_contract(
    *,
    message: str,
    town_name: str,
    scenario_id: str,
    town_risk: dict[str, Any],
    official_status: dict[str, Any],
) -> dict[str, Any]:
    # 開始ノードの入力変数（dify_chatflow_setup.md「開始ノードの入力変数」）。
    inputs = {
        "town_name": town_name,
        "scenario_label": SCENARIO_META.get(scenario_id, {}).get("label", scenario_id),
        "calibration_status": "pre_calibration_screening",
        "risk_level": town_risk.get("risk_level", "不明"),
        "area_ratio_pct": str(round(town_risk.get("area_over_threshold_ratio", 0.0) * 100, 2)),
        "official_status": json.dumps(
            {k: v for k, v in official_status.items() if k != "retrieved_at"}, ensure_ascii=False
        ),
    }
    # 知識検索のクエリはsys.query。町丁目名を付けて、その町丁目のファイルが検索に掛かるようにする。
    return _call_dify(inputs, f"{town_name}について: {message}")


# このマップそのものについての質問では、町丁目の入力変数にこの値を入れる。
# Difyの入力変数を増やさずに済むよう、プロンプト側はこの値を見て答え方を変える（dify_llm_prompt.md「答え方」2行目）。
ABOUT_MAP_TOWN = "このマップ全般（町丁目の指定なし）"
_ABOUT_MAP_FACTS = [
    "このマップは、品川区 中延・二葉地区の10町丁目で、大雨のとき雨水が地表にたまりやすい場所を地形と土地利用から試算し、東京都の公式の浸水想定と並べて見せるPoCです。",
    "試算は、国土地理院の5m標高データとPLATEAUの土地利用をもとに、下水道が受け切れない分の雨水が低い所へ流れてたまる量を10分ごとに24時間分計算したものです。",
    "下水道の管路は計算に入れていません。今の雨の状況や浸水の予報を伝えるものではありません。",
]


def generate_about_map(*, message: str, scenario_id: str, official_status: dict[str, Any]) -> dict[str, Any]:
    """このマップ（Webツール）についての質問に答える。町丁目の数値は渡さない。"""
    if os.environ.get("DIFY_API_KEY"):
        try:
            inputs = {
                "town_name": ABOUT_MAP_TOWN,
                "scenario_label": SCENARIO_META.get(scenario_id, {}).get("label", scenario_id),
                "calibration_status": "pre_calibration_screening",
                "risk_level": "対象外（町丁目の指定なし）",
                "area_ratio_pct": "対象外",
                "official_status": json.dumps(
                    {k: v for k, v in official_status.items() if k != "retrieved_at"}, ensure_ascii=False
                ),
            }
            # 「このマップについて」を付けて、RAG/04_このマップについて.md のチャンクが検索に掛かるようにする。
            contract = _call_dify(inputs, f"このマップについて: {message}")
            contract["sources"] = [
                {
                    "name": f"Difyナレッジ {KNOWLEDGE_NAME}（RAG/：このマップについて・用語）",
                    "retrieved_at": datetime.now(timezone.utc).isoformat(),
                }
            ]
            return contract
        except Exception as exc:  # タイムアウト・通信エラー・契約違反はすべてテンプレートに戻す
            logger.warning("Dify response rejected, falling back to template: %s", exc)
    return {
        "headline": "このマップについて",
        "status": "caution",
        "facts": _ABOUT_MAP_FACTS,
        "model_context": f"このマップの試算は{MODEL_INFO['label']}で、実際の浸水予報ではありません。{MODEL_INFO['not_evaluated']}。",
        "safe_next_steps": ["計算のしかたや使っている技術は、画面上部の「このマップについて知る」で詳しく読めます。"],
        "prohibited_claim_check": {k: False for k in PROHIBITED_KEYS},
        "sources": [],
    }


def _call_dify(inputs: dict[str, str], query: str) -> dict[str, Any]:
    base_url = os.environ.get("DIFY_BASE_URL", "https://api.dify.ai/v1").rstrip("/")
    timeout = float(os.environ.get("DIFY_TIMEOUT_SECONDS", "30"))
    body = {
        "inputs": inputs,
        "query": query,
        "response_mode": "blocking",
        "user": "naisui-poc-backend",
    }
    request = urllib.request.Request(
        f"{base_url}/chat-messages",
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {os.environ['DIFY_API_KEY']}",
            "Content-Type": "application/json",
            # api.dify.aiの前段のCloudflareは、urllib既定のUser-Agent（Python-urllib）を403（error 1010）で拒否する。
            "User-Agent": "naisui-poc-backend/0.1",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            answer = json.loads(response.read().decode("utf-8"))["answer"]
    except urllib.error.HTTPError as exc:
        # Difyはエラーの理由を本文のJSONで返す（例: Workflow not published）。ログで原因を追えるよう残す。
        # モデル側の失敗はPluginInvokeErrorの長いtracebackになり、理由（例: 429 RESOURCE_EXHAUSTED）は末尾にある。
        detail = exc.read().decode("utf-8", "replace")
        try:
            detail = json.loads(detail).get("message", detail)
        except ValueError:
            pass
        detail = detail if len(detail) <= 400 else "..." + detail[-400:]
        raise ValueError(f"Dify HTTP {exc.code}: {detail}") from exc
    return _validate(_parse_json(answer))


def _parse_json(answer: str) -> dict[str, Any]:
    # モデルが```json ... ```で囲んで返すことがあるため、最初の{から最後の}までを取り出す。
    match = re.search(r"\{.*\}", answer, re.DOTALL)
    if not match:
        raise ValueError("no JSON object in Dify answer")
    return json.loads(match.group(0))


def _validate(raw: dict[str, Any]) -> dict[str, Any]:
    """JSON契約で検証する。違反はValueErrorにし、呼び出し側でテンプレートに戻す。"""

    def text(key: str) -> str:
        value = raw.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{key} must be a non-empty string")
        return value.strip()

    def texts(key: str) -> list[str]:
        value = raw.get(key)
        if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
            raise ValueError(f"{key} must be a list of strings")
        return [v.strip() for v in value if v.strip()]

    status = text("status")
    if status not in STATUSES:
        raise ValueError(f"unknown status: {status}")
    check = raw.get("prohibited_claim_check")
    if not isinstance(check, dict) or any(check.get(k) is not False for k in PROHIBITED_KEYS):
        raise ValueError(f"prohibited_claim_check failed: {check}")
    facts = texts("facts")
    if status == "caution" and not facts:
        raise ValueError("caution response without facts")
    return {
        "headline": text("headline"),
        "status": status,
        "facts": facts,
        "model_context": text("model_context"),
        "safe_next_steps": texts("safe_next_steps"),
        "prohibited_claim_check": {k: False for k in PROHIBITED_KEYS},
    }


def _sources(run_metadata: dict[str, Any], official_status: dict[str, Any], *, knowledge: bool) -> list[dict[str, str]]:
    sources = [
        {
            "name": f"naisui PoC モデル (pysheds_surface_routing + PLATEAU土地利用 {MODEL_INFO['version']})",
            "retrieved_at": run_metadata.get("generated_at", datetime.now(timezone.utc).isoformat()),
        },
        {
            "name": official_status["source"],
            "retrieved_at": official_status["retrieved_at"],
        },
    ]
    if knowledge:
        sources.append(
            {
                "name": f"Difyナレッジ {KNOWLEDGE_NAME}（RAG/：地域の背景・町丁目の事実・用語）",
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
            }
        )
    return sources


def _template(
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
            f"この結果は{MODEL_INFO['label']}（試行的なシナリオ計算）であり、"
            "実際の浸水予報ではありません。個別地点の浸水深予報・避難判断には使用しないでください。"
            f"{MODEL_INFO['assumption']}（{MODEL_INFO['data_versions']}）。{MODEL_INFO['not_evaluated']}。"
        ),
        "safe_next_steps": [
            "最新の公式な避難情報・気象警報を確認してください。",
            "不安な場合は品川区の公式情報を確認してください。",
        ],
        "prohibited_claim_check": {k: False for k in PROHIBITED_KEYS},
        "sources": _sources(run_metadata, official_status, knowledge=False),
    }
