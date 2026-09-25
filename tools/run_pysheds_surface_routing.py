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

from run_surface_water_balance import DemMosaic, load_dem_tiles, load_scenario, write_geotiff

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
    drainage_m3_per_cell: float,
    destination: np.ndarray,
    downstream_order: np.ndarray,
) -> np.ndarray:
    """Route local excess once; retain in depressions and pass only overflow onward."""
    stored = np.maximum(0.0, stored_m3 - drainage_m3_per_cell)
    incoming = local_excess_m3.ravel().astype(np.float64, copy=True)
    stored_flat = stored.ravel()
    capacity_flat = storage_capacity_m3.ravel()
    destination_flat = destination.ravel()

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
        # At a terrain outlet, overflow intentionally leaves the analysis domain.
    return stored


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

    cell_area_m2 = abs(mosaic.transform.a * mosaic.transform.e)
    # セル別流出係数（PLATEAU導入計画フェーズ1）。省略時は降雨シナリオの一律値を使う。
    runoff_coefficient = load_runoff_coefficient(args.runoff_coefficient_raster, mosaic) if args.runoff_coefficient_raster else None
    if runoff_coefficient is not None and any(row["runoff_coefficient"] != 1.0 for row in scenario):
        raise ValueError("Use a scenario with runoff_coefficient=1.0 together with --runoff-coefficient-raster to avoid applying both.")
    storage_capacity_m3 = depression_depth_m * cell_area_m2
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
        stored_m3 = route_step(
            local_excess_m3, stored_m3, storage_capacity_m3, drainage_m3_per_cell, destination, downstream_order
        )
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
                "ponded_area_m2": float(np.count_nonzero(depth_m[valid] >= args.ponding_threshold_m)) * cell_area_m2,
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
        "--runoff-coefficient-raster",
        type=Path,
        help="セル別流出係数GeoTIFF（tools/rasterize_surface_parameters.py の出力）。DEMと同じ格子であること。",
    )
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
