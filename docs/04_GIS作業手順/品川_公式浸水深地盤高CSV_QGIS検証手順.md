# 品川区：公式浸水深・地盤高CSV（城南地区河川流域）QGIS検証手順書

更新日: 2026-09-24
用途: 東京都オープンデータの2018年改定「浸水予想区域図」CSVの出所・座標系・属性定義の検証
状態: **読み込みと概略表示まで確認済み。原典の測地系・ゼロ値定義は未確認。評価利用は保留**

## 2026-09-24訂正：比較対象が異なる

このCSVは2018年12月改定・2019年6月一部修正の「城南地区河川流域浸水予想区域図」に対応し、河川と下水道による浸水を扱う。一方、`hazard_shinagawa_normalized.gpkg`の原典は2026年3月公表の「城南地区河川流域 雨水出水浸水想定区域図」で、下水道による浸水を扱う。同じ153mm/h・690mmの降雨条件でも、**同一図面のCSVとPDFではない**。両者の浸水域のずれからCSVのCRSの正誤を判断せず、このCSVで2026年PDF派生レイヤを置き換えたり、直接IoU評価したりしない。

参照: [東京都下水道局の公表一覧](https://www.gesui.metro.tokyo.lg.jp/living/amesh/inundation)、[雨水出水浸水想定区域図Q&A](https://www.kensetsu.metro.tokyo.lg.jp/documents/d/gesui/usuisyussuiQA)。

2026-09-24のQGIS確認では、両CSVをShift_JIS・X=経度・Y=緯度・仮CRS EPSG:4326として読み込んだ。中延・二葉付近では「その１」に浸水深0の点、「その２」に正の浸水深の点がある。元CSVの全体集計では「その１」700,000行中207,954行が正、「その２」708,938行は全行が正。検証用QGISプロジェクトは`data/naisui_poc/02_processed/evaluation/tokyo_jonankaisei_csv_validation.qgz`に別名保存した。

**測地系の追加検証**: EPSG:4326仮定の点群はPDF派生レイヤより南東へ一様にずれて見えた。EPSG:4301（Tokyo Datum）仮定では約290m西・約360m北へ移動し、目視の位置関係が改善した。同一の浸水深0.1m以上の5,991点を比較すると、PDF派生ポリゴン内の点はEPSG:4326仮定で414点、EPSG:4301仮定で1,076点だった。確認用ファイルは`csv3_wgs84_assumption_preview.geojson`と`csv3_tokyo_datum_assumption_preview.geojson`。Tokyo Datum変換は高精度グリッドがないため、利用可能な概算変換（EPSG:15484、公称9m）で作成した。**EPSG:4301は有力な作業上の解釈として採用するが、異なる図面との比較だけで原典の測地系を確定しない**。浸水深0の意味も未確定。原典仕様の確認まで正式な評価への投入は保留する。

CSV2の全708,938点を同じ作業上の解釈でWGS84座標へ変換し、`data/naisui_poc/02_processed/evaluation/jonankaisei_csv2_tokyo_datum_working.gpkg`に保存した。元の緯度・経度とCSVの行番号を属性として保持する。再生成スクリプトは`tools/build_jonankaisei_csv2_tokyo_datum_working.py`。このGeoPackageはQGISでの比較作業用であり、2026年内水ハザードの公式GIS原典とは扱わない。

## 背景

`docs/01_概要・計画/公開データ活用案.md`のレビューをきっかけに、東京都オープンデータカタログから城南地区河川流域（品川区を含む）の
公式「浸水深・地盤高CSV」を取得した。想定降雨は本PoC採用シナリオ`sc_153mmh_24h_690mm_official`
（時間最大153mm・総雨量690mm）と一致しており、現在PDFから手動デジタイズしている
`hazard_shinagawa_normalized.gpkg`（`derived_from_pdf=true`）とは別の図面に対応する（上記訂正参照）。

ただし座標系・浸水深の定義（0が「浸水なし」か「データなし」か）は未検証であり、
**Phase 1〜3を完了しても、2026年PDF派生データの代替として評価・IoU計算に使用してはならない。**

取得済みデータの由来・ライセンス・カバレッジ確認結果は
`data/naisui_poc/01_raw/hazard_map/tokyo_opendata_jonankaisei/README.md`を正とする。

## 使用ファイル

| 用途 | パス | 備考 |
| --- | --- | --- |
| 新規CSV（その１） | `data/naisui_poc/01_raw/hazard_map/tokyo_opendata_jonankaisei/2_jonankaiseicsv1.csv` | Shift_JIS、列: `浸水深,地盤高,緯度,経度` |
| 新規CSV（その２） | `data/naisui_poc/01_raw/hazard_map/tokyo_opendata_jonankaisei/3_jonankaiseicsv2.csv` | 同上。2ファイルで城南地区全体を分割 |
| 品川区境界 | `data/naisui_poc/01_raw/boundaries/r2kb13109.shp` | CRS: JGD2000経緯度（EPSG:4612） |
| 既存PDF派生ポリゴン（比較用） | `data/naisui_poc/02_processed/evaluation/hazard_shinagawa_normalized.gpkg` | CRS: EPSG:6677 |
| 現行採用シナリオのDEM・モデル出力（比較用） | `data/naisui_poc/02_processed/pysheds_surface_routing/sc_153mmh_24h_690mm_official/dem_conditioned.tif` ほか | 標高照合に使用 |
| 既存QGISプロジェクト | `data/naisui_poc/02_processed/evaluation/shinagawa_hazard_pdf_validation.qgz` | 開いて流用可（境界・比較レイヤー入り） |

`shinagawa_hazard_pdf_validation.qgz`を開いてから始めると、境界・比較レイヤーが既に入っている。

## 検証時の原則

- CSVの座標値をいったん別のCRSへ**変換してはいけない**。Phase 2で行うのは、CSVの座標値をどのCRSとして解釈するかの確認である。
- QGISの「レイヤCRSを設定」は座標値を変換せず解釈だけを変更する操作である。候補CRSを試す場合だけ使い、確定後の変換は「名前を付けて保存」等で別レイヤーに出力する。
- `浸水深=0`の意味は、点の分布だけでは確定しない。必ず配布元のデータ説明・図郭割・凡例で裏付ける。
- CSVは公式の**浸水想定データ**である。モデルとの比較は「公式浸水想定との一致度」であり、実測浸水への精度検証・校正ではない。校正は別途、R7.9.11等の浸水実績で行う。

## Phase 1：CSVを読み込む（文字コードに注意）

- [ ] 「レイヤ」→「レイヤの追加」→「デリミテッドテキストレイヤの追加」
- [ ] `2_jonankaiseicsv1.csv`を選択
- [ ] エンコーディングを**Shift_JIS**に変更する（UTF-8のままだと列名・値が文字化けする。列名が`ｦｽ[`のように見えたら未修正のサイン）
- [ ] ジオメトリ定義「ポイント座標」を選択し、Xフィールド=`経度`、Yフィールド=`緯度`
- [ ] レイヤCRSはひとまず**EPSG:4326（WGS84）**として指定する（未確定の仮設定であり、後で検証する）
- [ ] `3_jonankaiseicsv2.csv`も同様に追加する

読み込み直後は点が70万件×2で描画がやや重い。この段階ではズームアウトして全体像だけ確認すれば十分。

## Phase 2：位置整合の検証（最重要）

- [ ] `r2kb13109`（品川区境界）を表示し、CSV点群が品川区の輪郭内に収まるか目視確認する
  - 大きく外れる場合は、経度・緯度フィールドの指定、桁・符号、またはCRSの解釈が誤っている。ここで作業を止める
  - 輪郭内に収まっても、EPSG:4326とJGD2000/JGD2011の差は小さいため、**見た目だけではCRSを確定できない**。配布元メタデータまたは図郭割PDFで根拠を確認する
  - Tokyo Datumの可能性を試す必要がある場合のみ、元CSVを読み直すか、レイヤCRSをEPSG:4301へ設定して同じ比較を行う。既に変換済みのレイヤに対してCRSを上書きしない
- [ ] 中延・二葉付近まで拡大し、`hazard_shinagawa_normalized.gpkg`（PDF派生ポリゴン）と重ねて
  浸水域の分布傾向が大まかに近いか確認する
  - 両者は別の浸水想定図に対応する。分布の不一致をCSVのCRSやPDFの地理参照の誤りと解釈しない

## Phase 3：属性の意味を確認

- [ ] 属性テーブルで`浸水深`列をソートし、`0.00000000000`が全域に散らばっているか、
  特定エリアだけ帯状・格子状に抜けているかを確認する
  - この観察は要確認箇所を見つけるためだけに使う。全域に散らばっていても「浸水なし」とは確定しない
  - 配布元のCSV仕様・図郭割PDF・凡例で定義を確認し、`zero_depth_meaning = no_inundation / no_data / unknown` と記録する。`unknown` のまま後続のIoUへ進まない
- [ ] `地盤高`列を既存DEMと同一地点で数点比較する場合は、地形改変済みの`dem_conditioned.tif`ではなく、比較可能な**元DEM**を使う
  - `dem_conditioned.tif`はピット・窪地・平坦面を補正したモデル入力であり、公式CSVの地盤高の正否を判定する基準にはならない
  - 数値差があれば、座標のずれだけでなく標高基準（T.P.基準、楕円体高等）、解像度、取得時点を疑う。数点比較だけで垂直基準を確定しない
- [ ] 2ファイルをまだ結合せず、対象範囲でそれぞれを別色表示して、隙間・重複・不連続を確認する
  - 結合が必要になった場合は、元ファイル名を保持する属性（例: `source_file`）を付け、経緯度の完全重複と浸水深値の競合を集計してから行う

## Phase 4：2018年版データを独立して分析する場合のみ範囲を絞って保存

この作業は現行の2026年版PDF派生データとの評価パイプラインには接続しない。測地系とゼロ値の定義が確定するまで実施しない。

- [ ] 「ベクタ」→「空間演算ツール」→「クリップ」で、品川区境界（または中延・二葉範囲）を使いCSV点群をクリップする
- [ ] 出力CRSを**EPSG:6677**（`hazard_shinagawa_normalized.gpkg`と同じ、プロジェクトの解析用座標系）に指定して保存する
  - 出力先案: `data/naisui_poc/02_processed/evaluation/tokyo_opendata_jonankaisei_shinagawa.gpkg`（未作成）
  - この出力は「検証済みの点群」であり、まだIoU入力用ポリゴンやモデル比較用ラスタではない。元CSV・元CRS・クリップ条件をメタデータに残す

## Phase 1〜3完了後にやること（この手順書の範囲外）

Phase 1〜3で「座標系OK」「浸水深0の意味が判明」まで確認でき、同じ2018年版の比較対象を確保した場合に限り、以下は担当者・後続LLMが引き取って実装する。
本手順書のPhase 4までは目視検証が目的であり、下記の自動化・pipeline統合は含まない。

1. CSV点群をメッシュポリゴンまたはラスタへ変換し、EPSG:6677で`pysheds_surface_routing/sc_153mmh_24h_690mm_official`のモデル格子と整列する
   - 格子サイズ・セル中心か格子交点か・ゼロ値の扱いを、Phase 3で確定した定義に従って固定する
2. CSV点群を受け付ける専用の変換処理を新設する。既存の`tools/preprocess_hazard_geojson.py`は**Polygon / MultiPolygon専用**であり、CSVを直接渡せない
3. 2026年PDF派生ベクタとのIoU評価や置き換えは行わない。2018年版の同一図面に対応する比較対象、または2026年版の数値・GIS原典が得られた場合に、評価設計を作り直す
4. PDF派生ベクタ（`derived_from_pdf=true`）は比較用の履歴成果物として残す
5. `data/naisui_poc/01_raw/hazard_map/README.md`の「IoU評価の状態」、入力データの版、CRS、ゼロ値定義、評価の限界を更新する
