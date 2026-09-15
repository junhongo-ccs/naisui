"""Validate and normalize an official inland-inundation polygon dataset.

This tool is intentionally strict: it rejects a dataset that does not overlap the
reference model raster.  That prevents a municipality-wide file with the wrong
coverage from silently entering the Shinagawa IoU evaluation.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd
import rasterio
from shapely.geometry import box


DEPTH_FIELD_CANDIDATES = ("depth_min_m", "A51_005", "depth", "depth_m", "浸水深", "浸水ランク")


def normalized_depth_min_m(value: object) -> float | None:
    """Return the lower bound of a Japanese depth-class label, where possible."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().lower().replace("ｍ", "m")
    if not text:
        return None
    if "未満" in text and "以上" not in text:
        return 0.0
    match = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*m?\s*以上", text)
    if match:
        return float(match.group(1))
    match = re.fullmatch(r"([0-9]+(?:\.[0-9]+)?)", text)
    return float(match.group(1)) if match else None


def find_depth_field(columns: list[str], requested: str | None) -> str:
    if requested:
        if requested not in columns:
            raise ValueError(f"Depth field '{requested}' was not found. Available: {columns}")
        return requested
    for field in DEPTH_FIELD_CANDIDATES:
        if field in columns:
            return field
    raise ValueError("No depth-class field was detected. Supply --depth-field explicitly.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="受領したGeoJSON / Shapefile / GPKG")
    parser.add_argument("--reference-raster", required=True, type=Path, help="中延・二葉モデルのGeoTIFF")
    parser.add_argument("--depth-field", help="浸水深区分の元属性。省略時は既知の候補を検出")
    parser.add_argument("--output", type=Path, default=Path("data/naisui_poc/02_processed/evaluation/hazard_shinagawa_normalized.gpkg"))
    parser.add_argument("--metadata-output", type=Path, default=Path("data/naisui_poc/02_processed/evaluation/hazard_shinagawa_normalized_metadata.json"))
    parser.add_argument("--target-crs", default="EPSG:6677", help="正規化後のCRS（既定: JGD2011 第IX系）")
    args = parser.parse_args()

    hazard = gpd.read_file(args.input)
    if hazard.empty:
        raise ValueError("Hazard data contains no features.")
    if hazard.crs is None:
        raise ValueError("Hazard data has no CRS. Assign its authoritative CRS before processing.")
    if not all(geometry is None or geometry.geom_type in {"Polygon", "MultiPolygon"} for geometry in hazard.geometry):
        raise ValueError("Hazard data must contain Polygon or MultiPolygon geometries only.")

    depth_field = find_depth_field(list(hazard.columns), args.depth_field)
    with rasterio.open(args.reference_raster) as raster:
        reference_crs = raster.crs
        reference_bounds = box(*raster.bounds)
    if reference_crs is None:
        raise ValueError("Reference raster has no CRS.")

    source_feature_count = len(hazard)
    hazard = hazard[hazard.geometry.notna()].copy()
    hazard["geometry"] = hazard.geometry.make_valid()
    hazard = hazard[~hazard.geometry.is_empty].copy()
    hazard_in_reference_crs = hazard.to_crs(reference_crs)
    overlap = hazard_in_reference_crs[hazard_in_reference_crs.intersects(reference_bounds)].copy()
    if overlap.empty:
        raise ValueError(
            "Hazard data does not overlap the reference raster (Nakanobu/Futaba). "
            "Do not use it for Shinagawa IoU evaluation."
        )

    overlap["depth_class_source"] = overlap[depth_field].astype(str)
    overlap["depth_min_m"] = overlap[depth_field].map(normalized_depth_min_m)
    unparsed = int(overlap["depth_min_m"].isna().sum())
    normalized = overlap.to_crs(args.target_crs)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.metadata_output.parent.mkdir(parents=True, exist_ok=True)
    normalized.to_file(args.output, layer="hazard", driver="GPKG")
    metadata = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "input": str(args.input),
        "reference_raster": str(args.reference_raster),
        "source_feature_count": source_feature_count,
        "overlapping_feature_count": len(normalized),
        "source_crs": str(hazard.crs),
        "output_crs": str(normalized.crs),
        "depth_field_source": depth_field,
        "depth_field_normalized": "depth_min_m",
        "unparsed_depth_class_count": unparsed,
        "acceptance": "passed",
    }
    args.metadata_output.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Accepted {len(normalized)} overlapping polygons -> {args.output}")


if __name__ == "__main__":
    main()
