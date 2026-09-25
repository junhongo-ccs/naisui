"""Count PLATEAU buildings per town and normalize inundation records by building count.

フェーズ0B（docs/01_概要・計画/PLATEAU導入計画.md）の実装。モデル、パラメータ、
リスク指標、UIは変更しない。検証の物差し（実績側）だけを建物数で正規化する。

入力の建築物データは、PLATEAU `bldg` のCityGMLをGeoPackage/GeoJSONへ変換したもの
（CityGMLを直接は読まない）。QGIS同梱のogr2ogrで変換できる:
  ogr2ogr -f GPKG bldg.gpkg 53393527_bldg_6697_op.gml Building -nlt MULTIPOLYGON -dim XY -nln bldg
複数メッシュは -append で同じレイヤーへ追加する。

出力（既定では data/naisui_poc/02_processed/plateau/）:
  building_counts_by_town.csv        町丁目別建物棟数
  inundation_history_normalized.csv  建物数で正規化した31年累計・R7.9.11実績
  rank_correlation_normalization.csv 正規化前後のSpearman順位相関（平均順位法）
  building_counts_run_metadata.json  入力・設定・注意事項

PLATEAUの整備年度と実績の対象期間（1989〜2020年、2025年9月11日）は一致せず、
その間の建て替え・新築による建物数の変化は補正できない。正規化後の値は検証用の
相対比較にのみ使い、個別建物の浸水や避難判断の根拠にしない。
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd
from shapely import force_2d, make_valid
from shapely.ops import unary_union


TARGET_TOWN_PATTERN = r"^(中延[一二三四五六]丁目|二葉[一二三四]丁目)$"
WORK_CRS = "EPSG:6677"  # JGD2011 / 平面直角座標系IX系。既存DEM・モデル出力と同じ
KANJI_DIGITS = {"1": "一", "2": "二", "3": "三", "4": "四", "5": "五", "6": "六", "7": "七", "8": "八", "9": "九"}


def normalize_town_name(name: str) -> str:
    """'中延2丁目' → '中延二丁目'。浸水実績CSVとe-Stat境界で数字表記が異なるため揃える。"""
    return re.sub(r"(\d)丁目$", lambda m: KANJI_DIGITS[m.group(1)] + "丁目", name.strip())


def parse_count_class(label: str) -> tuple[float, float]:
    """R7.9.11実績の件数階級（'0件'、'1-5件'、'111件以上'等）を下限・上限へ変換する。"""
    text = label.strip()
    if matched := re.fullmatch(r"(\d+)件", text):
        value = float(matched.group(1))
        return value, value
    if matched := re.fullmatch(r"(\d+)-(\d+)件", text):
        return float(matched.group(1)), float(matched.group(2))
    if matched := re.fullmatch(r"(\d+)件以上", text):
        # 上限が無い階級では上限側の率を定義できない。順位安定性の確認は不能として扱う。
        return float(matched.group(1)), math.nan
    raise ValueError(f"Unexpected R7.9.11 class label: {label}")


# 平均順位法（tied rank）。docs/03_モデル検証/中延二葉_モデル実績照合レビュー.md 第6章と同じ処理。
def average_ranks(values: dict[str, float]) -> dict[str, float]:
    ordered = sorted(values, key=lambda key: -values[key])
    ranks: dict[str, float] = {}
    i = 0
    while i < len(ordered):
        j = i
        while j + 1 < len(ordered) and values[ordered[j + 1]] == values[ordered[i]]:
            j += 1
        for key in ordered[i : j + 1]:
            ranks[key] = (i + j) / 2 + 1
        i = j + 1
    return ranks


def spearman(x: dict[str, float], y: dict[str, float]) -> tuple[float | None, int, str]:
    common = [key for key in x if key in y and not math.isnan(x[key]) and not math.isnan(y[key])]
    n = len(common)
    if n < 3:
        return None, n, "算出不能（共通町丁目が3未満）"
    if len({x[key] for key in common}) == 1 or len({y[key] for key in common}) == 1:
        # 全町丁目が同値だと分散0で相関が定義できない。rank()の辞書順タイブレークによる
        # 無意味な値を出さないよう明示的に弾く（照合レビュー第2.2章の−0.250の誤りの再発防止）。
        return None, n, "算出不能（一方が全町丁目同値）"
    rank_x = average_ranks({key: x[key] for key in common})
    rank_y = average_ranks({key: y[key] for key in common})
    a = [rank_x[key] for key in common]
    b = [rank_y[key] for key in common]
    mean_a, mean_b = sum(a) / n, sum(b) / n
    sd_a = sum((v - mean_a) ** 2 for v in a) ** 0.5
    sd_b = sum((v - mean_b) ** 2 for v in b) ** 0.5
    rho = sum((u - mean_a) * (v - mean_b) for u, v in zip(a, b)) / (sd_a * sd_b)
    return rho, n, ""


def load_towns(path: Path, name_field: str, target_pattern: str) -> gpd.GeoDataFrame:
    towns = gpd.read_file(path)
    if name_field not in towns.columns:
        fields = ", ".join(str(field) for field in towns.columns)
        raise KeyError(f"Name field '{name_field}' not found. Available fields: {fields}")
    if towns.crs is None:
        raise ValueError("Town polygon file has no CRS. Define its CRS before processing.")
    # QGIS同梱のpandas/pyarrowの組合せでは .str.fullmatch が失敗するため、reで判定する。
    pattern = re.compile(target_pattern)
    matched = [bool(pattern.fullmatch(str(value))) for value in towns[name_field]]
    towns = towns[matched].copy()
    if towns.empty:
        raise ValueError("No towns matched --target-pattern. Check names and --name-field.")
    towns = towns.to_crs(WORK_CRS)
    # e-Statのファイルには基本単位区単位で同じ町丁目名が繰り返されるため、町丁目単位へ結合する。
    towns = towns.dissolve(by=name_field, as_index=False)[[name_field, "geometry"]]
    return towns.rename(columns={name_field: "town"})


def load_buildings(path: Path, layer: str | None, id_field: str) -> tuple[gpd.GeoDataFrame, dict[str, int]]:
    buildings = gpd.read_file(path, layer=layer) if layer else gpd.read_file(path)
    if buildings.crs is None:
        raise ValueError("Building file has no CRS. Define its CRS before processing.")
    stats = {"input_features": len(buildings)}
    # ogr2ogrはlod2Solidを持つ建物の形状を空で出力する（品川区2025年度版で確認）。件数を記録して除外する。
    empty = buildings.geometry.isna() | buildings.geometry.is_empty
    stats["empty_geometries"] = int(empty.sum())
    buildings = buildings[~empty].copy()
    buildings = buildings[buildings.geom_type.isin(["Polygon", "MultiPolygon"])].copy()
    stats["polygon_features"] = len(buildings)
    # 複数メッシュを結合した入力では同じ建物が重複し得るため、gml_id等で一意にする。
    if id_field in buildings.columns:
        buildings = buildings.drop_duplicates(subset=id_field)
    stats["unique_buildings"] = len(buildings)
    stats["id_field_found"] = int(id_field in buildings.columns)
    # LOD1等の立体は3D座標を持つ。平面上の帰属判定には高さを使わない。
    buildings["geometry"] = force_2d(buildings.geometry.values)
    # ogr2ogr -nlt MULTIPOLYGON でlod1Solidを変換すると、屋根面と底面が重なり壁面が潰れた
    # 不正なMultiPolygonになる。面を結合して平面上の建物外形へ直す。
    invalid = ~buildings.geometry.is_valid
    stats["repaired_invalid_geometries"] = int(invalid.sum())
    buildings.loc[invalid, "geometry"] = [
        get_polygons(geometry) for geometry in make_valid(buildings.geometry[invalid].values, method="structure")
    ]
    buildings = buildings[~buildings.geometry.is_empty].copy()
    return buildings.to_crs(WORK_CRS), stats


def get_polygons(geometry: object) -> object:
    """make_validがGeometryCollectionを返した場合に面だけを残す。"""
    if geometry.geom_type in ("Polygon", "MultiPolygon"):
        return geometry
    return unary_union([part for part in getattr(geometry, "geoms", []) if part.geom_type in ("Polygon", "MultiPolygon")])


def assign_points(buildings: gpd.GeoDataFrame) -> tuple[gpd.GeoSeries, int]:
    """重心を代表点にする。L字形等で重心が建物外に出る場合だけ、建物内部の点で代える。"""
    centroids = buildings.geometry.centroid
    outside = ~buildings.geometry.contains(centroids)
    points = centroids.where(~outside, buildings.geometry.representative_point())
    return gpd.GeoSeries(points, crs=buildings.crs), int(outside.sum())


def count_buildings(towns: gpd.GeoDataFrame, buildings: gpd.GeoDataFrame) -> tuple[dict[str, int], int]:
    points, fallback_count = assign_points(buildings)
    joined = gpd.sjoin(gpd.GeoDataFrame(geometry=points), towns, how="inner", predicate="within")
    counts = joined.groupby("town").size().to_dict()
    return {town: int(counts.get(town, 0)) for town in towns["town"]}, fallback_count


def read_history(path: Path) -> dict[str, dict[str, int]]:
    with path.open(encoding="utf-8") as file:
        return {
            normalize_town_name(row["area"]): {
                "underfloor": int(row["underfloor_buildings"]),
                "abovefloor": int(row["abovefloor_buildings"]),
            }
            for row in csv.DictReader(file)
        }


def read_r7(path: Path) -> dict[str, dict[str, object]]:
    with path.open(encoding="utf-8") as file:
        result: dict[str, dict[str, object]] = {}
        for row in csv.DictReader(file):
            lower, upper = parse_count_class(row["class_label"])
            result[normalize_town_name(row["town"])] = {
                "class_label": row["class_label"],
                "lower": lower,
                "upper": upper,
                "confidence": row["confidence"],
                "class_ordinal": float(row["class_ordinal"]),
            }
        return result


def ratio(numerator: float, denominator: int) -> float:
    return numerator / denominator if denominator > 0 else math.nan


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        for row in rows:
            writer.writerow({key: "" if isinstance(value, float) and math.isnan(value) else value for key, value in row.items()})


def run(args: argparse.Namespace) -> None:
    towns = load_towns(args.towns, args.name_field, args.target_pattern)
    buildings, building_stats = load_buildings(args.buildings, args.buildings_layer, args.id_field)
    counts, centroid_fallbacks = count_buildings(towns, buildings)
    if sum(counts.values()) == 0:
        raise ValueError("No buildings fell inside the target towns. Check the building file's coverage and CRS.")
    empty_towns = [town for town, count in counts.items() if count == 0]

    history = read_history(args.history)
    r7 = read_r7(args.r7)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    count_rows = [
        {"town": town, "building_count": counts[town], "plateau_year": args.plateau_year, "retrieved_at": args.retrieved_at}
        for town in sorted(counts)
    ]
    write_csv(args.output_dir / "building_counts_by_town.csv", count_rows)

    # 実績側の系列（正規化前・後）。町丁目名 → 値。
    series: dict[str, dict[str, float]] = {
        "history_total_buildings": {},
        "history_total_rate": {},
        "history_abovefloor_rate": {},
        "r7_class_ordinal": {},
        "r7_rate_lower": {},
        "r7_rate_upper": {},
    }
    normalized_rows = []
    for town in sorted(counts):
        count = counts[town]
        row: dict[str, object] = {"town": town, "building_count": count}
        if town in history:
            total = history[town]["underfloor"] + history[town]["abovefloor"]
            row |= {
                "history_underfloor_buildings": history[town]["underfloor"],
                "history_abovefloor_buildings": history[town]["abovefloor"],
                "history_total_buildings": total,
                "history_total_rate": ratio(total, count),
                "history_abovefloor_rate": ratio(history[town]["abovefloor"], count),
            }
            series["history_total_buildings"][town] = float(total)
            series["history_total_rate"][town] = row["history_total_rate"]  # type: ignore[assignment]
            series["history_abovefloor_rate"][town] = row["history_abovefloor_rate"]  # type: ignore[assignment]
        else:
            row |= dict.fromkeys(
                ["history_underfloor_buildings", "history_abovefloor_buildings", "history_total_buildings",
                 "history_total_rate", "history_abovefloor_rate"], math.nan)
        if town in r7:
            record = r7[town]
            row |= {
                "r7_class_label": record["class_label"],
                "r7_confidence": record["confidence"],
                "r7_rate_lower": ratio(record["lower"], count),  # type: ignore[arg-type]
                "r7_rate_upper": ratio(record["upper"], count),  # type: ignore[arg-type]
            }
            # 正規化前の比較対象は照合レビュー第2.2章と同じく階級の順序とする。
            series["r7_class_ordinal"][town] = record["class_ordinal"]  # type: ignore[assignment]
            series["r7_rate_lower"][town] = row["r7_rate_lower"]  # type: ignore[assignment]
            series["r7_rate_upper"][town] = row["r7_rate_upper"]  # type: ignore[assignment]
        else:
            row |= dict.fromkeys(["r7_class_label", "r7_confidence", "r7_rate_lower", "r7_rate_upper"], math.nan)
        normalized_rows.append(row)

    # R7.9.11の正規化値は、階級の下限・上限どちらで割っても順位が変わらない場合だけ主要指標にできる。
    lower_ranks = average_ranks({k: v for k, v in series["r7_rate_lower"].items() if not math.isnan(v)})
    upper_ranks = average_ranks({k: v for k, v in series["r7_rate_upper"].items() if not math.isnan(v)})
    r7_upper_defined = set(lower_ranks) == set(upper_ranks) and bool(lower_ranks)
    r7_rank_stable = r7_upper_defined and lower_ranks == upper_ranks
    r7_rank_changed_towns = sorted(k for k in lower_ranks if k in upper_ranks and lower_ranks[k] != upper_ranks[k])
    for row in normalized_rows:
        town = str(row["town"])
        row["r7_rank_by_lower"] = lower_ranks.get(town, math.nan)
        row["r7_rank_by_upper"] = upper_ranks.get(town, math.nan)
    write_csv(args.output_dir / "inundation_history_normalized.csv", normalized_rows)

    target_labels = {
        "history_total_buildings": ("31年累計", "正規化前（浸水棟数）"),
        "history_total_rate": ("31年累計", "正規化後（床下＋床上／建物数）"),
        "history_abovefloor_rate": ("31年累計", "正規化後（床上／建物数）"),
        "r7_class_ordinal": ("R7.9.11", "正規化前（件数階級）"),
        "r7_rate_lower": ("R7.9.11", "正規化後（階級下限／建物数）"),
        "r7_rate_upper": ("R7.9.11", "正規化後（階級上限／建物数）"),
    }
    correlation_rows = []
    for lookup_path in args.risk_lookup:
        lookup = json.loads(lookup_path.read_text(encoding="utf-8"))
        model = {normalize_town_name(name): float(values[args.metric]) for name, values in lookup["towns"].items()}
        for key, (record_name, normalization) in target_labels.items():
            rho, n, note = spearman(model, series[key])
            if key.startswith("r7_rate") and not r7_rank_stable:
                note = (note + " " if note else "") + "階級下限・上限で順位が変わるため参考扱い"
            correlation_rows.append({
                "scenario_id": lookup.get("scenario_id", lookup_path.parent.name),
                "model_metric": args.metric,
                "record": record_name,
                "target": key,
                "normalization": normalization,
                "n": n,
                "spearman_rho": "" if rho is None else round(rho, 4),
                "note": note,
            })
    if correlation_rows:
        write_csv(args.output_dir / "rank_correlation_normalization.csv", correlation_rows)

    metadata = {
        "phase": "PLATEAU導入計画 フェーズ0B",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "inputs": {
            "buildings": str(args.buildings),
            "buildings_layer": args.buildings_layer,
            "towns": str(args.towns),
            "history": str(args.history),
            "r7": str(args.r7),
            "risk_lookup": [str(path) for path in args.risk_lookup],
        },
        "plateau_year": args.plateau_year,
        "retrieved_at": args.retrieved_at,
        "work_crs": WORK_CRS,
        "assignment_rule": "建物ポリゴンの重心が含まれる町丁目に割り当てる。重心が建物外の場合は建物内部の代表点を使う。",
        "building_stats": building_stats | {"centroid_outside_footprint": centroid_fallbacks},
        "towns_without_buildings": empty_towns,
        "r7_rank_stable_between_class_bounds": r7_rank_stable,
        "r7_rank_changed_towns": r7_rank_changed_towns,
        "r7_upper_bound_defined_for_all": r7_upper_defined,
        "limitations": [
            "PLATEAUの整備年度と実績の対象期間（1989〜2020年、2025年9月11日）は一致せず、建て替え・新築による建物数の変化は補正していない。",
            "R7.9.11実績は件数の階級であり、正規化後の率は階級の下限・上限の幅を持つ。",
            "照合できる町丁目は9〜10であり、順位相関の小さな差を改善・悪化と判定しない（PLATEAU導入計画 2.1節）。",
            "正規化後の値は検証用の町丁目単位の相対比較であり、個別建物の浸水や避難判断の根拠にしない。",
        ],
    }
    (args.output_dir / "building_counts_run_metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"Counted {sum(counts.values())} buildings in {len(counts)} towns -> {args.output_dir}")
    if empty_towns:
        print(f"WARNING: no buildings in {', '.join(empty_towns)}. Check PLATEAU coverage.")
    if building_stats["empty_geometries"]:
        print(
            f"WARNING: {building_stats['empty_geometries']} buildings had empty geometry and were skipped. "
            "Check that none lie in the target towns (e.g. LOD2 buildings converted by ogr2ogr)."
        )
    print(f"R7.9.11 rank stable between class bounds: {r7_rank_stable}")
    for row in correlation_rows:
        print(f"  {row['scenario_id']:<32} {row['target']:<24} n={row['n']} rho={row['spearman_rho'] or '-'} {row['note']}")


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[1]
    processed = root / "data/naisui_poc/02_processed"
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--buildings", type=Path, required=True, help="PLATEAU bldgを変換したGeoPackage/GeoJSON等")
    parser.add_argument("--buildings-layer", help="GeoPackage内の建築物レイヤー名（複数レイヤーがある場合）")
    parser.add_argument("--id-field", default="gml_id", help="重複除去に使う建物ID列")
    parser.add_argument("--plateau-year", required=True, help="PLATEAUデータの整備年度（例: 2023）")
    parser.add_argument("--retrieved-at", required=True, help="PLATEAUデータの取得日（例: 2026-09-26）")
    parser.add_argument(
        "--towns",
        type=Path,
        default=root / "data/naisui_poc/01_raw/boundaries/r2kb13109.shp",
        help="町丁目ポリゴン（GeoJSON、GPKG、Shapefile等）",
    )
    parser.add_argument("--name-field", default="S_NAME", help="町丁目名を格納した属性列")
    parser.add_argument("--target-pattern", default=TARGET_TOWN_PATTERN, help="対象町丁目名を選ぶ正規表現")
    parser.add_argument("--history", type=Path, default=processed / "shinagawa_inundation_history_target.csv")
    parser.add_argument("--r7", type=Path, default=processed / "shinagawa_inundation_r7_0911_target.csv")
    parser.add_argument(
        "--risk-lookup",
        type=Path,
        nargs="*",
        default=[
            processed
            / "pysheds_surface_routing/sc_153mmh_24h_690mm_official/risk_lookup_sc_153mmh_24h_690mm_official.json"
        ],
        help="順位相関を取るモデル側のrisk_lookup JSON（複数可、空なら相関を計算しない）",
    )
    parser.add_argument("--metric", default="area_over_threshold_ratio", help="risk_lookup内のモデル指標")
    parser.add_argument("--output-dir", type=Path, default=processed / "plateau")
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
