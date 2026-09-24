"""Loads and caches scenario/town data at process startup.

All reads happen once here; request handlers only touch in-memory dicts.
This mirrors the requirement that re-querying a scenario must not
re-fetch or re-compute anything (docs/02_仕様・要件/UI_デザイン受け入れ基準.md).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data/naisui_poc/02_processed"
RAW = ROOT / "data/naisui_poc/01_raw"
WEB_MAP = PROCESSED / "web_map"

# 採用パイプライン。docs/03_モデル検証/中延二葉_モデル実績照合レビュー.md で確定。
PIPELINE_DIR = PROCESSED / "pysheds_surface_routing"

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
