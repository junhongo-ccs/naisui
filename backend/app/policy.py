"""Deterministic safety policy, applied before any LLM/template response is built.

Implements the decision table in
docs/02_仕様・要件/中延二葉_段階3_Dify_LLM安全ガードレール仕様.md §3, ahead of the (currently
template-based, later Dify-backed) explanation step. Nothing here should be
bypassed by user input, RAG content, or the LLM adapter.
"""

from __future__ import annotations

import re
import unicodedata
from datetime import datetime, timezone
from typing import Any

from .data import COVERAGE_LABEL, TOWN_CHOICES

# 質問の長さの上限（画面の入力欄と合わせる）。長文の貼り付けや指示の注入を抑える。
MAX_MESSAGE_LENGTH = 200

# このマップが答えない質問（2026-09-29、要件定義 8章の決定）。Difyを呼ぶ前に決まった答えを返す。
# 判断を求める質問: 避難の要否、経路、通行、安全の保証。
_JUDGMENT = re.compile(
    r"避難(?:す|し)(?:べき|たほう|た方|なきゃ|ないと)|逃げ(?:るべき|たほう|た方|なきゃ|ないと)|どこ[にへ]逃げ"
    r"|避難経路|通れ|通行でき|安全(?:です|か|な場所|な道|[?？])|大丈夫"
)
# 今の状況・予報を聞く質問。「今まで」「今回」は過去や一般の話、「今のうちに」「明日から」は備えの話なので含めない。
_REALTIME = re.compile(
    r"今[、,は]|今の(?!うち)|いま[、は]|いまの(?!うち)|現在|リアルタイム|予報|今日|今夜|明日(?!から)|あした(?!から)"
    r"|開いて|空いて|開設|警報|注意報|避難指示|避難情報|降って|雨雲"
)

# このマップ（Webツール）そのものについての質問（2026-09-30）。町丁目が決まっていなくてもDifyに渡し、
# ナレッジの RAG/04_このマップについて.md で答えさせる。町丁目名が書かれた質問は町丁目の質問として扱う（main.py）。
_ABOUT_MAP = re.compile(
    r"この(?:マップ|地図|ツール|サイト|アプリ|サービス|チャット|ページ)|マップについて"
    r"|どうやって(?:計算|試算|作|求め)|計算(?:の)?(?:しかた|仕方|方法)|試算(?:の)?(?:しかた|仕方|方法|前提)"
    r"|仕組み|しくみ|使い方|使いかた|操作方法|見方|凡例|紫色?(?:は|って|の意味)|青灰色"
    r"|技術|だれが作|誰が作|何のため|なんのため|目的|精度|相関|照合|流出係数|湛水深|リスク区分"
    r"|Dify|Gemini|pysheds|PLATEAU|React|Vercel|Render"
)
# 用語の意味を聞く質問（RAG/03_用語とデータの説明.md で答える）。「暗渠はどこを通ってる？」のような
# 場所を聞く質問は町丁目ごとの事実なので含めず、「って何」「とは」など意味を聞く言い方に限る。
_TERM_QUESTION = re.compile(
    r"(?:暗渠|あんきょ|立会川|立会道路|立会川幹線|内水(?:氾濫|はん濫|はんらん)|外水(?:氾濫|はん濫|はんらん)|浸水想定区域"
    r"|想定最大規模(?:降雨|の大雨)?|湛水|冠水|床下浸水|床上浸水|アンダーパス|掘割|土のう置場|ハザードマップ|標高タイル)"
    r"\s*(?:って|とは|の意味|は何|はなに|について|(?:と[^\s?？。、]{1,12})?の違い)"
)


def detect_about_map(message: str) -> bool:
    """このマップそのもの、または用語の意味を聞く質問か。どちらも町丁目を選ばなくても答えられる。"""
    text = unicodedata.normalize("NFKC", message)
    return bool(_ABOUT_MAP.search(text) or _TERM_QUESTION.search(text))


# 簡易キーワードマッチ。精緻化は別タスク（docs/02_仕様・要件/中延二葉_チャットUI_要件定義.md 未確定の前提）。
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


