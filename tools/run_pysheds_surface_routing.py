"""Run a mass-conserving, depression-storage surface-routing screening model.

This is an experimental PoC model. Pysheds is used to condition the DEM and
derive D8 paths. Excess rainfall is routed once along those paths, retained up
to the original depression capacity, then passed downstream as overflow.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np
import rasterio
from pysheds.grid import Grid

from run_surface_water_balance import DemMosaic, ground_cell_areas_m2, load_dem_tiles, load_scenario, write_geotiff

# pysheds 0.4.x calls the removed NumPy 1.x alias internally.
if not hasattr(np, "in1d"):
    np.in1d = np.isin  # type: ignore[attr-defined]


D8_OFFSETS = {64: (-1, 0), 128: (-1, 1), 1: (0, 1), 2: (1, 1), 4: (1, 0), 8: (1, -1), 16: (0, -1), 32: (-1, -1)}


def d8_destinations(flow_direction: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """Create flat downstream indexes from pysheds' default D8 encoding."""
    rows, cols = np.indices(flow_direction.shape)
    destination = np.full(flow_direction.shape, -1, dtype=np.int64)
    for code, (row_offset, col_offset) in D8_OFFSETS.items():
        target_row = rows + row_offset
        target_col = cols + col_offset
        in_bounds = (
            (target_row >= 0)
            & (target_row < flow_direction.shape[0])
            & (target_col >= 0)
            & (target_col < flow_direction.shape[1])
        )
        use = (flow_direction == code) & in_bounds
        target_flat = target_row * flow_direction.shape[1] + target_col
        destination[use] = target_flat[use]
    destination[~valid] = -1
    return destination


def route_step(
    local_excess_m3: np.ndarray,
    stored_m3: np.ndarray,
    storage_capacity_m3: np.ndarray,
    drainage_m3_per_cell: np.ndarray,
    destination: np.ndarray,
    downstream_order: np.ndarray,
) -> tuple[np.ndarray, float]:
    """Route local excess once; retain in depressions and pass only overflow onward.

    Returns the new storage and the volume (m³) that left the domain at terrain outlets.
    """
    stored = np.maximum(0.0, stored_m3 - drainage_m3_per_cell)
    incoming = local_excess_m3.ravel().astype(np.float64, copy=True)
    stored_flat = stored.ravel()
    capacity_flat = storage_capacity_m3.ravel()
    destination_flat = destination.ravel()
    outflow_m3 = 0.0

    for source in downstream_order:
        water = incoming[source]
        if water <= 0:
            continue
        available = max(0.0, capacity_flat[source] - stored_flat[source])
        retained = min(water, available)
        stored_flat[source] += retained
        overflow = water - retained
        target = destination_flat[source]
        if overflow > 0 and target >= 0:
            incoming[target] += overflow
        elif overflow > 0:
            # At a terrain outlet, overflow intentionally leaves the analysis domain.
            outflow_m3 += overflow
    return stored, outflow_m3


D8_DISTANCE = {code: (2**0.5 if row_offset and col_offset else 1.0) for code, (row_offset, col_offset) in D8_OFFSETS.items()}


