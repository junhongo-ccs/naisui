"""Hydrologically condition GSI DEM tiles and calculate D8 flow products.

Outputs are diagnostic inputs for the next model revision. They do not by
themselves constitute an urban drainage or inundation simulation.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from pysheds.grid import Grid

from run_surface_water_balance import load_dem_tiles, write_geotiff

# pysheds 0.4.x calls the removed NumPy 1.x alias internally.
if not hasattr(np, "in1d"):
    np.in1d = np.isin  # type: ignore[attr-defined]


def run(args: argparse.Namespace) -> None:
    output = args.output
    output.mkdir(parents=True, exist_ok=True)

    # The downloaded GSI source is DEM PNG; make an analysis GeoTIFF first.
    mosaic = load_dem_tiles(args.dem_tiles, args.zoom)
    dem_path = output / "dem_mosaic_epsg3857.tif"
    write_geotiff(dem_path, mosaic.elevation_m, mosaic)

    grid = Grid.from_raster(str(dem_path))
    dem = grid.read_raster(str(dem_path))

    # Hydrologic conditioning prevents artificial micro-pits and flats from
    # terminating a D8 path before it reaches a downstream outlet.
    pits_filled = grid.fill_pits(dem)
    depressions_filled = grid.fill_depressions(pits_filled)
    conditioned_dem = grid.resolve_flats(depressions_filled)
    flow_direction = grid.flowdir(conditioned_dem, routing="d8")
    flow_accumulation = grid.accumulation(flow_direction, routing="d8")

    grid.to_raster(pits_filled, str(output / "dem_pits_filled.tif"))
    grid.to_raster(depressions_filled, str(output / "dem_depressions_filled.tif"))
    grid.to_raster(conditioned_dem, str(output / "dem_conditioned.tif"))
    grid.to_raster(flow_direction, str(output / "flow_direction_d8_pysheds.tif"))
    grid.to_raster(flow_accumulation, str(output / "flow_accumulation_cells_pysheds.tif"))

    print(f"Wrote hydrologic conditioning and D8 products to {output}")


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dem-tiles", type=Path, default=root / "data/naisui_poc/01_raw/dem/gsi_dem5a_png_z15")
    parser.add_argument("--output", type=Path, default=root / "data/naisui_poc/02_processed/dem_analysis")
    parser.add_argument("--zoom", type=int, default=15)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
