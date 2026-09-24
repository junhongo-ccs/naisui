# 品川区内水ハザードPDF：地理参照・色採取記録

更新日: 2026-09-14  
用途: 中延・二葉 PoCにおける、公式PDF由来の比較用浸水域データ作成

## 原典

- PDF: `data/naisui_poc/01_raw/hazard_map/tokyo_jonan_usuisyusui_2026-03-25.pdf`
- 資料名: 城南地区河川流域 雨水出水浸水想定区域図
- 出力GeoTIFF: `data/naisui_poc/01_raw/hazard_map/shinagawa_georeferenced.tif`
- 座標参照系: JGD2011 / Japan Plane Rectangular CS IX（EPSG:6677）

## 地理参照

- 変換方式: 線形（Linear）
- リサンプリング: 最近傍法（色値を保持するため）
- 有効GCP: ID 1〜5 の5点
- 除外GCP: ID 0（残差が大きいため）
- 有効GCPのRMSE: 約 **4.5 m**
- 有効GCPの最大残差: 約 **7.84 m**

このGeoTIFFおよび以降に作るベクタは、公式GIS原典ではなく、公式PDFを地理参照して作成した派生データである。10mメッシュ相当の想定浸水域との**相対的な空間比較用**に限り用い、絶対精度を保証しない。

## 採取済みの凡例カラー

QGISの「地物情報表示」で、PDF内の凡例の各色見本中央を採取する。地図上の塗りつぶしは道路・文字等との混色の可能性があるため、凡例からの直接採取値を正とする。

| 浸水深区分 | RGB | 状態 |
| --- | --- | --- |
| 0.1m以上 0.5m未満 | `(247, 245, 170)` | 凡例から採取済み |
| 0.5m以上 1.0m未満 | `(247, 225, 167)` | 凡例から採取済み |
| 1.0m以上 3.0m未満 | `(254, 217, 191)` | 凡例から採取済み |
| 3.0m以上 5.0m未満 | `(255, 183, 184)` | 凡例から採取済み |
| 5.0m以上 | `(255, 145, 144)` | 凡例から採取済み |

5区分すべてを凡例から採取済みである。

## 後続処理の注意

- ベクタ化設定には、採取済みの実測RGB値のみを登録する。テンプレート中のRGB例は使用しない。
- 出力属性には `derived_from_pdf=true`、`gcp_rmse_m=4.5`、原典PDFパス、想定降雨条件を保持する。
- 原典の想定降雨（最大時間雨量153mm・総雨量690mm）はPoCの50/80/100mm/hケースと一致しない。IoUはケース間の相対比較として扱う。

## 生成・相対比較の実行結果

- PDF由来GeoJSON: `data/naisui_poc/02_processed/evaluation/shinagawa_hazard_from_pdf.geojson`
  - 生成ポリゴン数: 21,076
- 対象範囲へ正規化した評価用GeoPackage: `data/naisui_poc/02_processed/evaluation/hazard_shinagawa_normalized.gpkg`
  - 対象範囲に重なるポリゴン数: 2,486
- IoU結果: `data/naisui_poc/02_processed/evaluation/iou_pdf_derived_vs_pysheds_cases.csv`

| 比較閾値 | Case A（凹地容量0.5m） | Case B（1.0m） | Case C（1.5m） |
| --- | ---: | ---: | ---: |
| 0.1m | 0.01967 | 0.01905 | 0.01891 |
| 0.2m | 0.01130 | 0.01083 | 0.01071 |

この限定比較ではCase Aが両閾値で最大だった。しかし、公式図とPoCで降雨条件・作成手法・解像度が一致しないうえ、公式図側もPDF地理参照による派生ベクタである。この結果だけでモデルや凹地容量を採用決定してはならない。