def detect_out_of_scope(message: str) -> str | None:
    """判断を求める質問なら "judgment"、今の状況・予報を聞く質問なら "realtime" を返す。"""
    text = unicodedata.normalize("NFKC", message)
    if _JUDGMENT.search(text):
        return "judgment"
    if _REALTIME.search(text):
        return "realtime"
    return None


def _no_claims() -> dict[str, bool]:
    return {"route_instruction": False, "shelter_safety_guarantee": False, "ungrounded_depth_forecast": False}


def out_of_scope_response(kind: str, town_name: str | None) -> dict[str, Any]:
    """このマップが答えない質問への決まった答え。公式情報へ案内し、町丁目が分かれば事実を聞けることを示す。"""
    if kind == "judgment":
        headline = "避難や安全の判断は、このチャットではできません"
        context = "このマップの試算は、避難の判断、避難所の安全、道路の通行可否を評価していません。"
        steps = ["避難するかどうかは、品川区の避難情報と気象庁の情報をもとに判断してください。"]
    else:
        headline = "このマップでは、今の状況や予報は分かりません"
        context = (
            "このマップは、想定最大規模の大雨のときに雨水がたまりやすい場所を、平時に確かめるためのものです。"
            "今の雨の状況、浸水の予報、避難所の開設状況、道路の通行可否は扱っていません。"
        )
        steps = [
            "今の避難情報と避難所の開設状況は、品川区の防災情報で確認してください。",
            "大雨による浸水の危険度は、気象庁の「キキクル（危険度分布）」で確認できます。",
        ]
    steps.append("命に関わる危険がある場合は119番または110番に通報してください。")
    if town_name:
        steps.append(f"{town_name}の地形やたまりやすい場所など、備えに役立つ事実は下の質問例から聞けます。")
    return {
        "headline": headline,
        "status": "insufficient_data",
        "facts": [],
        "model_context": context,
        "safe_next_steps": steps,
        "prohibited_claim_check": _no_claims(),
        "sources": [],
    }


def too_long_response() -> dict[str, Any]:
    return {
        "headline": f"質問は{MAX_MESSAGE_LENGTH}字以内で入力してください",
        "status": "insufficient_data",
        "facts": [],
        "model_context": "長い文章は受け付けていません。聞きたいことを短くまとめて、もう一度送ってください。",
        "safe_next_steps": [],
        "prohibited_claim_check": _no_claims(),
        "sources": [],
    }


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


def ambiguous_location_response(
    unrecognized_place: str | None = None,
    out_of_area_town: str | None = None,
    multiple_towns: list[str] | None = None,
) -> dict[str, Any]:
    """町丁目を特定できないときの応答。PoCのデータ範囲を明示し、その中から選んでもらう。

    地名から町丁目を推測しない。場所が特定できない地名は「範囲外」とも断定しない
    （実際には範囲内の地名である可能性があるため）。
    """
    coverage = f"このPoCでデータがあるのは、{COVERAGE_LABEL}だけです。"
    if out_of_area_town:
        headline = f"{out_of_area_town}はこのPoCの対象範囲外です"
        context = f"{coverage}{out_of_area_town}のデータはありません。"
    elif unrecognized_place:
        headline = f"「{unrecognized_place}」の場所を特定できません"
        context = f"{coverage}「{unrecognized_place}」がこの中のどの町丁目にあたるかは推測しません。"
    elif multiple_towns:
        headline = "町丁目を1つ選んでください"
        context = f"{'と'.join(multiple_towns)}の{len(multiple_towns)}つが書かれています。1つずつお答えします。{coverage}"
    else:
        headline = "対象の町丁目を教えてください"
        context = f"町丁目が未指定のため、推測で地点を補完していません。{coverage}"
    steps = ["下の町丁目から1つ選んでください（選ぶと入力欄に反映されます）。"]
    if out_of_area_town or unrecognized_place:
        steps.append("対象範囲外の地域は、品川区の公式ハザードマップ・浸水実績を確認してください。")
    return {
        "headline": headline,
        "status": "insufficient_data",
        "facts": [],
        "model_context": context,
        "safe_next_steps": steps,
        "town_choices": TOWN_CHOICES,
        "prohibited_claim_check": {
            "route_instruction": False,
            "shelter_safety_guarantee": False,
            "ungrounded_depth_forecast": False,
        },
        "sources": [],
    }
