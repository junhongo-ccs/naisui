# 内水ハザード比較データの台帳

## 現在の比較資料（品川区）

| ファイル | 範囲・条件 | 用途 | 判定 |
| --- | --- | --- | --- |
| `tokyo_jonan_usuisyusui_2026-03-25.pdf` | 城南地区河川流域。品川区を含む。時間最大153mm・総雨量690mm。10mメッシュ。 | 中延・二葉の浸水域の定性比較、将来の地理参照・ベクタ化の原典 | 面データ未入手 |
| `A51-25_13_GML.zip` | 国土数値情報A51東京都版。展開内容は福生市（13218）のみ。 | 品川区の比較には使わない | 対象外 |
| `shinagawa_disaster_map_2026-06.pdf` | 品川区防災地図。雨水出水浸水ハザードマップを含む。 | 中延・二葉を切り出した表示・定性確認 | 補助資料 |

## IoU評価の状態と取得要件

**IoUは未実行です。** 品川区を対象とするGIS面データが未入手のため、PDFや福生市のA51データを
`tools/evaluate_inundation_iou.py` の `--hazard` に渡してはなりません。

次の取得依頼では、以下を明記します。

> 城南地区河川流域・品川区部分・雨水出水（内水）・浸水深区分付き・GIS面データ（GeoJSON / Shapefile / GML）

取得後は、少なくとも対象範囲（中延・二葉を含むこと）、座標系、浸水深属性、想定降雨
（時間最大153mm・総雨量690mm）を確認してから評価対象として登録します。

受領データの検証・正規化は、次のように実行します。

```powershell
uv --system-certs run --with-requirements tools/requirements-surface-water-balance.txt python tools/preprocess_hazard_geojson.py `
  --input <受領ファイル.geojson> `
  --reference-raster data/naisui_poc/02_processed/surface_water_balance/sc_100mm_extreme/maximum_ponding_depth_m.tif `
  --depth-field <浸水深区分の属性名>
```

正常終了すると、対象範囲に重なるポリゴンだけをEPSG:6677で
`02_processed/evaluation/hazard_shinagawa_normalized.gpkg` に出力し、
`depth_min_m`（浸水深区分の下限値、m）を付与します。対象外のデータはエラーで停止します。

## 公式PDFからの派生ベクタ化（公式GIS面データ未入手時のみ）

PDFを地理参照したRGB GeoTIFFを用意した後、凡例から採取したRGBを
`hazard_pdf_colour_classes.template.json` を複製して設定します。テンプレートのRGB値は例示であり、
実際の図から採取せずに使用してはいけません。

```powershell
uv --system-certs run --with-requirements tools/requirements-surface-water-balance.txt python tools/vectorize_georeferenced_hazard.py `
  --input <GCP位置合わせ済みRGB.tif> `
  --classes data/naisui_poc/01_raw/hazard_map/hazard_pdf_colour_classes.json `
  --source-pdf data/naisui_poc/01_raw/hazard_map/tokyo_jonan_usuisyusui_2026-03-25.pdf `
  --gcp-rmse-m <QGISに表示されたRMSE_m>
```

出力には `derived_from_pdf=true` と `gcp_rmse_m` を保持します。これは公式GIS原典ではなく、
モデルケース間の相対的な空間比較のための派生データです。公式GIS面データを入手できた場合は、
必ずそちらへ差し替えます。

## 評価上の注意

本PoCの50/80/100mm/hシナリオと、公式図の153mm/h・総690mmは同一の降雨条件ではありません。
したがって、当面のIoUは**空間的な妥当性比較**であり、予測精度や避難判断の精度を示す数値ではありません。
