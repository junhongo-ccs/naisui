"""Export a scenario's max ponding-depth raster to a colorized PNG overlay for MapLibre.

Reprojects to EPSG:4326 (so the output rectangle is axis-aligned lon/lat, usable
directly as a MapLibre `ImageSource` with its 4 corner coordinates) and applies a
depth color ramp distinct from the official hazard-PDF legend colors, so the two
layers are not visually mistaken for the same data source on the PC map.

This is a build-time / data-refresh step. Run it once per scenario after the
model output changes; do not convert at request time.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio
from PIL import Image
from rasterio.features import geometry_mask
from rasterio.warp import Resampling, calculate_default_transform, reproject

ROOT = Path(__file__).resolve().parents[1]

# 対象10町丁目 + 100mバッファの外側はDEM解析範囲の縁にあたり、水が「その先に流れる場所がない」
# ことによる境界アーティファクトの疑いが強い（docs/03_モデル検証/中延二葉_モデル実績照合レビュー.md 第3章の
# 凹地容量アーティファクトと同根）。2026-09-15、着色ピクセルの93.4%が対象町丁目の外だったため、
# ユーザー判断でクリップすることに決定（オプション3: 対象町丁目+少し余白のみ表示）。
TARGET_TOWN_PATTERN = r"^(中延[一二三四五六]丁目|二葉[一二三四]丁目)$"
TARGET_BUFFER_M = 100


def target_area_geometry_4326():
    towns = gpd.read_file(ROOT / "data/naisui_poc/01_raw/boundaries/r2kb13109.shp")
    towns = towns[towns["S_NAME"].astype(str).str.fullmatch(TARGET_TOWN_PATTERN, na=False)]
    # 元のCRSはEPSG:4612（度単位の地理座標系）。度のままbuffer()すると単位を誤り、
    # 桁違いに巨大な（あるいは無意味な）形状になる。メートル単位の投影系に変換してからバッファする。
    towns_m = towns.to_crs("EPSG:6677")
    union_m = towns_m.union_all()
    buffered_m = union_m.buffer(TARGET_BUFFER_M)
    return gpd.GeoSeries([buffered_m], crs="EPSG:6677").to_crs("EPSG:4326").iloc[0]

# Sequential purple ramp for the model's screening depth. Deliberately different
# from the official hazard layer (PDF-derived, drawn blue-grey in MapPanel.jsx)
# so this overlay is never mistaken for the official hazard-map extent
# (2026-09-25: changed from blue to purple for that reason).
#
# NO_PONDING_THRESHOLD_M is intentionally NOT aligned to `depth_threshold_m`
# (0.2m) used in tools/export_risk_lookup.py's area_over_threshold_ratio.
# That alignment was tried on 2026-09-15 and reverted the same day per the
# user: this map is showing 内水氾濫 (water that backed up because the
# drainage system was overwhelmed), not rainfall pooling on the ground — even
# 1cm of that is meaningfully "内水氾濫" and worth showing, unlike a 1cm rain
# puddle. The 0.2m figure in the risk panel is a separate, stricter judgment
# threshold for the risk_level label; the map's job is to show where the
# model finds any ponding at all. Cap is 0.3m (not the raw max_depth_m range,
# up to 6m, dominated by DEM artifacts — docs/03_モデル検証/中延二葉_モデル実績照合レビュー.md
# 第3章) so the gradient stays legible across the depths that actually occur.
NO_PONDING_THRESHOLD_M = 0.01
RAMP_STOPS = [
    (0.01, (226, 206, 242)),  # just above no-ponding
    (0.05, (196, 160, 230)),
    (0.10, (160, 107, 212)),
    (0.20, (120, 58, 180)),
    (0.30, (80, 20, 130)),  # cap: anything deeper (incl. DEM artifacts) clamps here
]
OVERLAY_ALPHA = 190


def color_for_depth(depth_m: np.ndarray) -> np.ndarray:
    depths = [stop[0] for stop in RAMP_STOPS]
    colors = np.array([stop[1] for stop in RAMP_STOPS], dtype=np.float64)
    clamped = np.clip(depth_m, depths[0], depths[-1])
    rgb = np.empty(clamped.shape + (3,), dtype=np.float64)
    for channel in range(3):
        rgb[..., channel] = np.interp(clamped, depths, colors[:, channel])
    return rgb


def run(args: argparse.Namespace) -> None:
    with rasterio.open(args.input) as src:
        dst_crs = "EPSG:4326"
        transform, width, height = calculate_default_transform(
            src.crs, dst_crs, src.width, src.height, *src.bounds
        )
        depth = np.full((height, width), np.nan, dtype=np.float32)
        reproject(
            source=rasterio.band(src, 1),
            destination=depth,
            src_transform=src.transform,
            src_crs=src.crs,
            dst_transform=transform,
            dst_crs=dst_crs,
            resampling=Resampling.bilinear,
        )
        left, top = transform * (0, 0)
        right, bottom = transform * (width, height)

    target_geom = target_area_geometry_4326()
    outside_target_area = geometry_mask([target_geom], out_shape=(height, width), transform=transform, invert=False)

    valid = np.isfinite(depth) & (depth >= NO_PONDING_THRESHOLD_M) & ~outside_target_area
    rgba = np.zeros((height, width, 4), dtype=np.uint8)
    colored = color_for_depth(depth[valid])
    rgba_valid = np.zeros((valid.sum(), 4), dtype=np.uint8)
    rgba_valid[:, :3] = np.clip(colored, 0, 255).astype(np.uint8)
    rgba_valid[:, 3] = OVERLAY_ALPHA
    rgba[valid] = rgba_valid

    args.output.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(rgba, mode="RGBA").save(args.output)

    bounds = {
        "scenario_id": args.scenario_id,
        "crs": "EPSG:4326",
        # MapLibre ImageSource coordinate order: top-left, top-right, bottom-right, bottom-left.
        "coordinates": [[left, top], [right, top], [right, bottom], [left, bottom]],
        "calibration_status": "pre_calibration_screening",
        "ramp_note": "内水氾濫ハザードPDF由来レイヤーとは異なる配色。本モデルの校正前スクリーニング結果であることを示す。",
        "no_ponding_threshold_m": NO_PONDING_THRESHOLD_M,
        "clipped_to_target_towns_buffer_m": TARGET_BUFFER_M,
        "depth_cap_m": RAMP_STOPS[-1][0],
        "source_raster": str(args.input),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    bounds_path = args.output.with_suffix("").with_suffix(".bounds.json")
    bounds_path.write_text(json.dumps(bounds, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {args.output} and {bounds_path}")


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario-id", required=True)
    parser.add_argument(
        "--input",
        type=Path,
        help="maximum_ponding_depth_m.tif のパス。省略時は pysheds_surface_routing/<scenario-id> から推定。",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="出力PNGパス。省略時は data/naisui_poc/02_processed/web_map/ponding_depth_<scenario-id>.png",
    )
    args = parser.parse_args()
    if args.input is None:
        args.input = root / f"data/naisui_poc/02_processed/pysheds_surface_routing/{args.scenario_id}/maximum_ponding_depth_m.tif"
    if args.output is None:
        args.output = root / f"data/naisui_poc/02_processed/web_map/ponding_depth_{args.scenario_id}.png"
    return args


if __name__ == "__main__":
    run(parse_args())
