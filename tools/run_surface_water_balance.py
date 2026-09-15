"""Run a screening-level 2D surface-water balance model for Nakanobu/Futaba.

Inputs are GSI DEM PNG tiles, a uniform equivalent drainage capacity, and a
rainfall time series. Outputs are GeoTIFFs in EPSG:3857 plus a CSV summary.
This is deliberately not a replacement for a 1D/2D hydraulic model.
"""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import rasterio
from PIL import Image
from rasterio.transform import from_bounds


WEB_MERCATOR_HALF_WORLD_M = 20037508.342789244
TILE_SIZE_PX = 256
NODATA_VALUE = -9999.0


@dataclass(frozen=True)
class DemMosaic:
    elevation_m: np.ndarray
    transform: rasterio.Affine
    crs: str


def decode_gsi_elevation(path: Path) -> np.ndarray:
    """Decode a GSI DEM PNG tile to elevations in metres."""
    rgba = np.asarray(Image.open(path).convert("RGBA"), dtype=np.int64)
    encoded = rgba[..., 0] * 256 * 256 + rgba[..., 1] * 256 + rgba[..., 2]
    signed = np.where(encoded < 2**23, encoded, encoded - 2**24)
    elevation = signed.astype(np.float32) * 0.01
    elevation[rgba[..., 3] == 0] = np.nan
    return elevation


def tile_bounds_mercator(zoom: int, x: int, y: int) -> tuple[float, float, float, float]:
    tiles_per_axis = 2**zoom
    tile_width = (2 * WEB_MERCATOR_HALF_WORLD_M) / tiles_per_axis
    left = -WEB_MERCATOR_HALF_WORLD_M + x * tile_width
    right = left + tile_width
    top = WEB_MERCATOR_HALF_WORLD_M - y * tile_width
    bottom = top - tile_width
    return left, bottom, right, top


def load_dem_tiles(tile_dir: Path, zoom: int) -> DemMosaic:
    tiles: dict[tuple[int, int], np.ndarray] = {}
    for path in tile_dir.glob("*.png"):
        try:
            x_text, y_text = path.stem.split("_", maxsplit=1)
            tiles[(int(x_text), int(y_text))] = decode_gsi_elevation(path)
        except ValueError as error:
            raise ValueError(f"Expected tile filename '<x>_<y>.png': {path.name}") from error

    if not tiles:
        raise FileNotFoundError(f"No DEM PNG tiles found in {tile_dir}")

    xs = sorted({x for x, _ in tiles})
    ys = sorted({y for _, y in tiles})
    expected = {(x, y) for x in range(xs[0], xs[-1] + 1) for y in range(ys[0], ys[-1] + 1)}
    missing = expected - set(tiles)
    if missing:
        raise ValueError(f"DEM tile grid has gaps: {sorted(missing)}")

    height = len(ys) * TILE_SIZE_PX
    width = len(xs) * TILE_SIZE_PX
    mosaic = np.full((height, width), np.nan, dtype=np.float32)
    for (x, y), elevation in tiles.items():
        row = (y - ys[0]) * TILE_SIZE_PX
        col = (x - xs[0]) * TILE_SIZE_PX
        mosaic[row : row + TILE_SIZE_PX, col : col + TILE_SIZE_PX] = elevation

    left, _, _, top = tile_bounds_mercator(zoom, xs[0], ys[0])
    _, bottom, right, _ = tile_bounds_mercator(zoom, xs[-1], ys[-1])
    transform = from_bounds(left, bottom, right, top, width, height)
    return DemMosaic(mosaic, transform, "EPSG:3857")


def load_scenario(path: Path, default_capacity_mmh: float, scenario_id: str | None) -> tuple[str, list[dict[str, float]]]:
    rows: list[dict[str, float]] = []
    selected_id: str | None = scenario_id
    with path.open(encoding="utf-8-sig", newline="") as handle:
        for raw in csv.DictReader(handle):
            row_scenario_id = (raw.get("scenario_id") or "default").strip()
            if selected_id is None:
                selected_id = row_scenario_id
            if row_scenario_id != selected_id:
                continue
            rainfall = float(raw.get("rainfall_mm_hr") or raw["raw_rainfall_mm_hr"])
            runoff = float(raw.get("runoff_coefficient") or 1.0)
            capacity = float(raw.get("equivalent_drainage_capacity_mm_hr") or default_capacity_mmh)
            rows.append(
                {
                    "elapsed_time_min": float(raw["elapsed_time_min"]),
                    "duration_min": float(raw.get("duration_min") or 10.0),
                    "rainfall_mm_hr": rainfall,
                    "runoff_coefficient": runoff,
                    "capacity_mm_hr": capacity,
                }
            )
    if not rows or selected_id is None:
        requested = scenario_id if scenario_id is not None else "(first scenario)"
        raise ValueError(f"Scenario '{requested}' has no rows in: {path}")
    return selected_id, rows


