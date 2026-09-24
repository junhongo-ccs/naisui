# 中延・二葉 Pysheds凹地容量 — 感度分析

## 共通条件

- 降雨シナリオ: `sc_100mm_extreme`
- 入力DEM: `dem_median_3x3.tif`
- 処理: Pyshedsによる凹地補正・D8流向・集水量、および水量保存型の凹地貯留・越流
- 位置づけ: 校正用の実験ケース。避難判断には使用しない。

## ケース定義と実行結果

| ケース | 出力フォルダ | 凹地容量上限 | 評価ポイント | 最大湛水深 | 最終貯留量 |
|---|---|---:|---|---:|---:|
| Case A | `median3_cap0p5m` | 0.5m | 軽微な道路冠水レベルに抑えた場合の挙動 | 約0.49m | 約103,838m³ |
| Case B | `median3_cap1m` | 1.0m | 床下・床上浸水境界レベルの標準的な挙動 | 約0.99m | 約116,749m³ |
| Case C | `median3_cap1p5m` | 1.5m | アンダーパス等の深い貯留を許容した場合の挙動 | 約1.49m | 約122,975m³ |

各ケースは `data/naisui_poc/02_processed/pysheds_sensitivity/{case}/sc_100mm_extreme/` に、最大・時刻別湛水深、D8流向、集水量、凹地深、町丁目別`risk_lookup`を保存している。

## 比較方法

1. QGISで各ケースの`maximum_ponding_depth_m.tif`と、`depression_candidates.geojson`、道路・鉄道・品川区ハザードを重ねる。
2. 0.1m・0.2mの浸水閾値ごとに、ハザード区域とのJaccard係数を算出する。
3. 実績地点の捕捉率と、町丁目別の深さ順位が浸水実績と整合するかを確認する。
4. 指標が最良のケースを候補とし、地形・構造物上の不自然な凹地がないことを確認してから採用する。

## IoUの自動評価

品川区の内水浸水区域をポリゴン（GeoJSON、GeoPackage、Shapefile等）として取得・位置合わせできた後、以下を実行する。

```powershell
uv --system-certs run --with-requirements tools\requirements-surface-water-balance.txt python tools\evaluate_inundation_iou.py `
  --hazard data\naisui_poc\01_raw\hazard_map\inland_flood_hazard.geojson `
  --model case_a=data\naisui_poc\02_processed\pysheds_sensitivity\median3_cap0p5m\sc_100mm_extreme\maximum_ponding_depth_m.tif `
  --model case_b=data\naisui_poc\02_processed\pysheds_sensitivity\median3_cap1m\sc_100mm_extreme\maximum_ponding_depth_m.tif `
  --model case_c=data\naisui_poc\02_processed\pysheds_sensitivity\median3_cap1p5m\sc_100mm_extreme\maximum_ponding_depth_m.tif
```

`0.1m`と`0.2m`の両方でIoUを計算する。IoUだけで採用せず、実績地点の捕捉率と、アンダーパス等の重要地点を不自然に除外していないことも確認する。
