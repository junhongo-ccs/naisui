# PLATEAU 3D都市モデル（品川区）

取得日: 2026-09-25  
用途: PLATEAU導入計画 フェーズ0B（町丁目別建物棟数による浸水実績の正規化）

## 保存データ

| ファイル | 内容 |
| --- | --- |
| `bldg/533935{26,27,28,36,37,38}_bldg_6697_op.gml` | 建築物モデル（CityGML、EPSG:6697）。中延・二葉＋100mバッファの約99.9%を含む3次メッシュ6面 |
| `13109_shinagawa-ku_pref_2025_citygml_1_op_codelists.zip` | コードリスト（属性の数値コードの意味） |
| `catalog_query_2026-09-25.json` | 取得時のCityGMLカタログAPIの応答（ファイルURL・地物数の記録） |
| `urls.txt` | 実際に取得したURL、APIが示すファイルサイズ・地物数 |

GML・ZIPは容量が大きいため `.gitignore` で除外している。再取得は `urls.txt` のURLから行う。URLは版ごとのIDを含むため、改版後は次のAPIで引き直す。

```
https://api.plateauview.mlit.go.jp/datacatalog/citygml/r:139.70468,35.59983,139.73100,35.61523
```

## 出所

- データセット: `plateau-13109-shinagawa-ku-2025`（品川区 2025年度、CityGML仕様5.0、東京都整備データ `pref`）
- 配信: PLATEAU配信サービス（CityGMLカタログAPI）、G空間情報センター
- ライセンス: G空間情報センターの登録上「PLATEAU Site Policy『3. 著作権について』に拠る」（https://www.mlit.go.jp/plateau/site-policy/ ）。本文と出典表記の方法は未確認であり、成果を公開する前に確認すること。

## 取得時の確認結果

- 6ファイルとも、`bldg:Building` の数がAPIの `features` と一致し、末尾の閉じタグまで揃っていた（計32,173棟）。ディスク上のサイズはAPIの `fileSize` より約1%大きいが、内容は完全である。
- 東京都整備データのため、ファイルは区ではなくメッシュ単位で、区境の外の建物も含む。
- `53393528`（大井・東大井周辺）の832棟はLOD2形状を持ち、ogr2ogrで変換すると形状が空になる。LOD0外形で確認したところ中延・二葉の町丁目内には1棟も無い（最短6m外）。
- 建物の災害リスク属性は `uro:RiverFloodingRiskAttribute` のみで、内水専用の属性は無い。`description=14`（城南地区河川流域）、`adminType=2`（都道府県）、`scale=2`（L2想定最大規模）、`rank` は浸水深6区分（1: 0.5m未満 〜 6: 20m以上）。東京都の城南地区河川流域浸水予想区域図に由来するとみられ、校正値ではなく相対比較用として扱う。

## 変換

QGIS 3.44同梱のGDAL 3.12で、6ファイルを一つのGeoPackageレイヤーへ結合した。

```bash
export GDAL_DATA="C:/Program Files/QGIS 3.44.9/apps/gdal/share/gdal"
out=data/naisui_poc/02_processed/plateau/bldg_2025.gpkg; mode=""
for f in data/naisui_poc/01_raw/plateau/bldg/*.gml; do
  ogr2ogr $mode -oo EXPOSE_GML_ID=YES -f GPKG $out $f Building -nlt MULTIPOLYGON -dim XY -nln bldg
  mode="-append -addfields"
done
```

- `-oo EXPOSE_GML_ID=YES` は必須。`Appearance` を含むファイル（LOD2あり）では、これが無いと `gml_id` が列にならず追記が失敗する。
- `lod1Solid` を平面のMultiPolygonへ変換するため、形状は屋根面と底面が重なった不正な形になる。`tools/count_buildings_by_town.py` が読み込み時に外形へ修復する。
- `depth_uom` の文字数に関する警告が大量に出るが、GeoPackageでは値は切り捨てられない。

## 土地利用モデル `luse`（フェーズ0）

| ファイル | 内容 |
| --- | --- |
| `luse/533935_luse_6697_op.gml` | 土地利用モデル（2次メッシュ533935、約400MB、126,744区画）。区ではなく2次メッシュ単位で、港区・目黒区・大田区等も含む |

- 元データは東京都の土地利用現況調査（`surveyYear` は対象範囲内すべて2021年）。建物（2025年度整備）とは時点が異なる。
- 区分は2種類ある。`luse:class` は全国共通の区分（`Common_landUseType`）、`uro:orgLandUse` は都の調査の元の区分（`LandUseDetailAttribute_orgLandUse`）。細かい `orgLandUse` を分類対応に使う。
- 属性に町丁目名・変化フラグ・面積が含まれる。

変換（全区画を一つのGeoPackageへ。約20秒）:

```bash
ogr2ogr -oo EXPOSE_GML_ID=YES -f GPKG data/naisui_poc/02_processed/plateau/luse_2025.gpkg \
  data/naisui_poc/01_raw/plateau/luse/533935_luse_6697_op.gml LandUse -nlt MULTIPOLYGON -dim XY -nln luse
```

カバレッジ確認は `tools/check_landuse_coverage.py`、分類対応表は `data/naisui_poc/02_processed/plateau/landuse_category_mapping.csv`。確認結果（2026-09-25）:

- 中延・二葉＋100mバッファ（1.84km²）を4,784区画が**隙間・重複なく100%覆う**。分類不明（`orgLandUse` 0・90）は無い。
- 建物外形が土地利用の「道路」区画に載る面積は建物面積の0.04%で、両データの位置ずれは小さい。
- 5区分の面積割合（対象範囲全体）: 建物・屋根41.9%、道路・舗装18.2%、駐車場等の不浸透面30.3%、緑地7.7%、水面・その他1.9%。ただし31.9%は分類対応表で確度lowの仮定（主に住宅敷地の建物外部分を舗装とみなしたもの）に依存する。
