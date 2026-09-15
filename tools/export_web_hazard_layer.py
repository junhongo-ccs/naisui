"""Export the QGIS-derived hazard vector layer to a web-map-ready GeoJSON.

Reprojects `hazard_shinagawa_normalized.gpkg` (EPSG:6677) to WGS84 and adds a
`color` (hex) property per feature so the frontend map can style features by
`depth_class` without re-deriving colors at runtime. This is a build-time /
data-refresh step, not something the frontend or backend should run per request.

Source of the underlying data and its limitations:
docs/品川_ハザードPDF地理参照・色採取記録.md
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd


def rgb_string_to_hex(rgb: str) -> str:
    r, g, b = (int(part) for part in rgb.split(","))
    return f"#{r:02x}{g:02x}{b:02x}"


def run(args: argparse.Namespace) -> None:
    gdf = gpd.read_file(args.input)
    if gdf.crs is None:
        raise ValueError("Input has no CRS defined.")
    gdf = gdf.to_crs("EPSG:4326")
    gdf["color"] = gdf["rgb"].map(rgb_string_to_hex)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(args.output, driver="GeoJSON")

    metadata = {
        "source_gpkg": str(args.input),
        "feature_count": int(len(gdf)),
        "crs": "EPSG:4326",
        "calibration_status": "pre_calibration_pdf_derived",
        "derivation_note": (
            "地理参照済みPDFから抽出した派生ベクタであり、公式GIS原典ではない。"
            "相対的な形状比較に限る。詳細: docs/品川_ハザードPDF地理参照・色採取記録.md"
        ),
        "gcp_rmse_m": float(gdf["gcp_rmse_m"].iloc[0]) if "gcp_rmse_m" in gdf.columns and len(gdf) else None,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    metadata_path = args.output.with_suffix(".metadata.json")
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {args.output} ({len(gdf)} features) and {metadata_path}")


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=root / "data/naisui_poc/02_processed/evaluation/hazard_shinagawa_normalized.gpkg",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=root / "data/naisui_poc/02_processed/web_map/hazard_pdf_derived.geojson",
    )
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
