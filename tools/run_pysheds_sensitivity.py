"""Run 0.5m, 1.0m, and 1.5m depression-cap sensitivity cases on a smoothed DEM."""

from __future__ import annotations

import argparse
from argparse import Namespace
from pathlib import Path

from run_pysheds_surface_routing import run


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario-id", default="sc_100mm_extreme")
    parser.add_argument("--dem", type=Path, default=root / "data/naisui_poc/02_processed/dem_analysis/dem_median_3x3.tif")
    parser.add_argument("--params", type=Path, default=root / "data/naisui_poc/02_processed/model_input/drainage_params.json")
    parser.add_argument("--scenario", type=Path, default=root / "data/naisui_poc/03_scenarios/rainfall_scenarios.csv")
    parser.add_argument("--output", type=Path, default=root / "data/naisui_poc/02_processed/pysheds_sensitivity")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    for cap in (0.5, 1.0, 1.5):
        label = f"median3_cap{cap:g}m".replace(".", "p")
        run(
            Namespace(
                scenario_id=args.scenario_id,
                dem=args.dem,
                dem_tiles=None,
                params=args.params,
                scenario=args.scenario,
                output=args.output / label,
                zoom=15,
                step_minutes=10.0,
                depression_threshold_m=0.01,
                max_depression_depth_m=cap,
                ponding_threshold_m=0.01,
                runoff_coefficient_raster=None,
                building_fraction_raster=None,
                building_threshold=0.5,
                road_fraction_raster=None,
                road_threshold=0.5,
            )
        )


if __name__ == "__main__":
    main()
