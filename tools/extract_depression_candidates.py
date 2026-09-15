"""Extract DEM depression candidates as ranked CSV and GeoJSON for review."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np
import rasterio
from rasterio.features import shapes
from rasterio.transform import xy
from rasterio.warp import transform
from scipy import ndimage


def run(args: argparse.Namespace) -> None:
    with rasterio.open(args.input) as dataset:
        depth = dataset.read(1, masked=True)
        valid = ~np.ma.getmaskarray(depth)
        transform_affine = dataset.transform
        crs = dataset.crs
    values = np.asarray(depth.filled(0), dtype=np.float32)
    candidate = valid & (values >= args.min_depth_m)
    labels, count = ndimage.label(candidate, structure=np.ones((3, 3), dtype=np.uint8))
    cell_area_m2 = abs(transform_affine.a * transform_affine.e)
    records: list[dict[str, object]] = []
    for label_id in range(1, count + 1):
        rows, cols = np.where(labels == label_id)
        if len(rows) < args.min_cells:
            continue
        depths = values[rows, cols]
        center_row = float(rows.mean())
        center_col = float(cols.mean())
        center_x, center_y = xy(transform_affine, center_row, center_col)
        longitude, latitude = transform(crs, "EPSG:4326", [center_x], [center_y])
        records.append(
            {
                "candidate_id": label_id,
                "max_depth_m": float(depths.max()),
                "mean_depth_m": float(depths.mean()),
                "area_m2": float(len(rows) * cell_area_m2),
                "cell_count": int(len(rows)),
                "center_x": center_x,
                "center_y": center_y,
                "longitude": longitude[0],
                "latitude": latitude[0],
            }
        )
    records.sort(key=lambda record: (-float(record["max_depth_m"]), -float(record["area_m2"])))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with (args.output_dir / "depression_candidates.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]) if records else ["candidate_id"])
        writer.writeheader()
        writer.writerows(records)

    retained_labels = {int(record["candidate_id"]) for record in records}
    properties = {int(record["candidate_id"]): record for record in records}
    features = []
    for geometry, label_value in shapes(labels.astype(np.int32), mask=np.isin(labels, list(retained_labels)), transform=transform_affine):
        label_id = int(label_value)
        features.append({"type": "Feature", "properties": properties[label_id], "geometry": geometry})
    geojson = {"type": "FeatureCollection", "name": "depression_candidates", "features": features}
    (args.output_dir / "depression_candidates.geojson").write_text(json.dumps(geojson, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(records)} depression candidates to {args.output_dir}")


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=root / "data/naisui_poc/02_processed/pysheds_surface_routing/sc_100mm_extreme/depression_depth_m.tif",
    )
    parser.add_argument("--output-dir", type=Path, default=root / "data/naisui_poc/02_processed/depression_review")
    parser.add_argument("--min-depth-m", type=float, default=0.10)
    parser.add_argument("--min-cells", type=int, default=2)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
