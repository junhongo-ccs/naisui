"""Build per-town objective facts for the Nakanobu/Futaba map (review before use in chat).

町丁目ごとに、データから機械的に求めた客観的事実をまとめる。文章は作らない。
チャットの回答に使う前に、Markdownの一覧で中身を人が確認するためのもの。

- 地形: 標高の最低・中央・最高
- 暗渠（立会川。上部は立会道路・立会川緑道）との位置関係: 町内を通るか、両側の標高、
  たまりやすい場所・公式の浸水想定区域が暗渠のどちら側にあるか
- くぼ地（DEMの窪地の深さ）と谷筋（上流の集水面積）

鉄道用地（PLATEAU土地利用の「鉄道・港湾等」）の中は、たまりやすい場所・くぼ地の集計から除き、別に記録する。
DEMは線路の掘割の底を地面として拾うため、住宅地の浸水とは別物のくぼ地が現れる（中延三丁目の池上線の掘割）。
道路のアンダーパス（OSMで tunnel=yes の道路と、その出入口の坂）も同様に除き、「アンダーパス」として別に記録する
（二葉一丁目のふたばトンネル）。線路の下をくぐる低い道路は、それ自体が大雨時に注意すべき場所である。
- 雨水がたまりやすい場所（採用モデルの最大湛水深が PONDING_MIN_M 以上のセル）:
  - 名前付きの通り（OpenStreetMap）の沿道（両側 CORRIDOR_M）に、町内のたまりやすい面積の何割があるか、
    沿道が周り（外側 RING_M まで）より低いか、公式の浸水想定区域が重なるか
  - 名前付きの通りから外れたまとまり（面積の大きい順）の方角・最寄りの通り
- 公式の浸水想定区域（PDF由来）の深さ区分ごとの面積割合
- 両方が重なる面積
- 過去の浸水実績（R7.9.11、31年累計）
- 町内・最寄りの避難所と土のう置場

出力（既定では data/naisui_poc/02_processed/town_facts/）:
  town_facts.json  町丁目ごとの事実（チャットの回答に使う）
  town_facts.md    確認用の一覧
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.features import geometry_mask
from rasterio.transform import xy
from scipy import ndimage
from shapely.geometry import LineString, Point, box

from count_buildings_by_town import TARGET_TOWN_PATTERN, load_towns
from run_surface_water_balance import ground_cell_areas_m2


WORK_CRS = "EPSG:6677"
PONDING_MIN_M = 0.10  # 地図の色は1cmから付けるが、事実として述べるのは10cm以上とする
CORRIDOR_M = 10.0  # 通りの沿道とみなす片側の幅
RING_M = 60.0  # 沿道と比べる「周り」の外側の幅
MIN_ROAD_LENGTH_M = 50.0  # 町内を通る長さがこれ未満の通りは扱わない
TOP_CLUSTERS = 3
CULVERT_NAMES = {"立会道路", "立会川緑道歩道"}  # 立会川の暗渠の上部（東京都建設局 立会川河川整備計画）
CULVERT_NEAR_M = 300.0  # 暗渠の両側を比べる範囲
CULVERT_BANDS_M = [(0, 50), (50, 100), (100, 200), (200, 300)]
DEPRESSION_MIN_M = 0.10  # くぼ地とみなす窪地の深さ
RAILWAY_LAND_USE = 5200  # PLATEAU土地利用（東京都 orgLandUse）の「鉄道・港湾等」
# 掘割の縁は土地利用の鉄道区画より1セル（約3.9m）ほど外まで地形データに現れるため、その分だけ広げて除く
RAILWAY_BUFFER_M = 6.0
# 道路トンネルの出入口の坂（掘割）まで含めて除くための幅。ふたばトンネルでは窪みの最深部が出入口から3〜5mにある
UNDERPASS_BUFFER_M = 20.0

# 人が現地・地図で確認した事項。データだけでは判断できない解釈を、確認日と一緒に残す。
FIELD_NOTES: dict[str, list[dict[str, str]]] = {
    "中延三丁目": [
        {
            "note": "北西にある深さ約6.5mの窪み（約128m×93m、北緯35.6085・東経139.7096付近）は、池上線が一段低く掘られた掘割を"
            "地形データが拾ったもので、住宅地のくぼ地ではない",
            "confirmed_by": "ユーザー（現地の状況の確認）",
            "confirmed_on": "2026-09-25",
        }
    ],
    "二葉一丁目": [
        {
            "note": "鮫洲大山線の上にある深さ約7.3m・約2.3mの窪み（北緯35.6084・東経139.7256付近）は、線路の下をくぐる道路トンネル"
            "「ふたばトンネル」の出入口の坂を地形データが拾ったもの",
            "confirmed_by": "ユーザー（地名の指摘）。OSMのふたばトンネル（tunnel=yes、layer=-1）の出入口から3〜5mの位置であることを確認",
            "confirmed_on": "2026-09-25",
        }
    ],
}
NOT_ROAD = re.compile(r"駐車場|出入庫|改札|サウナ|路線バス専用|歩道|歩行者")
DIRECTIONS = ["東", "北東", "北", "北西", "西", "南西", "南", "南東"]


def direction_label(dx: float, dy: float) -> str:
    angle = math.degrees(math.atan2(dy, dx)) % 360
    return DIRECTIONS[int((angle + 22.5) // 45) % 8]


def load_roads(path: Path) -> gpd.GeoDataFrame:
    osm = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    for element in osm["elements"]:
        name = element.get("tags", {}).get("name", "")
        if not name or NOT_ROAD.search(name) or len(element.get("geometry", [])) < 2:
            continue
        # 「仲通り (Naka dori Street)」のような併記を除き、「鮫洲大山線（旧道）」等は本線にまとめる
        name = re.sub(r"\s*\(.*\)$", "", name)
        name = re.sub(r"（(旧道|側道|接続部)）$", "", name)
        rows.append({"name": name, "geometry": LineString([(p["lon"], p["lat"]) for p in element["geometry"]])})
    roads = gpd.GeoDataFrame(rows, crs="EPSG:4326").to_crs(WORK_CRS)
    return roads.dissolve(by="name", as_index=False)


def load_underpasses(path: Path) -> gpd.GeoDataFrame:
    """線路などの下をくぐる道路トンネル（OSMで tunnel=yes の道路）。"""
    osm = json.loads(path.read_text(encoding="utf-8"))
    rows = [
        {"name": element["tags"].get("name", ""), "geometry": LineString([(p["lon"], p["lat"]) for p in element["geometry"]])}
        for element in osm["elements"]
        if element.get("tags", {}).get("tunnel") == "yes"
        and element["tags"].get("highway")
        and len(element.get("geometry", [])) >= 2
    ]
    if not rows:
        return gpd.GeoDataFrame({"name": []}, geometry=[], crs=WORK_CRS)
    return gpd.GeoDataFrame(rows, crs="EPSG:4326").to_crs(WORK_CRS).dissolve(by="name", as_index=False)


def load_culvert(path: Path) -> object:
    """立会川の暗渠の位置として、OSMの立会道路・立会川緑道歩道の線を使う。"""
    osm = json.loads(path.read_text(encoding="utf-8"))
    lines = [
        LineString([(p["lon"], p["lat"]) for p in element["geometry"]])
        for element in osm["elements"]
        if element.get("tags", {}).get("name") in CULVERT_NAMES and len(element.get("geometry", [])) >= 2
    ]
    return gpd.GeoSeries(lines, crs="EPSG:4326").to_crs(WORK_CRS).union_all()


def read_records(path: Path) -> dict[str, dict[str, object]]:
    with path.open(encoding="utf-8") as file:
        return {row["town"]: row for row in csv.DictReader(file)}


def points(path: Path, label_fields: list[str]) -> gpd.GeoDataFrame:
    gdf = gpd.read_file(path).to_crs(WORK_CRS)
    gdf["label"] = [
        next((str(row[field]) for field in label_fields if field in row and row[field]), "") for _, row in gdf.iterrows()
    ]
    return gdf


def nearest(gdf: gpd.GeoDataFrame, geometry: object) -> dict[str, object]:
    distances = gdf.distance(geometry)
    index = distances.idxmin()
    return {"name": gdf.loc[index, "label"], "distance_m": round(float(distances[index]))}


class Grid:
    """モデル格子（EPSG:3857）上でのマスクと面積の計算。"""

    def __init__(self, depth_path: Path, dem_path: Path, landuse_path: Path, underpasses: gpd.GeoDataFrame) -> None:
        with rasterio.open(depth_path) as dataset:
            self.depth = dataset.read(1).astype(np.float64)
            self.transform = dataset.transform
            self.crs = dataset.crs
        with rasterio.open(dem_path) as dataset:
            self.dem = dataset.read(1).astype(np.float64)
        # モデル実行時に出力される窪地の深さと、上流のセル数（同じ格子）
        with rasterio.open(depth_path.parent / "depression_depth_m.tif") as dataset:
            self.depression = dataset.read(1).astype(np.float64)
        with rasterio.open(depth_path.parent / "flow_accumulation_cells_pysheds.tif") as dataset:
            self.upstream_cells = dataset.read(1).astype(np.float64)
        self.area = np.broadcast_to(ground_cell_areas_m2(self.transform, self.crs, self.depth.shape[0]), self.depth.shape)
        self.valid_dem = self.dem > -100
        # 鉄道用地は、たまりやすい場所・くぼ地の集計から除く（掘割の底を地形として拾うため）
        self.railway = self._railway_mask(landuse_path)
        self.underpass = (
            self.mask(underpasses.geometry.buffer(UNDERPASS_BUFFER_M).union_all()) if len(underpasses) else np.zeros_like(self.railway)
        )
        self.excluded = self.railway | self.underpass
        self.ponding_all = self.depth >= PONDING_MIN_M
        self.ponding = self.ponding_all & ~self.excluded

    def _railway_mask(self, landuse_path: Path) -> np.ndarray:
        bounds = rasterio.transform.array_bounds(self.depth.shape[0], self.depth.shape[1], self.transform)
        bbox = tuple(gpd.GeoSeries([box(*bounds)], crs=self.crs).to_crs("EPSG:6668").total_bounds)
        landuse = gpd.read_file(landuse_path, bbox=bbox)
        railway = landuse[landuse["orgLandUse"] == RAILWAY_LAND_USE].to_crs(WORK_CRS)
        if railway.empty:
            return np.zeros(self.depth.shape, dtype=bool)
        widened = railway.geometry.buffer(RAILWAY_BUFFER_M).to_crs(self.crs)
        return ~geometry_mask(list(widened), self.depth.shape, self.transform)

    def mask(self, geometry: object) -> np.ndarray:
        if geometry.is_empty:
            return np.zeros(self.depth.shape, dtype=bool)
        projected = gpd.GeoSeries([geometry], crs=WORK_CRS).to_crs(self.crs).iloc[0]
        return ~geometry_mask([projected], self.depth.shape, self.transform)

    def cell_point(self, row: float, col: float) -> Point:
        x, y = xy(self.transform, row, col)
        return gpd.GeoSeries([Point(x, y)], crs=self.crs).to_crs(WORK_CRS).iloc[0]

    def cell_points(self, mask: np.ndarray) -> tuple[np.ndarray, np.ndarray, gpd.GeoSeries]:
        rows, cols = np.nonzero(mask)
        xs, ys = xy(self.transform, rows, cols)
        return rows, cols, gpd.GeoSeries(gpd.points_from_xy(xs, ys), crs=self.crs).to_crs(WORK_CRS)


def culvert_facts(
    town: object, grid: Grid, culvert: object, town_mask: np.ndarray, ponding_mask: np.ndarray, hazard_mask: np.ndarray
) -> dict[str, object]:
    """暗渠との位置関係。暗渠の両側で、標高・たまりやすい場所・公式の浸水想定区域を比べる。"""
    distance = float(culvert.distance(town))
    facts: dict[str, object] = {
        "passes_through_town": bool(culvert.intersects(town)),
        "length_in_town_m": round(culvert.intersection(town).length),
        "distance_from_town_m": round(distance),
    }
    if distance > CULVERT_NEAR_M:
        return facts
    local = culvert.intersection(town.buffer(CULVERT_NEAR_M))
    coords = np.array([c for part in getattr(local, "geoms", [local]) for c in part.coords])
    # 暗渠の大まかな向き（主軸）に直交する向きで、両側を分ける
    centered = coords - coords.mean(axis=0)
    axis = np.linalg.svd(centered, full_matrices=False)[2][0]
    normal = np.array([-axis[1], axis[0]])
    rows, cols, pts = grid.cell_points(town_mask)
    nearest_on_line = [local.interpolate(local.project(p)) for p in pts]
    offset = np.array([[p.x - q.x, p.y - q.y] for p, q in zip(pts, nearest_on_line)])
    dist = np.hypot(offset[:, 0], offset[:, 1])
    side_positive = offset @ normal > 0
    area = grid.area[rows, cols]
    elevation = grid.dem[rows, cols]
    ponding = ponding_mask[rows, cols]
    hazard = hazard_mask[rows, cols]
    near = dist < CULVERT_NEAR_M
    sides = []
    for sign, selector in ((1, side_positive), (-1, ~side_positive)):
        vector = normal * sign
        cells = selector & near
        bands = []
        for low, high in CULVERT_BANDS_M:
            band = cells & (dist >= low) & (dist < high)
            if area[band].sum() < 1000:
                continue
            bands.append({
                "from_m": low,
                "to_m": high,
                "elevation_median_m": round(float(np.median(elevation[band])), 2),
                "ponding_share": round(float(area[band & ponding].sum() / area[band].sum()), 3),
                "official_hazard_share": round(float(area[band & hazard].sum() / area[band].sum()), 3),
            })
        sides.append({
            "direction": direction_label(vector[0], vector[1]),
            "share_of_town_area": round(float(area[selector].sum() / area.sum()), 3),
            "share_of_town_ponding": round(float(area[selector & ponding].sum() / area[ponding].sum()), 3) if area[ponding].sum() else 0.0,
            "share_of_town_official_hazard": round(float(area[selector & hazard].sum() / area[hazard].sum()), 3) if area[hazard].sum() else 0.0,
            "bands": bands,
        })
    facts["sides"] = sides
    return facts


def town_facts(
    name: str,
    town: object,
    grid: Grid,
    roads: gpd.GeoDataFrame,
    hazard: gpd.GeoDataFrame,
    records: dict[str, dict[str, object]],
    shelters: gpd.GeoDataFrame,
    sandbags: gpd.GeoDataFrame,
    culvert: object,
    underpasses: gpd.GeoDataFrame,
) -> dict[str, object]:
    town_mask = grid.mask(town)
    elevations = grid.dem[town_mask & grid.valid_dem]
    town_area = float(grid.area[town_mask].sum())
    ponding_mask = town_mask & grid.ponding
    ponding_area = float(grid.area[ponding_mask].sum())

    def percentile_in_town(value: float) -> int:
        return round(100 * float((elevations < value).mean()))

    facts: dict[str, object] = {
        "town": name,
        "area_m2": round(town_area),
        "elevation_m": {
            "min": round(float(elevations.min()), 2),
            "median": round(float(np.median(elevations)), 2),
            "max": round(float(elevations.max()), 2),
        },
        "ponding": {
            "threshold_m": PONDING_MIN_M,
            "area_m2": round(ponding_area),
            "share_of_town": round(ponding_area / town_area, 4),
            # 最大値はDEMの誤差に支配されることがある（照合レビュー 3章）ため、上位5%の値を示す
            "depth_p95_m": round(float(np.percentile(grid.depth[ponding_mask], 95)), 2) if ponding_area else 0.0,
        },
    }

    # 名前付きの通りの沿道
    road_rows = []
    corridors_union = []
    for _, road in roads.iterrows():
        line = road.geometry.intersection(town)
        if line.is_empty or line.length < MIN_ROAD_LENGTH_M:
            continue
        corridor = line.buffer(CORRIDOR_M).intersection(town)
        ring = line.buffer(RING_M).difference(line.buffer(CORRIDOR_M)).intersection(town)
        corridors_union.append(corridor)
        corridor_mask = grid.mask(corridor)
        ring_mask = grid.mask(ring)
        corridor_ponding = float(grid.area[corridor_mask & grid.ponding].sum())
        corridor_elevation = float(np.median(grid.dem[corridor_mask & grid.valid_dem]))
        ring_elevation = float(np.median(grid.dem[ring_mask & grid.valid_dem])) if (ring_mask & grid.valid_dem).any() else math.nan
        hazard_in_corridor = hazard[hazard.intersects(corridor)]
        hazard_area = float(hazard_in_corridor.intersection(corridor).area.sum()) if len(hazard_in_corridor) else 0.0
        road_rows.append({
            "road": road["name"],
            "length_in_town_m": round(line.length),
            "ponding_area_m2": round(corridor_ponding),
            "share_of_town_ponding": round(corridor_ponding / ponding_area, 3) if ponding_area else 0.0,
            "ponding_share_of_corridor": round(corridor_ponding / float(grid.area[corridor_mask].sum()), 3),
            "corridor_elevation_m": round(corridor_elevation, 2),
            "surrounding_elevation_m": None if math.isnan(ring_elevation) else round(ring_elevation, 2),
            "lower_than_surroundings_m": None if math.isnan(ring_elevation) else round(ring_elevation - corridor_elevation, 2),
            "elevation_percentile_in_town": percentile_in_town(corridor_elevation),
            "official_hazard_share_of_corridor": round(hazard_area / corridor.area, 3) if corridor.area else 0.0,
            "official_hazard_classes": sorted(set(hazard_in_corridor["depth_class"])) if len(hazard_in_corridor) else [],
        })
    facts["roads"] = sorted(road_rows, key=lambda row: -row["ponding_area_m2"])

    # 名前付きの通りから外れた、たまりやすい場所のまとまり
    corridor_mask_all = grid.mask(gpd.GeoSeries(corridors_union, crs=WORK_CRS).union_all()) if corridors_union else np.zeros_like(town_mask)
    off_road = ponding_mask & ~corridor_mask_all
    labels, count = ndimage.label(off_road, structure=np.ones((3, 3), dtype=bool))
    clusters = []
    town_center = town.representative_point()
    for label_id in range(1, count + 1):
        cells = labels == label_id
        area = float(grid.area[cells].sum())
        rows, cols = np.nonzero(cells)
        center = grid.cell_point(float(rows.mean()), float(cols.mean()))
        cluster_elevation = float(np.median(grid.dem[cells & grid.valid_dem])) if (cells & grid.valid_dem).any() else math.nan
        nearby = roads.distance(center)
        clusters.append({
            "area_m2": round(area),
            "share_of_town_ponding": round(area / ponding_area, 3) if ponding_area else 0.0,
            "direction_in_town": direction_label(center.x - town_center.x, center.y - town_center.y),
            "nearest_named_road": roads.loc[nearby.idxmin(), "name"] if len(roads) else None,
            "nearest_named_road_m": round(float(nearby.min())) if len(roads) else None,
            "elevation_percentile_in_town": percentile_in_town(cluster_elevation) if not math.isnan(cluster_elevation) else None,
            "overlaps_official_hazard": bool(hazard.intersects(center.buffer(5)).any()),
        })
    clusters.sort(key=lambda row: -row["area_m2"])
    facts["off_road_ponding"] = {
        "share_of_town_ponding": round(float(grid.area[off_road].sum()) / ponding_area, 3) if ponding_area else 0.0,
        "cluster_count": count,
        "largest": clusters[:TOP_CLUSTERS],
    }

    # 公式の浸水想定区域（PDF由来）
    hazard_in_town = hazard[hazard.intersects(town)].copy()
    hazard_in_town["area_in_town"] = hazard_in_town.intersection(town).area
    by_class = hazard_in_town.groupby("depth_class")["area_in_town"].sum()
    order = hazard_in_town.drop_duplicates("depth_class").sort_values("depth_min_m")["depth_class"].tolist()
    facts["official_hazard"] = {
        "share_of_town": round(float(hazard_in_town["area_in_town"].sum()) / town.area, 4),
        "share_by_depth_class": {depth_class: round(float(by_class[depth_class]) / town.area, 4) for depth_class in order},
        "deepest_class": order[-1] if order else None,
    }
    hazard_mask = grid.mask(hazard_in_town.union_all()) if len(hazard_in_town) else np.zeros_like(town_mask)
    overlap = float(grid.area[ponding_mask & hazard_mask].sum())
    facts["ponding_in_official_hazard"] = {
        "area_m2": round(overlap),
        "share_of_ponding": round(overlap / ponding_area, 3) if ponding_area else 0.0,
    }

    facts["culvert"] = culvert_facts(town, grid, culvert, town_mask, ponding_mask, hazard_mask)

    # 鉄道用地の中にあって集計から除いた分
    railway_in_town = town_mask & grid.railway
    railway_depression = railway_in_town & (grid.depression >= DEPRESSION_MIN_M)
    facts["railway_excluded"] = {
        "railway_share_of_town": round(float(grid.area[railway_in_town].sum()) / town_area, 4),
        "ponding_area_m2": round(float(grid.area[railway_in_town & grid.ponding_all].sum())),
        "depression_area_m2": round(float(grid.area[railway_depression].sum())),
        "depression_depth_max_m": round(float(grid.depression[railway_depression].max()), 2) if railway_depression.any() else 0.0,
    }
    underpass_rows = []
    for _, underpass in underpasses.iterrows():
        zone = underpass.geometry.buffer(UNDERPASS_BUFFER_M)
        if not zone.intersects(town):
            continue
        zone_mask = grid.mask(zone.intersection(town))
        underpass_rows.append({
            "name": underpass["name"],
            "depression_depth_max_m": round(float(grid.depression[zone_mask].max()), 2) if zone_mask.any() else 0.0,
            "ponding_area_m2": round(float(grid.area[zone_mask & grid.ponding_all].sum())),
        })
    facts["underpasses"] = underpass_rows
    facts["field_notes"] = FIELD_NOTES.get(name, [])

    # くぼ地（窪地の深さ）と谷筋（上流の集水面積）。鉄道用地は除く
    depression_mask = town_mask & (grid.depression >= DEPRESSION_MIN_M) & ~grid.excluded
    depression_labels, depression_count = ndimage.label(depression_mask, structure=np.ones((3, 3), dtype=bool))
    sizes = ndimage.sum(np.ones_like(grid.depression), depression_labels, range(1, depression_count + 1)) if depression_count else []
    upstream_m2 = grid.upstream_cells * grid.area
    peak_index = np.unravel_index(np.argmax(np.where(town_mask, upstream_m2, -1)), upstream_m2.shape)
    peak_point = grid.cell_point(float(peak_index[0]), float(peak_index[1]))
    facts["terrain"] = {
        "depression_share_of_town": round(float(grid.area[depression_mask].sum()) / town_area, 4),
        "depression_count_2cells_or_more": int(sum(1 for size in sizes if size >= 2)),
        "depression_depth_p95_m": round(float(np.percentile(grid.depression[depression_mask], 95)), 2) if depression_mask.any() else 0.0,
        "ponding_in_depressions_share": round(float(grid.area[ponding_mask & depression_mask].sum()) / ponding_area, 3) if ponding_area else 0.0,
        "max_upstream_area_ha": round(float(upstream_m2[peak_index]) / 10_000, 1),
        "max_upstream_direction_in_town": direction_label(peak_point.x - town_center.x, peak_point.y - town_center.y),
    }

    record = records.get(name, {})
    facts["records"] = {
        "r7_0911_class": record.get("r7_class_label") or None,
        "r7_0911_confidence": record.get("r7_confidence") or None,
        "history_1989_2020_buildings": int(record["history_total_buildings"]) if record.get("history_total_buildings") else None,
        "history_1989_2020_abovefloor": int(record["history_abovefloor_buildings"]) if record.get("history_abovefloor_buildings") else None,
    }

    facts["facilities"] = {
        "shelters_in_town": shelters[shelters.within(town)]["label"].tolist(),
        "nearest_shelter": nearest(shelters, town.representative_point()),
        "sandbags_in_town": sandbags[sandbags.within(town)]["label"].tolist(),
        "nearest_sandbag": nearest(sandbags, town.representative_point()),
    }
    return facts


def to_markdown(all_facts: list[dict[str, object]], metadata: dict[str, object]) -> str:
    lines = [
        "# 町丁目ごとの客観的事実（確認用）",
        "",
        f"生成: {metadata['generated_at']}　モデル: `{metadata['model_version']}`　"
        f"たまりやすい場所の基準: 最大湛水深{PONDING_MIN_M}m以上　沿道: 通りの両側{CORRIDOR_M:g}m",
        "",
        "数値はデータから機械的に求めたもの。文章表現と、チャットで述べてよいかの判断はこの一覧を確認してから行う。",
        "",
    ]
    for facts in all_facts:
        ponding = facts["ponding"]
        hazard = facts["official_hazard"]
        records = facts["records"]
        lines += [
            f"## {facts['town']}",
            "",
            f"- 標高: 最低{facts['elevation_m']['min']}m・中央{facts['elevation_m']['median']}m・最高{facts['elevation_m']['max']}m",
            f"- 雨水がたまりやすい面積: {ponding['area_m2']:,}m²（町の{ponding['share_of_town']:.1%}）、深さの上位5%値 {ponding['depth_p95_m']}m",
            f"- 公式の浸水想定区域: 町の{hazard['share_of_town']:.1%}（"
            + "、".join(f"{k} {v:.1%}" for k, v in hazard["share_by_depth_class"].items())
            + "）",
            f"- たまりやすい場所のうち公式の浸水想定区域と重なる割合: {facts['ponding_in_official_hazard']['share_of_ponding']:.0%}",
            f"- 過去の浸水: R7.9.11 {records['r7_0911_class']}（{records['r7_0911_confidence']}）、"
            f"1989〜2020年 {records['history_1989_2020_buildings'] if records['history_1989_2020_buildings'] is not None else '記録なし'}棟",
            f"- くぼ地（深さ{DEPRESSION_MIN_M}m以上）: 町の{facts['terrain']['depression_share_of_town']:.1%}、"
            f"{facts['terrain']['depression_count_2cells_or_more']}か所、深さの上位5%値 {facts['terrain']['depression_depth_p95_m']}m。"
            f"たまりやすい場所のうちくぼ地にある割合 {facts['terrain']['ponding_in_depressions_share']:.0%}",
            f"- 谷筋: 町内で上流の集水面積が最大の地点は町の{facts['terrain']['max_upstream_direction_in_town']}側で"
            f"{facts['terrain']['max_upstream_area_ha']}ha",
            f"- 集計から除いた鉄道用地: 町の{facts['railway_excluded']['railway_share_of_town']:.1%}"
            f"（中のたまりやすい場所 {facts['railway_excluded']['ponding_area_m2']:,}m²、"
            f"くぼ地 {facts['railway_excluded']['depression_area_m2']:,}m²・最深 {facts['railway_excluded']['depression_depth_max_m']}m）",
        ]
        for underpass in facts["underpasses"]:
            lines.append(
                f"- アンダーパス: {underpass['name']}（線路などの下をくぐる道路。地形データでは周りより最大"
                f"{underpass['depression_depth_max_m']}m低い。集計から除外）"
            )
        for note in facts["field_notes"]:
            lines.append(f"- 確認事項: {note['note']}（{note['confirmed_by']}、{note['confirmed_on']}）")
        lines += [
            "",
        ]
        culvert = facts["culvert"]
        if culvert["passes_through_town"]:
            lines.append(f"暗渠（立会川）: 町内を{culvert['length_in_town_m']}m通る")
        else:
            lines.append(f"暗渠（立会川）: 町内を通らない（町から{culvert['distance_from_town_m']}m）")
        for side in culvert.get("sides", []):
            lines.append(
                f"- 暗渠の{side['direction']}側: 町の面積の{side['share_of_town_area']:.0%}、"
                f"たまりやすい場所の{side['share_of_town_ponding']:.0%}、公式の浸水想定区域の{side['share_of_town_official_hazard']:.0%}"
            )
            for band in side["bands"]:
                lines.append(
                    f"  - 暗渠から{band['from_m']}〜{band['to_m']}m: 標高 {band['elevation_median_m']}m、"
                    f"たまりやすい {band['ponding_share']:.1%}、浸水想定 {band['official_hazard_share']:.1%}"
                )
        lines += [
            "",
            "| 通り | 町内の長さ | 町内のたまりやすい面積に占める割合 | 沿道のうちたまりやすい割合 | 周りより低い | 町内の標高の低い方から | 沿道の公式想定区域 |",
            "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
        for road in facts["roads"]:
            lower = road["lower_than_surroundings_m"]
            lines.append(
                f"| {road['road']} | {road['length_in_town_m']}m | {road['share_of_town_ponding']:.0%} | "
                f"{road['ponding_share_of_corridor']:.0%} | {'—' if lower is None else f'{lower:+.2f}m'} | "
                f"{road['elevation_percentile_in_town']}% | {road['official_hazard_share_of_corridor']:.0%} "
                f"{'・'.join(road['official_hazard_classes'])} |"
            )
        off = facts["off_road_ponding"]
        lines += ["", f"名前付きの通りから外れた場所: 町内のたまりやすい面積の{off['share_of_town_ponding']:.0%}（{off['cluster_count']}か所）。大きい順:", ""]
        for cluster in off["largest"]:
            lines.append(
                f"- 町の{cluster['direction_in_town']}側 {cluster['area_m2']:,}m²（{cluster['share_of_town_ponding']:.0%}）、"
                f"最寄りの通り {cluster['nearest_named_road']}（{cluster['nearest_named_road_m']}m）、"
                f"標高は町内の低い方から{cluster['elevation_percentile_in_town']}%、"
                f"公式想定区域{'あり' if cluster['overlaps_official_hazard'] else 'なし'}"
            )
        fac = facts["facilities"]
        lines += [
            "",
            f"- 避難所: 町内 {('、'.join(fac['shelters_in_town']) or 'なし')}／最寄り {fac['nearest_shelter']['name']}（{fac['nearest_shelter']['distance_m']}m）",
            f"- 土のう置場: 町内 {('、'.join(fac['sandbags_in_town']) or 'なし')}／最寄り {fac['nearest_sandbag']['name']}（{fac['nearest_sandbag']['distance_m']}m）",
            "",
        ]
    return "\n".join(lines)


def run(args: argparse.Namespace) -> None:
    towns = load_towns(args.towns, "S_NAME", TARGET_TOWN_PATTERN)
    underpasses = load_underpasses(args.roads)
    grid = Grid(args.depth, args.dem, args.landuse, underpasses)
    roads = load_roads(args.roads)
    hazard = gpd.read_file(args.hazard).to_crs(WORK_CRS)
    records = read_records(args.records)
    shelters = points(args.shelters, ["name"])
    sandbags = points(args.sandbags, ["landmark", "address"])
    culvert = load_culvert(args.roads)

    all_facts = [
        town_facts(name, geometry, grid, roads, hazard, records, shelters, sandbags, culvert, underpasses)
        for name, geometry in sorted(zip(towns["town"], towns.geometry), key=lambda item: item[0])
    ]
    metadata = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "model_version": args.model_version,
        "inputs": {key: str(getattr(args, key)) for key in ("depth", "dem", "roads", "landuse", "hazard", "records", "shelters", "sandbags", "towns")},
        "ponding_min_m": PONDING_MIN_M,
        "corridor_m": CORRIDOR_M,
        "ring_m": RING_M,
        "notes": [
            "雨水がたまりやすい場所は校正前のスクリーニングモデルの結果であり、実際の浸水予報ではない。",
            "公式の浸水想定区域は公式PDFを地理参照して作った派生データで、位置の誤差は約4.5m（最大約7.8m）。",
            "道路名は © OpenStreetMap contributors（ODbL）。名前の無い路地は含まれない。",
            "鉄道用地（PLATEAU土地利用の鉄道・港湾等、縁を6m広げる）の中は、たまりやすい場所・くぼ地の集計から除いている（railway_excluded に別記）。",
            "道路のアンダーパス（OSMで tunnel=yes の道路の周り20m）も集計から除き、underpasses に別記している。",
        ],
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "town_facts.json").write_text(
        json.dumps({"metadata": metadata, "towns": all_facts}, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (args.output_dir / "town_facts.md").write_text(to_markdown(all_facts, metadata), encoding="utf-8")
    print(f"Wrote facts for {len(all_facts)} towns -> {args.output_dir}")


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[1]
    processed = root / "data/naisui_poc/02_processed"
    raw = root / "data/naisui_poc/01_raw"
    version = "plateau2025_v3_road050"
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model-version", default=version)
    parser.add_argument(
        "--depth",
        type=Path,
        default=processed / f"pysheds_surface_routing_roads/{version}/sc_153mmh_24h_690mm_official/maximum_ponding_depth_m.tif",
    )
    parser.add_argument("--dem", type=Path, default=processed / "pysheds_surface_routing/sc_100mm_extreme/dem_raw_epsg3857.tif")
    parser.add_argument("--roads", type=Path, default=raw / "osm/named_roads_2026-09-25.json")
    parser.add_argument("--landuse", type=Path, default=processed / "plateau/luse_2025.gpkg")
    parser.add_argument("--hazard", type=Path, default=processed / "evaluation/hazard_shinagawa_normalized.gpkg")
    parser.add_argument("--records", type=Path, default=processed / "plateau/inundation_history_normalized.csv")
    parser.add_argument("--shelters", type=Path, default=raw / "shelter/shelter_locations_nakanobu_futaba.geojson")
    parser.add_argument("--sandbags", type=Path, default=raw / "shelter/sandbag_locations_nakanobu_futaba.geojson")
    parser.add_argument("--towns", type=Path, default=raw / "boundaries/r2kb13109.shp")
    parser.add_argument("--output-dir", type=Path, default=processed / "town_facts")
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
