"""Create a reversible median-filtered DEM variant for sensitivity analysis."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import median_filter


def run(args: argparse.Namespace) -> None:
    with rasterio.open(args.input) as source:
        profile = source.profile.copy()
        dem = source.read(1, masked=True)
    valid = ~np.ma.getmaskarray(dem)
    values = np.asarray(dem.filled(np.nan), dtype=np.float32)
    # Nearest-neighbour padding avoids importing NoData into edge cells.
    filtered = median_filter(np.where(valid, values, np.nanmedian(values[valid])), size=args.window_cells, mode="nearest")
    nodata = profile.get("nodata", -9999.0)
    output = np.where(valid, filtered, nodata).astype(np.float32)
    profile.update(dtype="float32", nodata=nodata, compress="deflate")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(args.output, "w", **profile) as destination:
        destination.write(output, 1)
    print(f"Wrote median-filtered DEM to {args.output}")


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=root / "data/naisui_poc/02_processed/pysheds_surface_routing/sc_100mm_extreme/dem_raw_epsg3857.tif",
    )
    parser.add_argument("--output", type=Path, default=root / "data/naisui_poc/02_processed/dem_analysis/dem_median_3x3.tif")
    parser.add_argument("--window-cells", type=int, default=3)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
