"""Check PLATEAU land-use coverage over the target towns and preview surface categories.

フェーズ0（docs/01_概要・計画/PLATEAU導入計画.md）の実装。モデル入力は作らない。
PLATEAU `luse` が中延・二葉＋バッファを欠損・重複なく覆っているか、分類不明が無いか、
建物（`bldg`）との位置ずれが無いかを確認し、分類対応表による5区分の面積割合を集計する。

土地利用は区画単位の用途であり、宅地には屋根と庭・通路の両方が含まれる。そこで、
`bldg` の建物外形を先に「建物・屋根」とし、残りを分類対応表の
`category_outside_buildings` で区分する。

入力の変換（QGIS同梱のogr2ogr）:
  ogr2ogr -oo EXPOSE_GML_ID=YES -f GPKG luse_2025.gpkg 533935_luse_6697_op.gml LandUse -nlt MULTIPOLYGON -dim XY -nln luse

出力（既定では data/naisui_poc/02_processed/plateau/）:
  landuse_coverage_by_town.csv   町丁目別・対象範囲全体のカバレッジ、品質指標、5区分の面積割合
  landuse_class_area.csv         対象範囲内の土地利用区分（orgLandUse）別面積
  landuse_coverage_metadata.json 入力・設定・注意事項
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd
import pandas as pd

from count_buildings_by_town import TARGET_TOWN_PATTERN, WORK_CRS, load_buildings, load_towns


CATEGORIES = ["建物・屋根", "道路・舗装", "駐車場等の不浸透面", "緑地", "水面・その他"]
ROAD_CODES = {5100}
UNKNOWN_CODES = {0, 90}
TARGET_AREA_NAME = "対象範囲全体（バッファ込み）"


def m2(value: float) -> float:
    # 浮動小数の誤差で出る -0.0 を 0.0 にそろえる
    return round(value, 1) + 0.0


def read_mapping(path: Path) -> pd.DataFrame:
    mapping = pd.read_csv(path, dtype={"org_land_use": int})
    unknown = set(mapping["category_outside_buildings"]) - set(CATEGORIES)
    if unknown:
        raise ValueError(f"Unknown categories in mapping: {sorted(unknown)}")
    if mapping["org_land_use"].duplicated().any():
        raise ValueError("Duplicate org_land_use codes in mapping.")
    return mapping


def load_landuse(path: Path, layer: str | None, area: object) -> gpd.GeoDataFrame:
    bbox = tuple(gpd.GeoSeries([area], crs=WORK_CRS).to_crs("EPSG:6668").total_bounds)
    landuse = gpd.read_file(path, layer=layer, bbox=bbox) if layer else gpd.read_file(path, bbox=bbox)
    if landuse.crs is None:
        raise ValueError("Land-use file has no CRS. Define its CRS before processing.")
    landuse = landuse.to_crs(WORK_CRS)
    landuse = landuse[landuse.intersects(area)].copy()
    if "orgLandUse" not in landuse.columns:
        raise KeyError("orgLandUse column not found. Convert the CityGML with the ogr2ogr command in the docstring.")
    landuse["orgLandUse"] = landuse["orgLandUse"].fillna(0).astype(int)
    return landuse


def summarize_area(
    name: str,
    zone: object,
    landuse: gpd.GeoDataFrame,
    buildings_union: object,
    road_union: object,
    category_by_code: dict[int, str],
    low_confidence_codes: set[int],
) -> dict[str, object]:
    zone_area = zone.area
    parts = landuse[landuse.intersects(zone)]
    clipped = parts.geometry.intersection(zone)
    covered = clipped.union_all()
    buildings_in_zone = buildings_union.intersection(zone)
    row: dict[str, object] = {
        "area_name": name,
        "area_m2": m2(zone_area),
        "luse_features": len(parts),
        "coverage_ratio": round(covered.area / zone_area, 6),
        "gap_m2": m2(zone_area - covered.area),
        # 重複面積 = 各区画の面積の合計 − 和集合の面積
        "overlap_m2": m2(float(clipped.area.sum()) - covered.area),
        "unknown_class_m2": m2(float(clipped[parts["orgLandUse"].isin(UNKNOWN_CODES)].area.sum())),
        "unmapped_class_m2": m2(float(clipped[~parts["orgLandUse"].isin(category_by_code)].area.sum())),
        "survey_years": ";".join(str(int(year)) for year in sorted(parts["surveyYear"].dropna().unique())),
        # 建物外形が土地利用の「道路」に載る面積。大きければ両データの位置ずれを疑う。
        "building_on_road_m2": m2(buildings_in_zone.intersection(road_union).area),
        "building_on_road_ratio": round(
            buildings_in_zone.intersection(road_union).area / buildings_in_zone.area if buildings_in_zone.area else 0.0, 6
        ),
    }
    category_area = dict.fromkeys(CATEGORIES, 0.0)
    category_area["建物・屋根"] = buildings_in_zone.area
    low_confidence_area = 0.0
    outside = parts.geometry.intersection(zone).difference(buildings_in_zone)
    for code, geometry in zip(parts["orgLandUse"], outside):
        category_area[category_by_code.get(code, "水面・その他")] += geometry.area
        if code in low_confidence_codes or code not in category_by_code:
            low_confidence_area += geometry.area
    for category in CATEGORIES:
        row[f"share_{category}"] = round(category_area[category] / zone_area, 4)
    # 分類対応表でconfidence=lowの区分に割り当てた面積。5区分の割合のうち仮定に依存する部分。
    row["share_low_confidence"] = round(low_confidence_area / zone_area, 4)
    return row


def run(args: argparse.Namespace) -> None:
    mapping = read_mapping(args.mapping)
    category_by_code = dict(zip(mapping["org_land_use"], mapping["category_outside_buildings"]))
    low_confidence_codes = set(mapping.loc[mapping["confidence"] == "low", "org_land_use"])
    towns = load_towns(args.towns, args.name_field, args.target_pattern)
    target_area = towns.union_all().buffer(args.buffer_m)

    landuse = load_landuse(args.landuse, args.landuse_layer, target_area)
    buildings, building_stats = load_buildings(args.buildings, args.buildings_layer, args.id_field)
    buildings = buildings[buildings.intersects(target_area)]
    buildings_union = buildings.geometry.union_all()
    road_union = landuse[landuse["orgLandUse"].isin(ROAD_CODES)].geometry.union_all()

    rows = [summarize_area(TARGET_AREA_NAME, target_area, landuse, buildings_union, road_union, category_by_code, low_confidence_codes)]
    for town, geometry in zip(towns["town"], towns.geometry):
        rows.append(summarize_area(town, geometry, landuse, buildings_union, road_union, category_by_code, low_confidence_codes))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with (args.output_dir / "landuse_coverage_by_town.csv").open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    clipped = landuse.assign(area_m2=landuse.geometry.intersection(target_area).area)
    class_area = (
        clipped.groupby(["orgLandUse", "class"], dropna=False)["area_m2"].sum().reset_index()
        .merge(mapping, how="left", left_on="orgLandUse", right_on="org_land_use")
        .drop(columns="org_land_use")
        .rename(columns={"orgLandUse": "org_land_use", "class": "common_class"})
    )
    class_area["share"] = (class_area["area_m2"] / target_area.area).round(4)
    class_area["area_m2"] = class_area["area_m2"].round(1)
    class_area = class_area.sort_values("area_m2", ascending=False)
    class_area.to_csv(args.output_dir / "landuse_class_area.csv", index=False, encoding="utf-8")

    metadata = {
        "phase": "PLATEAU導入計画 フェーズ0",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "inputs": {
            "landuse": str(args.landuse),
            "buildings": str(args.buildings),
            "towns": str(args.towns),
            "mapping": str(args.mapping),
        },
        "work_crs": WORK_CRS,
        "buffer_m": args.buffer_m,
        "landuse_features_in_target": len(landuse),
        "landuse_change_flag_counts": {str(k): int(v) for k, v in landuse["変化フラグ"].value_counts().items()}
        if "変化フラグ" in landuse.columns else {},
        "buildings_in_target": len(buildings),
        "building_stats": building_stats,
        "category_rule": "bldgの建物外形を「建物・屋根」とし、残りの土地利用区画を分類対応表のcategory_outside_buildingsで区分する。",
        "limitations": [
            "土地利用は2021年調査、建物は2025年度整備であり、時点が一致しない。",
            "5区分の割合は分類対応表の仮定に依存する。confidence=lowの区分（特に住宅の建物外部分）はフェーズ1の感度分析で扱う。",
            "土地利用区分から浸透能・流出係数を直接得られるわけではない。",
        ],
    }
    (args.output_dir / "landuse_coverage_metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"Land-use features in target: {len(landuse)}; buildings: {len(buildings)} -> {args.output_dir}")
    for row in rows:
        shares = " ".join(f"{category}={row[f'share_{category}']:.1%}" for category in CATEGORIES)
        shares += f" (low={row['share_low_confidence']:.1%})"
        print(
            f"  {row['area_name']:<18} cover={row['coverage_ratio']:.4f} gap={row['gap_m2']}m2 "
            f"overlap={row['overlap_m2']}m2 unknown={row['unknown_class_m2']}m2 "
            f"bldg_on_road={row['building_on_road_ratio']:.2%} | {shares}"
        )


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[1]
    processed = root / "data/naisui_poc/02_processed"
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--landuse", type=Path, default=processed / "plateau/luse_2025.gpkg")
    parser.add_argument("--landuse-layer", help="GeoPackage内の土地利用レイヤー名（複数レイヤーがある場合）")
    parser.add_argument("--buildings", type=Path, default=processed / "plateau/bldg_2025_lod0.gpkg")
    parser.add_argument("--buildings-layer", help="GeoPackage内の建築物レイヤー名（複数レイヤーがある場合）")
    parser.add_argument("--id-field", default="gml_id", help="建物の重複除去に使うID列")
    parser.add_argument("--mapping", type=Path, default=processed / "plateau/landuse_category_mapping.csv")
    parser.add_argument(
        "--towns",
        type=Path,
        default=root / "data/naisui_poc/01_raw/boundaries/r2kb13109.shp",
        help="町丁目ポリゴン（GeoJSON、GPKG、Shapefile等）",
    )
    parser.add_argument("--name-field", default="S_NAME", help="町丁目名を格納した属性列")
    parser.add_argument("--target-pattern", default=TARGET_TOWN_PATTERN, help="対象町丁目名を選ぶ正規表現")
    parser.add_argument("--buffer-m", type=float, default=100.0, help="対象範囲全体に付けるバッファ（m）")
    parser.add_argument("--output-dir", type=Path, default=processed / "plateau")
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