def reroute_flow(
    destination: np.ndarray,
    conditioned_dem: np.ndarray,
    valid: np.ndarray,
    blocked: np.ndarray,
    preferred: np.ndarray | None = None,
) -> tuple[np.ndarray, dict[str, int]]:
    """建物・道路に応じてD8の流下先を付け替える（PLATEAU導入計画フェーズ2）。

    候補は、整形DEMで厳密に低く、blocked（建物）でない隣接セル。preferred（道路）の候補が
    あれば、その中で最も急な方向へ流す。無ければ、元の流下先が建物でない限りそのまま残し、
    建物なら候補全体で最も急な方向へ流す。候補が無い場合は元の流下先を残す。流下先は常に整形DEMで低いセルなので、downstream_order
    （整形DEMの降順）の処理順は保たれ、循環も生じない。
    """
    rows, cols = np.indices(conditioned_dem.shape)
    height, width = conditioned_dem.shape
    best_slope = np.zeros(conditioned_dem.shape, dtype=np.float64)
    best_target = np.full(conditioned_dem.shape, -1, dtype=np.int64)
    preferred_slope = np.zeros(conditioned_dem.shape, dtype=np.float64)
    preferred_target = np.full(conditioned_dem.shape, -1, dtype=np.int64)
    for code, (row_offset, col_offset) in D8_OFFSETS.items():
        target_row = rows + row_offset
        target_col = cols + col_offset
        inside = (target_row >= 0) & (target_row < height) & (target_col >= 0) & (target_col < width)
        target_row = np.clip(target_row, 0, height - 1)
        target_col = np.clip(target_col, 0, width - 1)
        target_flat = target_row * width + target_col
        slope = (conditioned_dem - conditioned_dem[target_row, target_col]) / D8_DISTANCE[code]
        candidate = inside & valid & valid[target_row, target_col] & ~blocked[target_row, target_col]
        usable = candidate & (slope > best_slope)
        best_slope = np.where(usable, slope, best_slope)
        best_target = np.where(usable, target_flat, best_target)
        if preferred is not None:
            usable = candidate & preferred[target_row, target_col] & (slope > preferred_slope)
            preferred_slope = np.where(usable, slope, preferred_slope)
            preferred_target = np.where(usable, target_flat, preferred_target)
    # 付け替えは最小限にする。道路へ流せない場合、元の流下先が建物でなければ元のまま残す。
    original_target = np.maximum(destination, 0)
    into_blocked = valid & (destination >= 0) & blocked.ravel()[original_target].reshape(destination.shape)
    original_ok = valid & (destination >= 0) & ~into_blocked
    chosen = np.where(preferred_target >= 0, preferred_target, np.where(original_ok, destination, best_target))
    new_destination = np.where(chosen >= 0, chosen, destination)
    new_destination[~valid] = -1
    stats = {
        "rerouted_cells": int(np.count_nonzero(valid & (new_destination != destination))),
        # 建物以外のセルで、低い建物以外の隣接セルが無いため建物へ流れ続けるもの（格子の粗さによる近似の限界）。
        "open_cells_still_draining_into_buildings": int(np.count_nonzero(into_blocked & (chosen < 0) & ~blocked)),
    }
    if preferred is not None:
        was_preferred = (destination >= 0) & preferred.ravel()[original_target].reshape(destination.shape)
        stats["cells_steered_to_roads"] = int(np.count_nonzero(valid & (preferred_target >= 0) & ~was_preferred))
    return new_destination, stats


def load_runoff_coefficient(path: Path, mosaic: DemMosaic) -> np.ndarray:
    """セル別流出係数ラスタを読む。DEMと同じ格子でなければ誤った位置に係数が付くため拒否する。"""
    with rasterio.open(path) as dataset:
        same_grid = (
            dataset.shape == mosaic.elevation_m.shape
            and dataset.transform.almost_equals(mosaic.transform)
            and str(dataset.crs) == str(mosaic.crs)
        )
        if not same_grid:
            raise ValueError(f"Runoff coefficient raster does not match the DEM grid: {path}")
        coefficient = dataset.read(1).astype(np.float64)
    if not np.all(np.isfinite(coefficient)) or coefficient.min() < 0 or coefficient.max() > 1:
        raise ValueError("Runoff coefficients must be finite and between 0 and 1.")
    return coefficient


def load_fraction_band(path: Path, mosaic: DemMosaic, band_name: str) -> np.ndarray:
    """surface_fraction の指定区分のバンドを読む。DEMと同じ格子であることを確認する。"""
    with rasterio.open(path) as dataset:
        if not (
            dataset.shape == mosaic.elevation_m.shape
            and dataset.transform.almost_equals(mosaic.transform)
            and str(dataset.crs) == str(mosaic.crs)
        ):
            raise ValueError(f"Surface fraction raster does not match the DEM grid: {path}")
        bands = [index for index, name in enumerate(dataset.descriptions, start=1) if name == band_name]
        if not bands:
            raise ValueError(f"No '{band_name}' band in {path}")
        return dataset.read(bands[0]).astype(np.float64)


