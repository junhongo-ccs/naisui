"""Loads and caches scenario/town data at process startup.

All reads happen once here; request handlers only touch in-memory dicts.
This mirrors the requirement that re-querying a scenario must not
re-fetch or re-compute anything (docs/02_仕様・要件/UI_デザイン受け入れ基準.md).
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data/naisui_poc/02_processed"
RAW = ROOT / "data/naisui_poc/01_raw"
WEB_MAP = PROCESSED / "web_map"

# 採用パイプライン。pysheds地表流モデル（docs/03_モデル検証/中延二葉_モデル実績照合レビュー.md で確定）に、
# PLATEAU土地利用・建物によるセル別流出係数（標準係数）と、低い道路セルへの優先流下を入れた版（2026-09-25、ユーザー決定）。
# 比較と採用の経緯: docs/03_モデル検証/中延二葉_土地利用反映モデル比較.md、中延二葉_道路優先流下モデル比較.md
PIPELINE_DIR = PROCESSED / "pysheds_surface_routing_roads/plateau2025_v3_road050"

# 画面・回答に必ず併記するモデルの前提（docs/01_概要・計画/PLATEAU導入計画.md 7章）。
MODEL_INFO: dict[str, Any] = {
    "label": "土地利用と道路の流れを反映した校正前スクリーニング結果",
    "version": "plateau2025_v3_road050",
    "data_versions": "土地利用: 東京都土地利用現況調査2021（PLATEAU 2025年度版）、建物: PLATEAU 2025年度版",
    "assumption": "土地利用と建物から、雨水が地表へ流出する割合（流出係数）をセルごとに仮定し、雨水は隣の低い道路へ優先して流れるとしています",
    "not_evaluated": "下水道の管路、避難の可否、道路の通行可否は評価していません",
}

SCENARIOS: list[dict[str, Any]] = [
    {"scenario_id": "sc_153mmh_24h_690mm_official", "label": "想定最大規模降雨 (1時間153mm・24時間690mm)", "default": True},
]
DEFAULT_SCENARIO_ID = "sc_153mmh_24h_690mm_official"

# risk_lookupの町丁目名 -> URLで使うslug。UIのボタン選択・地図クリックの双方から参照する。
TOWN_SLUGS: dict[str, str] = {
    "中延一丁目": "nakanobu-1",
    "中延二丁目": "nakanobu-2",
    "中延三丁目": "nakanobu-3",
    "中延四丁目": "nakanobu-4",
    "中延五丁目": "nakanobu-5",
    "中延六丁目": "nakanobu-6",
    "二葉一丁目": "futaba-1",
    "二葉二丁目": "futaba-2",
    "二葉三丁目": "futaba-3",
    "二葉四丁目": "futaba-4",
}
SLUG_TO_TOWN = {v: k for k, v in TOWN_SLUGS.items()}

# PoCでデータがある範囲。範囲外・特定できない場所を聞かれたときに、この範囲と選択肢を示す。
COVERAGE_LABEL = "品川区の中延一〜六丁目・二葉一〜四丁目の10町丁目"
TOWN_CHOICES: list[dict[str, str]] = [{"name": name, "slug": slug} for name, slug in TOWN_SLUGS.items()]

# 自由入力の町丁目名の読み取り。「二葉二丁目」「二葉2丁目」「二葉２」「中延 6丁目」などを受け付ける。
# 丁目の無い「二葉」や「荏原中延」は丁目が特定できないので読み取らない（推測で補わない）。
_KANJI_DIGITS = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
_TOWN_MENTION = re.compile(r"(中延|二葉)\s*([1-9一二三四五六七八九])(?![0-9])\s*(?:丁目)?")


def towns_mentioned(message: str) -> list[str]:
    """メッセージに書かれた町丁目名（TOWN_SLUGSのキー表記）を出現順に重複なく返す。

    対象外の丁目（中延七丁目など）は "対象外:<表記>" として返し、呼び出し側で確認を促す。
    """
    text = unicodedata.normalize("NFKC", message)  # 全角数字・全角スペースを半角へ
    found: list[str] = []
    for area, digit in _TOWN_MENTION.findall(text):
        number = int(digit) if digit.isdigit() else _KANJI_DIGITS[digit]
        kanji = next((k for k, v in _KANJI_DIGITS.items() if v == number), str(number))
        name = f"{area}{kanji}丁目"
        entry = name if name in TOWN_SLUGS else f"対象外:{name}"
        if entry not in found:
            found.append(entry)
    return found


# 「下神明あたり」「戸越公園駅の近く」のように場所を指す言い方。町丁目名として読めない場所が書かれて
# いるときに、選択中の町丁目で黙って答えないために使う（駅名・地名から町丁目への変換は推測になるのでしない）。
_PLACE_MENTION = re.compile(r"([^\s、。,.!?「」『』()はもがのをにでとへや]{1,12}?)の?(?:あたり|辺り|付近|周辺|近辺|近く|界隈|周り|方面|駅)")
# 選択中の町丁目を指すとみなす語。「この辺り」は「こ」＋「の」＋「辺り」と読まれるため、こ・そ・あ・どの1文字も含める。
_DEICTIC_PLACES = {"こ", "そ", "あ", "ど", "この", "その", "あの", "ここ", "そこ", "こちら", "うち", "自宅", "家", "現在地", "今いる所"}


def unrecognized_places(message: str) -> list[str]:
    """場所を指す言い方のうち、対象の町丁目名として読み取れないもの（「下新明」等）を返す。"""
    text = unicodedata.normalize("NFKC", message)
    places: list[str] = []
    for place in _PLACE_MENTION.findall(text):
        if place in _DEICTIC_PLACES or _TOWN_MENTION.search(place) or place in places:
            continue
        places.append(place)
    return places


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


class Store:
    """In-memory cache built once at import time."""

    def __init__(self) -> None:
        self.risk_lookups: dict[str, dict[str, Any]] = {}
        self.run_metadata: dict[str, dict[str, Any]] = {}
        for scenario in SCENARIOS:
            sid = scenario["scenario_id"]
            scenario_dir = PIPELINE_DIR / sid
            risk_path = scenario_dir / f"risk_lookup_{sid}.json"
            metadata_path = scenario_dir / "run_metadata.json"
            self.risk_lookups[sid] = _load_json(risk_path) if risk_path.exists() else {"towns": {}}
            self.run_metadata[sid] = _load_json(metadata_path) if metadata_path.exists() else {}

        hazard_meta_path = WEB_MAP / "hazard_pdf_derived.metadata.json"
        self.hazard_metadata = _load_json(hazard_meta_path) if hazard_meta_path.exists() else {}

        self.sandbag_geojson = _load_json(RAW / "shelter/sandbag_locations_nakanobu_futaba.geojson")
        self.shelter_geojson = _load_json(RAW / "shelter/shelter_locations_nakanobu_futaba.geojson")

    def risk_for(self, scenario_id: str, town_name: str) -> dict[str, Any] | None:
        return self.risk_lookups.get(scenario_id, {}).get("towns", {}).get(town_name)

    def ponding_bounds(self, scenario_id: str) -> dict[str, Any] | None:
        path = WEB_MAP / f"ponding_depth_{scenario_id}.bounds.json"
        return _load_json(path) if path.exists() else None


store = Store()
