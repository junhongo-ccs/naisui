"""Evaluate model inundation masks against an official hazard polygon by IoU."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.features import rasterize

from run_surface_water_balance import ground_cell_areas_m2


def evaluate(model_path: Path, hazard: gpd.GeoDataFrame, threshold_m: float, hazard_depth_field: str | None) -> dict[str, object]:
    with rasterio.open(model_path) as dataset:
        model = dataset.read(1, masked=True)
        valid = ~np.ma.getmaskarray(model)
        model_mask = valid & (np.asarray(model.filled(0), dtype=float) >= threshold_m)
        hazards_in_crs = hazard.to_crs(dataset.crs)
        if hazard_depth_field:
            if hazard_depth_field not in hazards_in_crs.columns:
                raise ValueError(f"Hazard depth field '{hazard_depth_field}' was not found.")
            hazards_in_crs = hazards_in_crs[hazards_in_crs[hazard_depth_field] >= threshold_m]
        hazard_mask = rasterize(
            ((geometry, 1) for geometry in hazards_in_crs.geometry if geometry is not None),
            out_shape=model.shape,
            transform=dataset.transform,
            fill=0,
            dtype="uint8",
            all_touched=True,
        ).astype(bool) & valid
        # EPSG:3857の名目画素面積は地上面積の約1.5倍になるため、行ごとの地上面積で集計する。
        cell_area_m2 = np.broadcast_to(ground_cell_areas_m2(dataset.transform, dataset.crs, model.shape[0]), model.shape)
    intersection = float(cell_area_m2[model_mask & hazard_mask].sum())
    union = float(cell_area_m2[model_mask | hazard_mask].sum())
    return {
        "model": str(model_path),
        "threshold_m": threshold_m,
        "iou_jaccard": intersection / union if union else None,
        "intersection_area_m2": intersection,
        "union_area_m2": union,
        "model_area_m2": float(cell_area_m2[model_mask].sum()),
        "hazard_area_m2": float(cell_area_m2[hazard_mask].sum()),
    }


def parse_model(value: str) -> tuple[str, Path]:
    try:
        label, path = value.split("=", maxsplit=1)
    except ValueError as error:
        raise argparse.ArgumentTypeError("--model must use LABEL=PATH") from error
    return label, Path(path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hazard", type=Path, required=True, help="公的な内水浸水区域ポリゴン（GeoJSON/GPKG/Shapefile）")
    parser.add_argument("--model", type=parse_model, action="append", required=True, help="LABEL=最大湛水深GeoTIFF。複数回指定可")
    parser.add_argument("--threshold", type=float, action="append", default=[0.1, 0.2])
    parser.add_argument("--hazard-depth-field", default="depth_min_m", help="公式浸水深の下限値（m）。不要なら空文字を指定")
    parser.add_argument("--output", type=Path, default=Path("data/naisui_poc/02_processed/evaluation/iou_results.csv"))
    args = parser.parse_args()

    hazard = gpd.read_file(args.hazard)
    if hazard.empty or hazard.crs is None:
        raise ValueError("Hazard polygon must contain geometries and a CRS.")
    rows = []
    for label, model_path in args.model:
        for threshold in sorted(set(args.threshold)):
            row = evaluate(model_path, hazard, threshold, args.hazard_depth_field or None)
            row["case"] = label
            rows.append(row)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote IoU evaluation for {len(rows)} case/threshold pairs to {args.output}")


if __name__ == "__main__":
    main()
