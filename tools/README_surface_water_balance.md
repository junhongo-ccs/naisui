# 簡易地表湛水モデル

`run_surface_water_balance.py` は、中延・二葉周辺に取得済みの国土地理院 DEM PNG タイル、降雨時系列、一律の等価排水能力から、地表湛水リスクを計算するスクリプトです。

これは初期 PoC のスクリーニングモデルです。下水道管路・マンホール・ポンプの水理、流速、粗度、道路縁石、建物形状は表現しません。出力を個別地点の浸水深予報や避難指示に使用してはいけません。

## 水収支

各 10 分コマで次を計算します。

`湛水量(t+1) = max(0, 湛水量(t) + (降雨強度 × 流出係数 - 等価排水能力) × Δt)`

基準モデルでは、その後に湛水の一部を最も低い上下左右セルへ1回移します。D8流向・集水量は `flow_direction_d8.tif` と `flow_accumulation_cells.tif` に診断出力しますが、凹地補正・越流を実装するまでD8連続ルーティングの数値は採用しません。初期設定は流出係数 1.0、等価排水能力 50 mm/h です。

## 実行

PowerShell でリポジトリ直下から実行します。

```powershell
uv --system-certs run --with-requirements tools\requirements-surface-water-balance.txt python tools\run_surface_water_balance.py --scenario-id sc_80mm_peak
```

入力は `data/naisui_poc/03_scenarios/rainfall_scenarios.csv` で管理します。`scenario_id` ごとに出力先を `data/naisui_poc/02_processed/surface_water_balance/{scenario_id}/` へ自動分離します。

- `maximum_ponding_depth_m.tif`: 全時刻の最大湛水深
- `final_ponding_depth_m.tif`: 最終時刻の湛水深
- `ponding_depth_t{時刻}min.tif`: 時刻別の湛水深
- `water_balance_summary.csv`: 時刻別の最大深、湛水面積、貯留体積
- `scenario_summary.json`: Dify等が参照できるシナリオ全体の要約
- `run_metadata.json`: 入力・パラメータ・制約

DEM はダウンロード済みタイルの矩形範囲をモザイクしています。中延・二葉の**厳密な町丁目境界でのクリップ**は、境界ポリゴンを取得してから QGIS または GeoPandas で行います。GISで他の品川区データと重ねる際は、出力 GeoTIFF（EPSG:3857）を EPSG:6677 にオンザフライ再投影します。

## DEMの流向・集水量解析

次の処理は `pysheds` により、DEMのピット補正・凹地補正・平坦面補正を行った後、D8流向と集水量をGeoTIFFへ出力します。

```powershell
uv --system-certs run --with-requirements tools\requirements-surface-water-balance.txt python tools\compute_flow_pysheds.py
```

出力先は `data/naisui_poc/02_processed/dem_analysis/` です。特に `flow_accumulation_cells_pysheds.tif` は水みち候補の確認用であり、そのまま浸水深や避難判断に使用しません。現行の水収支モデルへ連結する前に、ハザード区域・道路・鉄道低部との位置関係をQGISで確認します。

## 実験的なPysheds地表流・凹地貯留モデル

`run_pysheds_surface_routing.py` は、凹地補正後のD8流向に沿って超過雨水を一度だけ下流へ伝播し、元DEMから求めた凹地容量へ貯留、容量を超えた分を越流させます。集水量を単純に水量へ乗算しないため、水量を二重計上しません。

```powershell
uv --system-certs run --with-requirements tools\requirements-surface-water-balance.txt python tools\run_pysheds_surface_routing.py --scenario-id sc_100mm_extreme
```

結果は `data/naisui_poc/02_processed/pysheds_surface_routing/sc_100mm_extreme/` に分離して出力します。ハザードとの空間比較・校正が済むまで、標準モデルや避難判断には使用しません。

平滑化DEMと凹地容量上限の感度分析は次で実行します。0.5m、1.0m、1.5mを別フォルダへ出力します。

```powershell
uv --system-certs run --with-requirements tools\requirements-surface-water-balance.txt python tools\run_pysheds_sensitivity.py
```

## 町丁目別 `risk_lookup` の出力

令和2年国勢調査の小地域（町丁・字等）境界を `data/naisui_poc/01_raw/boundaries/shinagawa_town_2020.geojson` として置きます。e-Statの境界データは町丁・字等単位のShape/KML/GML形式を提供しています。取得データの属性名が `S_NAME` でない場合は `--name-field` を指定します。

```powershell
uv --system-certs run --with-requirements tools\requirements-surface-water-balance.txt python tools\export_risk_lookup.py --scenario-dir data\naisui_poc\02_processed\surface_water_balance\sc_80mm_peak --towns data\naisui_poc\01_raw\boundaries\shinagawa_town_2020.geojson --name-field S_NAME
```

スクリプトは中延一〜六丁目・二葉一〜四丁目だけを抽出し、基本単位区など同じ町丁目名のポリゴンが複数ある場合は自動的に結合します。最大・平均湛水深、0.2m以上の面積と割合、ピーク時刻を `risk_lookup_sc_80mm_peak.json` として同じシナリオフォルダに出力します。
