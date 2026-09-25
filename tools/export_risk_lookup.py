"""Aggregate a scenario's GeoTIFFs by town polygon and write risk_lookup JSON.

This is a screening-level spatial summary. Its risk labels are not official
evacuation classifications and must not be used as evacuation instructions.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.mask import mask

from run_surface_water_balance import ground_cell_areas_m2


TARGET_TOWN_PATTERN = r"^(中延[一二三四五六]丁目|二葉[一二三四]丁目)$"

# area_over_threshold_ratio（浸水深閾値を超えたセルの面積比）でラベル付けする。
# max_depth_m は単一セルの最大値でありDEMアーティファクトに支配されるため使わない。
# 根拠: docs/03_モデル検証/中延二葉_モデル実績照合レビュー.md
#   区の浸水実績（町丁目別棟数）とのSpearman順位相関で、max_depth_mは負相関（ρ=-0.30）、
#   area_over_threshold_ratioは正相関（ρ=+0.517、n=9のため統計的有意ではないが実績と整合的）。
# 閾値は sc_100mm_extreme / pysheds_surface_routing の実データ分布（0%〜2.385%）を参考にした
# 暫定値であり、正式な校正（優先度B: 町丁目ラベルの判定根拠の明文化）で見直す前提。
def risk_level(area_over_threshold_ratio: float) -> str:
    if area_over_threshold_ratio <= 0.0:
        return "湛水なし（本簡易モデル上）"
    if area_over_threshold_ratio < 0.003:
        return "軽微な湛水（注意）"
    if area_over_threshold_ratio < 0.006:
        return "道路冠水相当（警戒）"
    if area_over_threshold_ratio < 0.012:
        return "床下浸水相当（警戒）"
    return "床上浸水相当（危険）"


def raster_values(path: Path, geometry: object) -> tuple[np.ndarray, np.ndarray]:
    """町丁目内のセル値と、各セルの地上面積（m²）を同じ順で返す。"""
    with rasterio.open(path) as dataset:
        values, transform = mask(dataset, [geometry], crop=True, filled=False, all_touched=True)
        areas = np.broadcast_to(ground_cell_areas_m2(transform, dataset.crs, values.shape[1]), values.shape[1:])
    band = values[0]
    return band.compressed().astype(float), np.ma.array(areas, mask=np.ma.getmaskarray(band)).compressed()


def parse_elapsed_minutes(path: Path) -> float:
    matched = re.fullmatch(r"ponding_depth_t([0-9.]+)min\.tif", path.name)
    if not matched:
        raise ValueError(f"Unexpected time-raster name: {path.name}")
    return float(matched.group(1))


def run(args: argparse.Namespace) -> None:
    maximum_raster = args.raster or args.scenario_dir / "maximum_ponding_depth_m.tif"
    if not maximum_raster.exists():
        raise FileNotFoundError(f"Scenario maximum raster not found: {maximum_raster}")
    time_rasters = sorted(args.scenario_dir.glob("ponding_depth_t*min.tif"), key=parse_elapsed_minutes)
    if not time_rasters:
        raise FileNotFoundError(f"No time rasters found in: {args.scenario_dir}")

    towns = gpd.read_file(args.towns)
    if args.name_field not in towns.columns:
        fields = ", ".join(str(field) for field in towns.columns)
        raise KeyError(f"Name field '{args.name_field}' not found. Available fields: {fields}")
    with rasterio.open(maximum_raster) as dataset:
        raster_crs = dataset.crs
    if towns.crs is None:
        raise ValueError("Town polygon file has no CRS. Define its CRS before processing.")
    towns = towns.to_crs(raster_crs)
    towns = towns[towns[args.name_field].astype(str).str.fullmatch(args.target_pattern, na=False)].copy()
    if towns.empty:
        raise ValueError("No towns matched --target-pattern. Check names and --name-field.")
    # e-Statのファイルには基本単位区単位で同じ町丁目名が繰り返されるものがある。
    # 町丁目単位のJSONにするため、同名ポリゴンを一つへ結合する。
    towns = towns.dissolve(by=args.name_field, as_index=False)

    result: dict[str, object] = {
        "scenario_id": args.scenario_dir.name,
        "source_raster": maximum_raster.name,
        "depth_threshold_m": args.depth_threshold_m,
        "risk_label_note": "PoC用の簡易分類。行政の浸水想定・避難情報を置き換えない。",
        "towns": {},
    }
    output_towns: dict[str, object] = result["towns"]  # type: ignore[assignment]
    for _, town in towns.iterrows():
        name = str(town[args.name_field])
        max_values, cell_areas_m2 = raster_values(maximum_raster, town.geometry)
        if not len(max_values):
            continue
        valid = max_values >= 0
        values = max_values[valid]
        areas = cell_areas_m2[valid]
        over_threshold = values >= args.depth_threshold_m
        peak_depth_m = -1.0
        peak_time_min = 0.0
        for raster_path in time_rasters:
            values_at_time, _ = raster_values(raster_path, town.geometry)
            if len(values_at_time) and float(np.max(values_at_time)) > peak_depth_m:
                peak_depth_m = float(np.max(values_at_time))
                peak_time_min = parse_elapsed_minutes(raster_path)
        max_depth_m = float(np.max(values))
        # 面積比は地上面積で重み付けする（EPSG:3857では行ごとにセル面積がわずかに異なる）。
        area_over_threshold_ratio = float(areas[over_threshold].sum() / areas.sum())
        output_towns[name] = {
            "max_depth_m": max_depth_m,
            "mean_depth_m": float(np.average(values, weights=areas)),
            "area_over_threshold_m2": float(areas[over_threshold].sum()),
            "area_over_threshold_ratio": area_over_threshold_ratio,
            "risk_level": risk_level(area_over_threshold_ratio),
            "peak_time_min": peak_time_min,
        }

    output = args.output or args.scenario_dir / f"risk_lookup_{args.scenario_dir.name}.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {output} for {len(output_towns)} towns")


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario-dir", type=Path, required=True)
    parser.add_argument("--raster", type=Path, help="集計対象の最大湛水深GeoTIFF。省略時はscenario-dir直下を使う。")
    parser.add_argument(
        "--towns",
        type=Path,
        default=root / "data/naisui_poc/01_raw/boundaries/shinagawa_town_2020.geojson",
        help="町丁目ポリゴン（GeoJSON、GPKG、Shapefile等）",
    )
    parser.add_argument("--name-field", default="S_NAME", help="町丁目名を格納した属性列")
    parser.add_argument("--target-pattern", default=TARGET_TOWN_PATTERN, help="対象町丁目名を選ぶ正規表現")
    parser.add_argument("--depth-threshold-m", type=float, default=0.20)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