def d8_flow_direction(elevation_m: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return downhill D8 destinations and a mask of cells with an outlet direction."""
    valid = np.isfinite(elevation_m)
    surface = np.where(valid, elevation_m, np.inf)
    candidates = np.stack(
        [
            np.pad(surface[:-1, :], ((1, 0), (0, 0)), constant_values=np.inf),
            np.pad(surface[1:, :], ((0, 1), (0, 0)), constant_values=np.inf),
            np.pad(surface[:, :-1], ((0, 0), (1, 0)), constant_values=np.inf),
            np.pad(surface[:, 1:], ((0, 0), (0, 1)), constant_values=np.inf),
            np.pad(surface[:-1, :-1], ((1, 0), (1, 0)), constant_values=np.inf),
            np.pad(surface[:-1, 1:], ((1, 0), (0, 1)), constant_values=np.inf),
            np.pad(surface[1:, :-1], ((0, 1), (1, 0)), constant_values=np.inf),
            np.pad(surface[1:, 1:], ((0, 1), (0, 1)), constant_values=np.inf),
        ]
    )
    direction = np.argmin(candidates, axis=0)
    lowest = np.min(candidates, axis=0)
    rows, cols = np.indices(elevation_m.shape)
    destination_rows = rows.copy()
    destination_cols = cols.copy()
    destination_rows[direction == 0] -= 1
    destination_rows[direction == 1] += 1
    destination_cols[direction == 2] -= 1
    destination_cols[direction == 3] += 1
    destination_rows[direction == 4] -= 1
    destination_cols[direction == 4] -= 1
    destination_rows[direction == 5] -= 1
    destination_cols[direction == 5] += 1
    destination_rows[direction == 6] += 1
    destination_cols[direction == 6] -= 1
    destination_rows[direction == 7] += 1
    destination_cols[direction == 7] += 1
    can_route = valid & (lowest < surface)
    return direction, destination_rows, destination_cols, can_route


def d8_flow_accumulation(
    elevation_m: np.ndarray, destination_rows: np.ndarray, destination_cols: np.ndarray, can_route: np.ndarray
) -> np.ndarray:
    """Count upstream cells contributing to each D8 cell; sinks retain accumulated flow."""
    valid = np.isfinite(elevation_m)
    accumulation = valid.astype(np.float32)
    descending = np.argsort(np.where(valid, elevation_m, -np.inf).ravel())[::-1]
    rows, cols = np.unravel_index(descending, elevation_m.shape)
    for row, col in zip(rows, cols):
        if can_route[row, col]:
            accumulation[destination_rows[row, col], destination_cols[row, col]] += accumulation[row, col]
    accumulation[~valid] = NODATA_VALUE
    return accumulation


def route_by_water_surface(
    depth_m: np.ndarray, elevation_m: np.ndarray, transfer_fraction: float
) -> np.ndarray:
    """Legacy one-pass routing used as the conservative baseline model."""
    valid = np.isfinite(elevation_m)
    surface = np.where(valid, elevation_m + depth_m, np.inf)
    candidates = np.stack(
        [
            np.pad(surface[:-1, :], ((1, 0), (0, 0)), constant_values=np.inf),
            np.pad(surface[1:, :], ((0, 1), (0, 0)), constant_values=np.inf),
            np.pad(surface[:, :-1], ((0, 0), (1, 0)), constant_values=np.inf),
            np.pad(surface[:, 1:], ((0, 0), (0, 1)), constant_values=np.inf),
        ]
    )
    direction = np.argmin(candidates, axis=0)
    lowest = np.min(candidates, axis=0)
    transferable = np.where(valid & (lowest < surface), depth_m * transfer_fraction, 0.0)
    result = depth_m - transferable
    rows, cols = np.indices(depth_m.shape)
    destination_rows = rows.copy()
    destination_cols = cols.copy()
    destination_rows[direction == 0] -= 1
    destination_rows[direction == 1] += 1
    destination_cols[direction == 2] -= 1
    destination_cols[direction == 3] += 1
    can_route = transferable > 0
    np.add.at(result, (destination_rows[can_route], destination_cols[can_route]), transferable[can_route])
    result[~valid] = 0.0
    return result


def route_along_d8(
    depth_m: np.ndarray,
    destination_rows: np.ndarray,
    destination_cols: np.ndarray,
    can_route: np.ndarray,
    transfer_fraction: float,
    iterations: int,
) -> np.ndarray:
    """Route water repeatedly along precomputed downhill D8 directions."""
    routed = depth_m
    for _ in range(iterations):
        transferable = np.where(can_route, routed * transfer_fraction, 0.0)
        routed = routed - transferable
        np.add.at(routed, (destination_rows[can_route], destination_cols[can_route]), transferable[can_route])
    return routed


def write_geotiff(path: Path, values: np.ndarray, mosaic: DemMosaic) -> None:
    output = np.where(np.isfinite(mosaic.elevation_m), values, NODATA_VALUE).astype(np.float32)
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        height=output.shape[0],
        width=output.shape[1],
        count=1,
        dtype="float32",
        crs=mosaic.crs,
        transform=mosaic.transform,
        nodata=NODATA_VALUE,
        compress="deflate",
    ) as dataset:
        dataset.write(output, 1)


def run(args: argparse.Namespace) -> None:
    config = json.loads(args.params.read_text(encoding="utf-8"))
    drainage_mmh = float(config["drainage_capacity"]["value_mm_per_hr"])
    routing_method = config["surface_routing"]["method"]
    routing_fraction = float(config["surface_routing"]["transfer_fraction_per_step"])
    routing_iterations = int(config["surface_routing"]["iterations_per_step"])
    mosaic = load_dem_tiles(args.dem_tiles, args.zoom)
    scenario_id, scenario = load_scenario(args.scenario, drainage_mmh, args.scenario_id)
    valid = np.isfinite(mosaic.elevation_m)
    direction, destination_rows, destination_cols, can_route = d8_flow_direction(mosaic.elevation_m)
    accumulation = d8_flow_accumulation(mosaic.elevation_m, destination_rows, destination_cols, can_route)
    depth_m = np.zeros_like(mosaic.elevation_m, dtype=np.float32)
    max_depth_m = np.zeros_like(mosaic.elevation_m, dtype=np.float32)
    output_dir = args.output / scenario_id
    output_dir.mkdir(parents=True, exist_ok=True)
    summary: list[dict[str, float]] = []
    step_hours = args.step_minutes / 60.0

    for step, row in enumerate(scenario, start=1):
        net_input_m = (row["rainfall_mm_hr"] * row["runoff_coefficient"] - row["capacity_mm_hr"]) / 1000.0
        depth_m = np.maximum(0.0, depth_m + net_input_m * step_hours)
        if routing_method == "surface_gradient_one_pass_baseline":
            depth_m = route_by_water_surface(depth_m, mosaic.elevation_m, routing_fraction)
        elif routing_method == "d8_downslope_multi_pass_experimental":
            depth_m = route_along_d8(
                depth_m, destination_rows, destination_cols, can_route, routing_fraction, routing_iterations
            )
        else:
            raise ValueError(f"Unsupported surface_routing.method: {routing_method}")
        max_depth_m = np.maximum(max_depth_m, depth_m)
        elapsed_min = row["elapsed_time_min"] + args.step_minutes
        write_geotiff(output_dir / f"ponding_depth_t{elapsed_min:g}min.tif", depth_m, mosaic)
        summary.append(
            {
                "step": step,
                "elapsed_time_min": elapsed_min,
                "rainfall_mm_hr": row["rainfall_mm_hr"],
                "net_input_mm_hr": net_input_m * 1000.0,
                "maximum_depth_m": float(np.nanmax(depth_m[valid])),
                "stored_volume_m3": float(np.sum(depth_m[valid])) * abs(mosaic.transform.a * mosaic.transform.e),
                "ponded_area_m2": float(np.count_nonzero(depth_m[valid] > args.ponding_threshold_m))
                * abs(mosaic.transform.a * mosaic.transform.e),
            }
        )

    write_geotiff(output_dir / "maximum_ponding_depth_m.tif", max_depth_m, mosaic)
    write_geotiff(output_dir / "final_ponding_depth_m.tif", depth_m, mosaic)
    write_geotiff(output_dir / "flow_direction_d8.tif", direction.astype(np.float32), mosaic)
    write_geotiff(output_dir / "flow_accumulation_cells.tif", accumulation, mosaic)
    with (output_dir / "water_balance_summary.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)
    (output_dir / "run_metadata.json").write_text(
        json.dumps(
            {
                "model": "screening-level uniform-drainage surface-water balance",
                "dem_tiles": str(args.dem_tiles),
                "scenario": str(args.scenario),
                "scenario_id": scenario_id,
                "parameters": config,
                "step_minutes": args.step_minutes,
                "limitations": config["limitations"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    final = summary[-1]
    (output_dir / "scenario_summary.json").write_text(
        json.dumps(
            {
                "scenario_id": scenario_id,
                "model_scope": "screening-level uniform-drainage surface-water balance",
                "maximum_ponding_depth_m": max(item["maximum_depth_m"] for item in summary),
                "maximum_ponded_area_m2": max(item["ponded_area_m2"] for item in summary),
                "final_ponding_depth_m": final["maximum_depth_m"],
                "final_stored_volume_m3": final["stored_volume_m3"],
                "duration_min": final["elapsed_time_min"],
                "limitations": config["limitations"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dem-tiles", type=Path, default=root / "data/naisui_poc/01_raw/dem/gsi_dem5a_png_z15")
    parser.add_argument("--params", type=Path, default=root / "data/naisui_poc/02_processed/model_input/drainage_params.json")
    parser.add_argument("--scenario", type=Path, default=root / "data/naisui_poc/03_scenarios/rainfall_scenarios.csv")
    parser.add_argument("--scenario-id", help="CSVのscenario_id。省略時は先頭のシナリオだけを実行する。")
    parser.add_argument("--output", type=Path, default=root / "data/naisui_poc/02_processed/surface_water_balance")
    parser.add_argument("--zoom", type=int, default=15)
    parser.add_argument("--step-minutes", type=float, default=10.0)
    parser.add_argument("--ponding-threshold-m", type=float, default=0.01)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
