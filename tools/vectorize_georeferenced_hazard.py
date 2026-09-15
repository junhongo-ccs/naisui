"""Vectorize colour-coded inland-inundation classes from a georeferenced raster.

The input must be a GeoTIFF/COG already georeferenced from an official PDF.
This creates a *derived* GIS dataset for relative PoC comparison; it does not
replace an authority-provided GIS source.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.features import shapes
from shapely.geometry import shape


def load_classes(path: Path) -> list[dict[str, object]]:
    config = json.loads(path.read_text(encoding="utf-8"))
    classes = config.get("classes", [])
    if not classes:
        raise ValueError("Colour-class JSON must have a non-empty 'classes' array.")
    required = {"depth_class", "depth_min_m", "rgb"}
    for item in classes:
        missing = required.difference(item)
        if missing:
            raise ValueError(f"Colour class is missing required fields: {sorted(missing)}")
        rgb = item["rgb"]
        if not isinstance(rgb, list) or len(rgb) != 3 or any(not isinstance(v, int) or not 0 <= v <= 255 for v in rgb):
            raise ValueError("'rgb' must be an array of three integers from 0 through 255.")
        if float(item["depth_min_m"]) < 0:
            raise ValueError("'depth_min_m' cannot be negative.")
    return classes


def write_vector(data: gpd.GeoDataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    suffix = path.suffix.lower()
    if suffix in {".geojson", ".json"}:
        data.to_file(path, driver="GeoJSON")
    elif suffix == ".gpkg":
        data.to_file(path, layer="hazard_from_pdf", driver="GPKG")
    else:
        raise ValueError("Output must have .geojson, .json, or .gpkg extension.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="GCP位置合わせ済みRGB GeoTIFF/COG")
    parser.add_argument("--classes", type=Path, required=True, help="RGBと浸水深区分のJSON設定")
    parser.add_argument("--source-pdf", type=Path, required=True, help="原典の公式PDF")
    parser.add_argument("--gcp-rmse-m", type=float, required=True, help="地理参照時のGCP RMSE（m）")
    parser.add_argument("--output", type=Path, default=Path("data/naisui_poc/02_processed/evaluation/shinagawa_hazard_from_pdf.geojson"))
    parser.add_argument("--metadata-output", type=Path, default=Path("data/naisui_poc/02_processed/evaluation/shinagawa_hazard_from_pdf_metadata.json"))
    parser.add_argument("--minimum-polygon-area-m2", type=float, default=100.0, help="ノイズ除去の最小面積（m2）")
    parser.add_argument("--hourly-maximum-rainfall-mm", type=float, default=153.0)
    parser.add_argument("--total-rainfall-mm", type=float, default=690.0)
    args = parser.parse_args()

    if args.gcp_rmse_m < 0 or args.minimum_polygon_area_m2 < 0:
        raise ValueError("RMSE and minimum polygon area must be non-negative.")
    if not args.source_pdf.is_file():
        raise FileNotFoundError(f"Source PDF does not exist: {args.source_pdf}")
    classes = load_classes(args.classes)
    records: list[dict[str, object]] = []

    with rasterio.open(args.input) as source:
        if source.crs is None:
            raise ValueError("Input raster has no CRS. Complete GCP georeferencing before vectorizing.")
        if not source.crs.is_projected:
            raise ValueError("Input raster CRS must use projected metre units (for example EPSG:6677).")
        if source.transform.is_identity:
            raise ValueError("Input raster has an identity transform. Complete GCP georeferencing before vectorizing.")
        if source.count < 3:
            raise ValueError("Input raster must contain at least three RGB bands.")
        rgb = source.read([1, 2, 3]).astype(np.int32)
        valid = np.ones((source.height, source.width), dtype=bool)
        if source.count >= 4:
            valid &= source.read(4) > 0

        for item in classes:
            color = np.asarray(item["rgb"], dtype=np.int32).reshape(3, 1, 1)
            tolerance = int(item.get("tolerance_rgb", 0))
            distance = np.sqrt(np.sum((rgb - color) ** 2, axis=0))
            mask = valid & (distance <= tolerance)
            if not mask.any():
                raise ValueError(
                    f"No pixels matched {item['depth_class']} RGB={item['rgb']}. "
                    "Check the sampled colour and tolerance_rgb."
                )
            for geometry, value in shapes(mask.astype("uint8"), mask=mask, transform=source.transform):
                if not value:
                    continue
                polygon = shape(geometry)
                if polygon.area < args.minimum_polygon_area_m2:
                    continue
                records.append(
                    {
                        "depth_class": str(item["depth_class"]),
                        "depth_min_m": float(item["depth_min_m"]),
                        "rgb": ",".join(str(value) for value in item["rgb"]),
                        "derived_from_pdf": True,
                        "gcp_rmse_m": args.gcp_rmse_m,
                        "geometry": polygon,
                    }
                )
        crs = source.crs

    if not records:
        raise ValueError("All matched regions were smaller than the minimum polygon area.")
    output = gpd.GeoDataFrame(records, geometry="geometry", crs=crs)
    output["geometry"] = output.geometry.make_valid()
    output = output[~output.geometry.is_empty].copy()
    write_vector(output, args.output)

    args.metadata_output.parent.mkdir(parents=True, exist_ok=True)
    metadata = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "derived_from_pdf": True,
        "source_pdf": str(args.source_pdf),
        "georeferenced_raster": str(args.input),
        "gcp_rmse_m": args.gcp_rmse_m,
        "hourly_maximum_rainfall_mm": args.hourly_maximum_rainfall_mm,
        "total_rainfall_mm": args.total_rainfall_mm,
        "output_crs": str(output.crs),
        "minimum_polygon_area_m2": args.minimum_polygon_area_m2,
        "feature_count": len(output),
        "classes": classes,
        "usage_limit": "Derived from an official PDF for relative spatial comparison only; not an authoritative GIS dataset or an evacuation-decision input.",
    }
    args.metadata_output.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(output)} derived polygons to {args.output}")


if __name__ == "__main__":
    main()
