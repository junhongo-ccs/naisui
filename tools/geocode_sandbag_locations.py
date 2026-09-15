"""Geocode sandbag storage locations (address-only) to lat/lon and GeoJSON.

Uses the GSI address search API (address-representative-point precision, not
the actual facility footprint). Source addresses in
data/naisui_poc/01_raw/shelter/sandbag_locations_ebara.csv have no coordinates.

This hits a live public API; run it manually when the source CSV changes, not
as part of any request-time path.
"""

from __future__ import annotations

import argparse
import csv
import json
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

API_URL = "https://msearch.gsi.go.jp/address-search/AddressSearch?q={query}"
PREFECTURE_CITY = "東京都品川区"


def geocode(address: str) -> tuple[float, float, str] | None:
    full_address = PREFECTURE_CITY + address
    url = API_URL.format(query=urllib.parse.quote(full_address))
    with urllib.request.urlopen(url, timeout=20) as response:
        results = json.loads(response.read().decode("utf-8"))
    if not results:
        return None
    lon, lat = results[0]["geometry"]["coordinates"]
    matched_title = results[0]["properties"]["title"]
    return lat, lon, matched_title


def run(args: argparse.Namespace) -> None:
    rows = list(csv.DictReader(args.input.open(encoding="utf-8")))
    geocoded_on = date.today().isoformat()
    features = []
    csv_rows = []
    for row in rows:
        result = geocode(row["address"])
        if result is None:
            raise RuntimeError(f"Geocoding failed for id={row['id']} address={row['address']}")
        lat, lon, matched_title = result
        record = {
            "id": row["id"],
            "address": PREFECTURE_CITY + row["address"],
            "landmark": row["landmark"],
            "quantity": row["quantity"],
            "source_updated": row["source_updated"],
            "lat": lat,
            "lon": lon,
            "geocode_precision": "banchi_representative_point",
            "geocode_source": "国土地理院 住所検索API (msearch.gsi.go.jp/address-search)",
            "geocode_matched_title": matched_title,
            "geocoded_on": geocoded_on,
            "crs": "EPSG:4326",
        }
        csv_rows.append(record)
        features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {k: v for k, v in record.items() if k not in ("lat", "lon")},
            }
        )
        time.sleep(args.request_interval_sec)

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(csv_rows[0].keys()))
        writer.writeheader()
        writer.writerows(csv_rows)

    geojson = {"type": "FeatureCollection", "name": args.output_geojson.stem, "features": features}
    args.output_geojson.write_text(json.dumps(geojson, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Wrote {args.output_csv} and {args.output_geojson} ({len(features)} points)")
    print(
        "注意: 住所代表点のジオコーディング結果であり、土のう置場の実際の設置位置とは"
        "数メートル〜十数メートルずれる可能性がある。"
    )


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input", type=Path, default=root / "data/naisui_poc/01_raw/shelter/sandbag_locations_ebara.csv"
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=root / "data/naisui_poc/01_raw/shelter/sandbag_locations_nakanobu_futaba.csv",
    )
    parser.add_argument(
        "--output-geojson",
        type=Path,
        default=root / "data/naisui_poc/01_raw/shelter/sandbag_locations_nakanobu_futaba.geojson",
    )
    parser.add_argument("--request-interval-sec", type=float, default=1.0, help="APIへの負荷軽減のための待機時間")
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
