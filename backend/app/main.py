from __future__ import annotations

import mimetypes

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from . import data, llm_adapter, policy
from .data import store
from .schemas import ChatRequest, ChatResponse

# Pythonのmimetypesは.geojsonを知らずapplication/octet-streamにフォールバックしてしまうため、
# StaticFilesが参照する前に明示的に登録する。
mimetypes.add_type("application/geo+json", ".geojson")

app = FastAPI(title="naisui PoC API")

# ローカル開発のVite既定ポート。デプロイ時はRender側の環境変数で許可オリジンを絞る。
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static/web_map", StaticFiles(directory=str(data.WEB_MAP)), name="web_map")
app.mount("/static/shelter", StaticFiles(directory=str(data.RAW / "shelter")), name="shelter")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/scenarios")
def get_scenarios() -> list[dict]:
    return data.SCENARIOS


@app.get("/api/towns")
def get_towns() -> list[dict]:
    return [{"name": name, "slug": slug} for name, slug in data.TOWN_SLUGS.items()]


def _mtime(path) -> int:
    return int(path.stat().st_mtime) if path.exists() else 0


@app.get("/api/scenario/{scenario_id}")
def get_scenario(scenario_id: str) -> dict:
    if scenario_id not in store.risk_lookups:
        raise HTTPException(status_code=404, detail="unknown scenario_id")
    risk_lookup = store.risk_lookups[scenario_id]
    towns_by_slug = {
        data.TOWN_SLUGS[name]: {
            "name": name,
            "risk_level": town["risk_level"],
            "area_over_threshold_ratio": town["area_over_threshold_ratio"],
        }
        for name, town in risk_lookup.get("towns", {}).items()
        if name in data.TOWN_SLUGS
    }
    return {
        "scenario_id": scenario_id,
        "calibration_status": "pre_calibration_screening",
        "model": data.MODEL_INFO,
        "depth_threshold_m": risk_lookup.get("depth_threshold_m"),
        "towns": towns_by_slug,
        "map_layers": {
            "town_boundaries": "/static/web_map/town_boundaries.geojson",
            "hazard_pdf_derived": "/static/web_map/hazard_pdf_derived.geojson",
            # 画像を作り直したときにブラウザの古いキャッシュが表示されないよう、更新時刻をURLに付ける。
            "ponding_overlay_png": f"/static/web_map/ponding_depth_{scenario_id}.png?v={_mtime(data.WEB_MAP / f'ponding_depth_{scenario_id}.png')}",
            "ponding_overlay_bounds": f"/static/web_map/ponding_depth_{scenario_id}.bounds.json",
            "sandbag_locations": "/static/shelter/sandbag_locations_nakanobu_futaba.geojson",
            "shelter_locations": "/static/shelter/shelter_locations_nakanobu_futaba.geojson",
        },
    }


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    if req.scenario_id not in store.risk_lookups:
        raise HTTPException(status_code=404, detail="unknown scenario_id")

    # 決定的ポリシー判定。LLM/テンプレート生成より必ず先に評価する。
    if policy.detect_emergency(req.message):
        contract = policy.emergency_response()
        return _to_chat_response(contract, contract["headline"])

    # メッセージに町丁目名があればそれを優先し、無ければボタン・地図で選んだ町丁目を使う。
    # 複数の町丁目・対象外の丁目、町丁目として読めない場所（「下神明あたり」等）が書かれている場合は、
    # 選択中の町丁目で答えず、推測せず確認を求める。
    mentioned = data.towns_mentioned(req.message)
    other_places = data.unrecognized_places(req.message)
    out_of_area = [name.removeprefix("対象外:") for name in mentioned if name.startswith("対象外:")]
    if out_of_area:
        contract = policy.ambiguous_location_response(out_of_area_town=out_of_area[0])
        return _to_chat_response(contract, contract["headline"])
    if other_places:
        contract = policy.ambiguous_location_response(unrecognized_place=other_places[0])
        return _to_chat_response(contract, contract["headline"])
    if len(mentioned) > 1:
        contract = policy.ambiguous_location_response(multiple_towns=mentioned)
        return _to_chat_response(contract, contract["headline"])
    if mentioned:
        town_name: str | None = mentioned[0]
    else:
        town_name = data.SLUG_TO_TOWN.get(req.town_slug) if req.town_slug else None
    if town_name is None:
        contract = policy.ambiguous_location_response()
        return _to_chat_response(contract, contract["headline"])

    town_risk = store.risk_for(req.scenario_id, town_name)
    if town_risk is None:
        raise HTTPException(status_code=404, detail="town not found in this scenario's risk_lookup")

    official_status = policy.official_status_stub(town_name)
    run_metadata = store.run_metadata.get(req.scenario_id, {})
    contract = llm_adapter.generate(
        town_name=town_name,
        scenario_id=req.scenario_id,
        town_risk=town_risk,
        official_status=official_status,
        run_metadata=run_metadata,
    )
    return _to_chat_response(contract, contract["headline"], data.TOWN_SLUGS[town_name])


def _to_chat_response(contract: dict, headline: str, town_slug: str | None = None) -> ChatResponse:
    lines = [headline, ""]
    lines.extend(f"・{fact}" for fact in contract["facts"])
    if contract["facts"]:
        lines.append("")
    lines.append(contract["model_context"])
    if contract["safe_next_steps"]:
        lines.append("")
        lines.extend(f"→ {step}" for step in contract["safe_next_steps"])
    return ChatResponse(display_text="\n".join(lines), town_slug=town_slug, **contract)
