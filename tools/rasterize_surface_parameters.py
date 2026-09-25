"""Rasterize PLATEAU land use and buildings onto the model grid as per-cell runoff coefficients.

フェーズ1（docs/01_概要・計画/PLATEAU導入計画.md）の入力ラスタを作る。モデル本体は変更しない。

1. モデルと同じ格子（--template のDEM）を細分割した格子に、土地利用区画の区分
   （landuse_category_mapping.csv の category_outside_buildings）を焼き、その上に
   建物外形を「建物・屋根」として焼く。
2. 細分割格子を集計し、モデル格子ごとに5区分の面積割合を求める（二値化しない）。
3. 区分ごとの流出係数（landuse_parameter_mapping.csv）を面積で重み付け平均する。

流出係数は浸透による損失を含む値と定義する（工種別基礎流出係数）。フェーズ1では浸透能を
別に差し引かないため、infiltration_capacity ラスタは作らない（二重計上の防止）。
土地利用・建物の無いセルは、現行モデルと同じ流出係数1.0とする。

出力（既定では data/naisui_poc/02_processed/model_input/）:
  surface_fraction_<version>.tif              5区分＋データ無しの面積割合（6バンド）
  runoff_coefficient_<version>_<column>.tif   列ごとのセル別流出係数（base、low、high）
  surface_parameters_<version>_metadata.json  入力・係数表・集計値
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.features import rasterize
from rasterio.transform import Affine
from shapely.geometry import box

from count_buildings_by_town import TARGET_TOWN_PATTERN, load_buildings, load_towns


CATEGORIES = ["建物・屋根", "道路・舗装", "駐車場等の不浸透面", "緑地", "水面・その他"]
NO_DATA_FALLBACK_COEFFICIENT = 1.0  # 現行モデルの一律値


def load_parameters(path: Path, columns: list[str]) -> pd.DataFrame:
    parameters = pd.read_csv(path).set_index("category")
    missing = [category for category in CATEGORIES if category not in parameters.index]
    if missing:
        raise ValueError(f"Categories missing from parameter table: {missing}")
    for column in columns:
        name = f"runoff_coefficient_{column}"
        if name not in parameters.columns:
            raise KeyError(f"Column '{name}' not found in {path}")
        values = parameters.loc[CATEGORIES, name]
        if ((values < 0) | (values > 1)).any():
            raise ValueError(f"Runoff coefficients in '{name}' must be between 0 and 1.")
    return parameters


def fine_category_grid(
    template: rasterio.DatasetReader,
    supersample: int,
    landuse: gpd.GeoDataFrame,
    category_by_code: dict[int, str],
    buildings: gpd.GeoDataFrame,
) -> np.ndarray:
    """0=データ無し、1〜5=CATEGORIESの順。土地利用を焼いた後に建物を上書きする。"""
    shape = (template.height * supersample, template.width * supersample)
    transform = template.transform * Affine.scale(1 / supersample)
    category_index = {category: index + 1 for index, category in enumerate(CATEGORIES)}
    landuse_shapes = (
        (geometry, category_index[category_by_code.get(code, "水面・その他")])
        for geometry, code in zip(landuse.geometry, landuse["orgLandUse"])
    )
    fine = rasterize(landuse_shapes, out_shape=shape, transform=transform, fill=0, dtype="uint8")
    rasterize(
        ((geometry, category_index["建物・屋根"]) for geometry in buildings.geometry),
        out=fine,
        transform=transform,
        dtype="uint8",
    )
    return fine


def block_fractions(fine: np.ndarray, supersample: int) -> np.ndarray:
    """細分割格子を集計し、(区分数+1, 行, 列) の面積割合を返す。バンド0がデータ無し。"""
    rows, cols = fine.shape[0] // supersample, fine.shape[1] // supersample
    blocks = fine.reshape(rows, supersample, cols, supersample)
    fractions = np.empty((len(CATEGORIES) + 1, rows, cols), dtype=np.float32)
    for index in range(len(CATEGORIES) + 1):
        fractions[index] = (blocks == index).mean(axis=(1, 3))
    return fractions


def write_raster(path: Path, data: np.ndarray, template: rasterio.DatasetReader, descriptions: list[str]) -> None:
    profile = template.profile | {
        "driver": "GTiff",
        "count": data.shape[0],
        "dtype": "float32",
        "nodata": None,
        "compress": "deflate",
    }
    with rasterio.open(path, "w", **profile) as dataset:
        dataset.write(data.astype(np.float32))
        for band, description in enumerate(descriptions, start=1):
            dataset.set_band_description(band, description)


def run(args: argparse.Namespace) -> None:
    parameters = load_parameters(args.parameters, args.columns)
    mapping = pd.read_csv(args.category_mapping, dtype={"org_land_use": int})
    category_by_code = dict(zip(mapping["org_land_use"], mapping["category_outside_buildings"]))

    with rasterio.open(args.template) as template:
        grid_bounds = box(*template.bounds)
        grid_crs = template.crs
        grid_info = {"crs": str(grid_crs), "width": template.width, "height": template.height, "transform": list(template.transform)[:6]}
        bbox_6668 = tuple(gpd.GeoSeries([grid_bounds], crs=grid_crs).to_crs("EPSG:6668").total_bounds)

        landuse = gpd.read_file(args.landuse, bbox=bbox_6668).to_crs(grid_crs)
        landuse["orgLandUse"] = landuse["orgLandUse"].fillna(0).astype(int)
        unmapped = sorted(set(landuse["orgLandUse"]) - set(category_by_code))
        buildings, building_stats = load_buildings(args.buildings, args.buildings_layer, args.id_field)
        buildings = buildings.to_crs(grid_crs)
        buildings = buildings[buildings.intersects(grid_bounds)]

        fine = fine_category_grid(template, args.supersample, landuse, category_by_code, buildings)
        fractions = block_fractions(fine, args.supersample)
        del fine

        args.output_dir.mkdir(parents=True, exist_ok=True)
        write_raster(
            args.output_dir / f"surface_fraction_{args.version}.tif",
            fractions,
            template,
            ["データ無し", *CATEGORIES],
        )
        coefficient_summary: dict[str, dict[str, float]] = {}
        towns = load_towns(args.towns, args.name_field, args.target_pattern).to_crs(grid_crs)
        target_mask = rasterize(
            ((geometry, 1) for geometry in towns.geometry),
            out_shape=(template.height, template.width),
            transform=template.transform,
            fill=0,
            dtype="uint8",
        ).astype(bool)
        for column in args.columns:
            values = parameters.loc[CATEGORIES, f"runoff_coefficient_{column}"].to_numpy(dtype=np.float32)
            coefficient = fractions[0] * NO_DATA_FALLBACK_COEFFICIENT + np.tensordot(values, fractions[1:], axes=1)
            write_raster(
                args.output_dir / f"runoff_coefficient_{args.version}_{column}.tif",
                coefficient[np.newaxis],
                template,
                [f"runoff_coefficient_{column}"],
            )
            coefficient_summary[column] = {
                "grid_mean": round(float(coefficient.mean()), 4),
                "grid_min": round(float(coefficient.min()), 4),
                "target_towns_mean": round(float(coefficient[target_mask].mean()), 4),
                "target_towns_p05": round(float(np.percentile(coefficient[target_mask], 5)), 4),
            }

    fraction_summary = {
        name: {
            "grid_mean": round(float(fractions[index].mean()), 4),
            "target_towns_mean": round(float(fractions[index][target_mask].mean()), 4),
        }
        for index, name in enumerate(["データ無し", *CATEGORIES])
    }
    metadata = {
        "phase": "PLATEAU導入計画 フェーズ1（入力ラスタ）",
        "version": args.version,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "inputs": {
            "template": str(args.template),
            "landuse": str(args.landuse),
            "buildings": str(args.buildings),
            "category_mapping": str(args.category_mapping),
            "parameters": str(args.parameters),
        },
        "grid": grid_info,
        "supersample": args.supersample,
        "coefficient_definition": "流出係数は浸透損失を含む（工種別基礎流出係数）。浸透能は別に差し引かない。",
        "no_data_fallback_coefficient": NO_DATA_FALLBACK_COEFFICIENT,
        "parameter_table": parameters.loc[CATEGORIES].reset_index().to_dict(orient="records"),
        "landuse_features": len(landuse),
        "unmapped_land_use_codes": unmapped,
        "buildings_in_grid": len(buildings),
        "building_stats": building_stats,
        "fraction_summary": fraction_summary,
        "runoff_coefficient_summary": coefficient_summary,
        "limitations": [
            "土地利用は2021年調査、建物は2025年度整備であり、時点が一致しない。",
            "建物データが格子全体を覆っていない場合、建物のあるべき区画は分類対応表の建物外区分で扱われる。building_statsと入力メッシュを確認すること。",
            "区分ごとの係数は指針の標準値であり、品川区の実測で校正したものではない。",
        ],
    }
    (args.output_dir / f"surface_parameters_{args.version}_metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"Wrote surface parameters '{args.version}' to {args.output_dir}")
    print(f"  land-use parcels: {len(landuse)}, buildings: {len(buildings)}, unmapped codes: {unmapped or 'none'}")
    for name, summary in fraction_summary.items():
        print(f"  fraction {name:<12} grid={summary['grid_mean']:.1%} towns={summary['target_towns_mean']:.1%}")
    for column, summary in coefficient_summary.items():
        print(f"  runoff_coefficient_{column}: grid mean={summary['grid_mean']} towns mean={summary['target_towns_mean']}")


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[1]
    processed = root / "data/naisui_poc/02_processed"
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", required=True, help="出力ファイル名に付ける版（例: plateau2025_v1）")
    parser.add_argument(
        "--template",
        type=Path,
        default=processed / "pysheds_surface_routing/sc_100mm_extreme/dem_raw_epsg3857.tif",
        help="モデル格子のDEM。採用モデルは sc_100mm_extreme のDEMを全シナリオで再利用している",
    )
    parser.add_argument("--landuse", type=Path, default=processed / "plateau/luse_2025.gpkg")
    parser.add_argument("--buildings", type=Path, default=processed / "plateau/bldg_2025_lod0.gpkg")
    parser.add_argument("--buildings-layer", help="GeoPackage内の建築物レイヤー名（複数レイヤーがある場合）")
    parser.add_argument("--id-field", default="gml_id", help="建物の重複除去に使うID列")
    parser.add_argument("--category-mapping", type=Path, default=processed / "plateau/landuse_category_mapping.csv")
    parser.add_argument("--parameters", type=Path, default=processed / "model_input/landuse_parameter_mapping.csv")
    parser.add_argument("--columns", nargs="+", default=["base", "low", "high"], help="出力する流出係数の列")
    parser.add_argument("--supersample", type=int, default=8, help="1セルを何×何に細分割して面積割合を求めるか")
    parser.add_argument(
        "--towns",
        type=Path,
        default=root / "data/naisui_poc/01_raw/boundaries/r2kb13109.shp",
        help="集計値を出す対象町丁目のポリゴン",
    )
    parser.add_argument("--name-field", default="S_NAME", help="町丁目名を格納した属性列")
    parser.add_argument("--target-pattern", default=TARGET_TOWN_PATTERN, help="対象町丁目名を選ぶ正規表現")
    parser.add_argument("--output-dir", type=Path, default=processed / "model_input")
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
