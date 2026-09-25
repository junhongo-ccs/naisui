# OpenStreetMap 道路名

取得日: 2026-09-25  
用途: 町丁目ごとの説明で「どの通り沿いか」を示すため（例: 中延六丁目の三間通り沿い）

| ファイル | 内容 |
| --- | --- |
| `named_roads_2026-09-25.json` | 名前付きの道路（`highway` と `name` のタグを持つway）149本、名前37種。Overpass APIの応答そのまま（ジオメトリ付き） |
| `source_endpoint.txt` | 取得に使ったOverpass APIのエンドポイント |

- 範囲: 中延・二葉＋100mバッファ（南西 35.59983, 139.70468 〜 北東 35.61523, 139.73100）
- クエリ: `[out:json][timeout:90];(way["highway"]["name"](35.59983,139.70468,35.61523,139.73100););out tags geom;`
- OSMデータの時点: 2026-05-31T22:37:44Z（応答の `timestamp_osm_base`）
- overpass-api.de と overpass.kumi.systems は混雑で失敗し、overpass.private.coffee から取得した

## ライセンス

© OpenStreetMap contributors。Open Database License（ODbL）1.0。画面・文書で使うときは出典「© OpenStreetMap contributors」を表示する（地図の背景にはすでに表示している）。

## 注意

- 駐車場の出入庫通路、駅の改札、店名などの道路でない名前も含まれるため、使うときに除外する。
- 名前の無い細い道（多くの路地）は含まれない。雨水がたまりやすい場所のうち、名前付きの道路沿いにあるのは一部である（中延六丁目では、三間通り沿いがたまりやすい面積の30%、立会道路沿いが7%）。