def run(args: argparse.Namespace) -> None:
    config = json.loads(args.params.read_text(encoding="utf-8"))
    drainage_mmh = float(config["drainage_capacity"]["value_mm_per_hr"])
    scenario_id, scenario = load_scenario(args.scenario, drainage_mmh, args.scenario_id)
    output = args.output / scenario_id
    output.mkdir(parents=True, exist_ok=True)

    if args.dem:
        with rasterio.open(args.dem) as dataset:
            source = dataset.read(1, masked=True)
            elevation = np.asarray(source.filled(np.nan), dtype=np.float32)
            mosaic = DemMosaic(elevation, dataset.transform, str(dataset.crs))
        dem_path = args.dem
    else:
        mosaic = load_dem_tiles(args.dem_tiles, args.zoom)
        dem_path = output / "dem_raw_epsg3857.tif"
        write_geotiff(dem_path, mosaic.elevation_m, mosaic)

    grid = Grid.from_raster(str(dem_path))
    dem = grid.read_raster(str(dem_path))
    raw_dem = np.asarray(dem, dtype=np.float64)
    valid = np.isfinite(raw_dem) & (raw_dem > -9000)
    pits_filled = grid.fill_pits(dem)
    depressions_filled = grid.fill_depressions(pits_filled)
    conditioned_dem = grid.resolve_flats(depressions_filled)
    flow_direction = grid.flowdir(conditioned_dem, routing="d8")
    flow_accumulation = grid.accumulation(flow_direction, routing="d8")

    depression_depth_m = np.maximum(0.0, np.asarray(depressions_filled) - raw_dem)
    depression_depth_m[~valid] = 0.0
    depression_depth_m[depression_depth_m < args.depression_threshold_m] = 0.0
    if args.max_depression_depth_m is not None:
        depression_depth_m = np.minimum(depression_depth_m, args.max_depression_depth_m)
    destination = d8_destinations(np.asarray(flow_direction), valid)
    downstream_order = np.argsort(np.where(valid, np.asarray(conditioned_dem), -np.inf).ravel())[::-1]

    # EPSG:3857では名目の画素面積が地上面積の約1.5倍になるため、行ごとの地上面積を使う。
    cell_area_m2 = np.broadcast_to(ground_cell_areas_m2(mosaic.transform, mosaic.crs, raw_dem.shape[0]), raw_dem.shape)
    # セル別流出係数（PLATEAU導入計画フェーズ1）。省略時は降雨シナリオの一律値を使う。
    runoff_coefficient = load_runoff_coefficient(args.runoff_coefficient_raster, mosaic) if args.runoff_coefficient_raster else None
    if runoff_coefficient is not None and any(row["runoff_coefficient"] != 1.0 for row in scenario):
        raise ValueError("Use a scenario with runoff_coefficient=1.0 together with --runoff-coefficient-raster to avoid applying both.")
    storage_capacity_m3 = depression_depth_m * cell_area_m2
    # 建物・道路による流下の変更（PLATEAU導入計画フェーズ2）。建物セルは貯留せず、水を流し込まない。
    # 道路セルは、低い隣接セルに道路があればそちらへ優先して流す（地形は変えない）。
    surface_stats: dict[str, object] | None = None
    if args.building_fraction_raster or args.road_fraction_raster:
        building = np.zeros_like(valid)
        road: np.ndarray | None = None
        surface_stats = {}
        if args.building_fraction_raster:
            building = (load_fraction_band(args.building_fraction_raster, mosaic, "建物・屋根") >= args.building_threshold) & valid
            storage_capacity_m3 = np.where(building, 0.0, storage_capacity_m3)
            surface_stats |= {
                "building_fraction_raster": str(args.building_fraction_raster),
                "building_threshold": args.building_threshold,
                "building_cells": int(np.count_nonzero(building)),
                "building_cell_share": float(np.count_nonzero(building) / np.count_nonzero(valid)),
                "storage_removed_m3": float(np.sum(depression_depth_m[building] * cell_area_m2[building])),
            }
        if args.road_fraction_raster:
            road = (load_fraction_band(args.road_fraction_raster, mosaic, "道路・舗装") >= args.road_threshold) & valid & ~building
            surface_stats |= {
                "road_fraction_raster": str(args.road_fraction_raster),
                "road_threshold": args.road_threshold,
                "road_cells": int(np.count_nonzero(road)),
                "road_cell_share": float(np.count_nonzero(road) / np.count_nonzero(valid)),
            }
        destination, reroute_stats = reroute_flow(
            destination, np.asarray(conditioned_dem, dtype=np.float64), valid, building, road
        )
        surface_stats |= reroute_stats
    stored_m3 = np.zeros_like(raw_dem, dtype=np.float64)
    maximum_depth_m = np.zeros_like(raw_dem, dtype=np.float32)
    summary: list[dict[str, float]] = []
    for step, row in enumerate(scenario, start=1):
        step_minutes = row.get("duration_min", args.step_minutes)
        step_hours = step_minutes / 60.0
        drainage_m3_per_cell = drainage_mmh / 1000.0 * step_hours * cell_area_m2
        if runoff_coefficient is None:
            excess_m = max(0.0, row["rainfall_mm_hr"] * row["runoff_coefficient"] - row["capacity_mm_hr"]) / 1000.0 * step_hours
        else:
            excess_m = np.maximum(0.0, row["rainfall_mm_hr"] * runoff_coefficient - row["capacity_mm_hr"]) / 1000.0 * step_hours
        local_excess_m3 = np.where(valid, excess_m * cell_area_m2, 0.0)
        previous_total_m3 = float(np.sum(stored_m3))
        drained_m3 = float(np.sum(np.minimum(stored_m3, drainage_m3_per_cell)))
        stored_m3, outflow_m3 = route_step(
            local_excess_m3, stored_m3, storage_capacity_m3, drainage_m3_per_cell, destination, downstream_order
        )
        input_m3 = float(np.sum(local_excess_m3))
        # 水量保存の点検: 前ステップの貯留 + 流入 − 排水 − 域外流出 = 今ステップの貯留
        balance_residual_m3 = previous_total_m3 + input_m3 - drained_m3 - outflow_m3 - float(np.sum(stored_m3))
        depth_m = (stored_m3 / cell_area_m2).astype(np.float32)
        maximum_depth_m = np.maximum(maximum_depth_m, depth_m)
        elapsed_min = row["elapsed_time_min"] + step_minutes
        write_geotiff(output / f"ponding_depth_t{elapsed_min:g}min.tif", depth_m, mosaic)
        summary.append(
            {
                "step": step,
                "elapsed_time_min": elapsed_min,
                "duration_min": step_minutes,
                "rainfall_mm_hr": row["rainfall_mm_hr"],
                "maximum_depth_m": float(np.max(depth_m[valid])),
                "stored_volume_m3": float(np.sum(stored_m3[valid])),
                "ponded_area_m2": float(np.sum(cell_area_m2[valid & (depth_m >= args.ponding_threshold_m)])),
                "input_m3": input_m3,
                "drained_m3": drained_m3,
                "outflow_m3": outflow_m3,
                "balance_residual_m3": balance_residual_m3,
            }
        )

    write_geotiff(output / "maximum_ponding_depth_m.tif", maximum_depth_m, mosaic)
    grid.to_raster(depressions_filled, str(output / "dem_depressions_filled.tif"))
    grid.to_raster(conditioned_dem, str(output / "dem_conditioned.tif"))
    grid.to_raster(flow_direction, str(output / "flow_direction_d8_pysheds.tif"))
    grid.to_raster(flow_accumulation, str(output / "flow_accumulation_cells_pysheds.tif"))
    write_geotiff(output / "depression_depth_m.tif", depression_depth_m.astype(np.float32), mosaic)
    with (output / "water_balance_summary.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)
    (output / "run_metadata.json").write_text(
        json.dumps(
            {
                "scenario_id": scenario_id,
                "model": "experimental pysheds D8 routing with depression capacity and overflow",
                "depression_threshold_m": args.depression_threshold_m,
                "max_depression_depth_m": args.max_depression_depth_m,
                "runoff_coefficient_raster": str(args.runoff_coefficient_raster) if args.runoff_coefficient_raster else None,
                "runoff_coefficient_mean": float(runoff_coefficient[valid].mean()) if runoff_coefficient is not None else None,
                "cell_area_m2_range": [float(cell_area_m2.min()), float(cell_area_m2.max())],
                "cell_area_note": "体積・面積は楕円体上の地上面積で計算（EPSG:3857の名目画素面積は使わない）",
                "surface_obstacles": surface_stats,
                "limitations": [
                    "地形由来の窪地容量を用いる簡易モデルであり、道路縁石、建物、下水道、雨水ます、ポンプは表現しない。",
                    "ハザード区域・実績地点との校正前であり、避難判断や個別地点の浸水予報に使用しない。",
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Wrote experimental pysheds routing results to {output}")


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario-id", required=True)
    parser.add_argument("--dem-tiles", type=Path, default=root / "data/naisui_poc/01_raw/dem/gsi_dem5a_png_z15")
    parser.add_argument("--dem", type=Path, help="解析対象DEM GeoTIFF。指定時は--dem-tilesを使わない。")
    parser.add_argument("--params", type=Path, default=root / "data/naisui_poc/02_processed/model_input/drainage_params.json")
    parser.add_argument("--scenario", type=Path, default=root / "data/naisui_poc/03_scenarios/rainfall_scenarios.csv")
    parser.add_argument("--output", type=Path, default=root / "data/naisui_poc/02_processed/pysheds_surface_routing")
    parser.add_argument("--zoom", type=int, default=15)
    parser.add_argument("--step-minutes", type=float, default=10.0)
    parser.add_argument("--depression-threshold-m", type=float, default=0.01)
    parser.add_argument("--max-depression-depth-m", type=float, help="感度分析用の凹地容量上限。省略時は上限なし。")
    parser.add_argument("--ponding-threshold-m", type=float, default=0.01)
    parser.add_argument(
        "--building-fraction-raster",
        type=Path,
        help="建物・屋根の面積割合を含むGeoTIFF（tools/rasterize_surface_parameters.py の surface_fraction）。"
        "指定すると建物セルへの流入と貯留を止める。",
    )
    parser.add_argument("--building-threshold", type=float, default=0.5, help="建物セルとみなす建物・屋根の面積割合")
    parser.add_argument(
        "--road-fraction-raster",
        type=Path,
        help="道路・舗装の面積割合を含むGeoTIFF（surface_fraction）。指定すると道路セルへ優先して流す。",
    )
    parser.add_argument("--road-threshold", type=float, default=0.5, help="道路セルとみなす道路・舗装の面積割合")
    parser.add_argument(
        "--runoff-coefficient-raster",
        type=Path,
        help="セル別流出係数GeoTIFF（tools/rasterize_surface_parameters.py の出力）。DEMと同じ格子であること。",
    )
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
