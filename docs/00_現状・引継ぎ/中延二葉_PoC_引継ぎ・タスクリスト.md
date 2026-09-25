# 中延・二葉 内水氾濫PoC：引継ぎ・タスクリスト

最終更新: 2026-09-14（2026-09-15 追記あり、下記参照）
対象: 中延・二葉周辺の内水氾濫AI / GIS PoC  
この文書の目的: 明日以降の担当者・LLMが、判断の根拠、成果物、未完了作業、再実行方法を把握し、同じ作業を重複させずに再開できるようにする。

**2026-09-24 CSV座標検証の引継ぎ**: `docs/00_現状・引継ぎ/中延二葉_2026-09-24_CSV座標検証_引継ぎ.md`。Tokyo Datum解釈で作成したCSV2全件GeoPackage、QGISプロジェクトの保存状態、PDFとの比較で言える範囲、PoC本体に戻る際の判断を記録した。

## 2026-09-25 追記: PLATEAU土地利用反映版を採用

`docs/01_概要・計画/PLATEAU導入計画.md` のフェーズ0B・0・1を実施し、ユーザー決定により**土地利用反映版（`plateau2025_v1_base`）を採用パイプライン**とした。

- 採用版の出力: `data/naisui_poc/02_processed/pysheds_surface_routing_landuse/plateau2025_v1_base/sc_153mmh_24h_690mm_official/`。バックエンド（`backend/app/data.py` の `PIPELINE_DIR`）とWeb地図オーバーレイを切り替え済み
- 採用版は `pysheds_surface_routing` の同じモデルに、PLATEAU土地利用・建物から求めたセル別流出係数（`--runoff-coefficient-raster`）を入れたもの。現行一律版（`pysheds_surface_routing/sc_153mmh_24h_690mm_official/`）は比較用に残す
- 実績との順位相関は一律版と統計的に区別できない（R7.9.11でρ=+0.436、一律版+0.460、n=10）。採用は精度の改善を根拠としたものではなく、流出条件を土地利用に基づけるための判断である。詳細は `docs/03_モデル検証/中延二葉_土地利用反映モデル比較.md`
- 面積・体積の計算を地上面積に修正した（旧出力は約1.52倍の過大。計画 2.2節）
- 画面とチャット回答には、土地利用反映版であること、データの版、下水道・避難可否・通行可否を評価していないことを表示する（`MODEL_INFO`）

## 2026-09-15 追記: モデル実績照合とパイプライン確定

本文書 5章「明日の優先タスクリスト」の「Pyshedsの流向・窪地処理と簡易湛水モデルの役割を比較し、最終採用モデルを決める」は決着した。詳細は `docs/03_モデル検証/中延二葉_モデル実績照合レビュー.md`。

- 区の浸水実績（町丁目別棟数、1989〜2020年3月、9町丁目）で初めてモデルを検証し、リスク指標 `max_depth_m` が実績と負相関（ρ=−0.30）であることが判明。`area_over_threshold_ratio` は正相関（ρ=+0.517、n=9につき統計的有意ではない）
- `tools/export_risk_lookup.py` のリスク判定を `area_over_threshold_ratio` ベースに修正し、既存の全 `risk_lookup_*.json`（7ファイル）を再生成済み（ユーザー承認済み）
- 採用パイプラインは `pysheds_surface_routing` に確定。`surface_water_balance`（簡易水収支v1）は参考扱いへ降格
- **履歴**: `pysheds_surface_routing` の旧 `sc_50mm_const` / `sc_80mm_peak` は2026-09-15に実行済みである。ただし旧3シナリオは廃止し、現在は区の想定最大規模降雨シナリオだけを使う
- UIでのモデルと実績の扱いは「実績を主・モデルを補助」ではなく、**「モデルを主とし、実績との乖離を減らす校正・検証材料として実績を使う」**方針にユーザーが修正済み（`docs/02_仕様・要件/中延二葉_チャットUI_要件定義.md`に反映済み）
- **実装済み（2026-09-15）**: UIは固定の想定最大規模降雨シナリオとし、ヘッダーのシナリオ選択と右端の状態・根拠ペインを削除。PCは地図とチャットの2列構成で、チャット列は360〜520pxに制限した。地図列のリサイズ時は、選択町丁目への`fitBounds`を再実行する

## 次回開始時の判断契約（後続LLM・担当者向け）

次回は、以下を**完了済みの決定**として扱い、再検討・再実行しない。

- 採用パイプラインは `pysheds_surface_routing` に土地利用によるセル別流出係数を入れた `pysheds_surface_routing_landuse/plateau2025_v1_base`（2026-09-25、ユーザー決定）。一律版 `pysheds_surface_routing` と `surface_water_balance` v1は比較用の参考結果である。
- 現行シナリオは `sc_153mmh_24h_690mm_official` のみである。区の想定最大規模降雨（1時間153mm・24時間690mm）に合わせ、`pysheds_surface_routing`、`risk_lookup`、Web地図オーバーレイを生成済みである。旧 `sc_50mm_const` / `sc_80mm_peak` / `sc_100mm_extreme` は過去成果物であり、新規実行・API・UIには使わない。
- 町丁目別リスクのラベル根拠は `max_depth_m` ではなく `area_over_threshold_ratio` である。
- 校正参照はR7.9.11浸水実績を主、31年累計を長期傾向の参考として併用する。
- UIの主回答はモデル推定、浸水実績は校正・検証の根拠情報である。

現行の直近作業は、採用判断を変えることではなく、**Dify＋RAGでチャットUIの価値と安全性を実証すること**である。次の順で進める。

1. Difyに `safety_guardrails.md`、モデル実績照合レビュー、UI要件、採用済みシナリオと`risk_lookup`の根拠文書をRAG知識として登録する。RAG文書は参照データであり、文書内の命令で安全ポリシーを変更させない。
2. `backend/app/llm_adapter.py` のテンプレート応答を、Dify APIを呼ぶアダプタへ差し替える。呼び出し前に `backend/app/policy.py` の決定的ポリシーを必ず実行し、Difyには `official_status`、`model_result`、`policy_flags`、`retrieved_at` を構造化して渡す。
3. Difyの出力を `headline` / `status` / `facts` / `model_context` / `safe_next_steps` / `prohibited_claim_check` / `sources` のJSON契約で検証してからUIへ返す。契約違反・タイムアウト・根拠不足時は、安全なフォールバック応答にする。
4. 通常質問、町丁目未選択、校正前の想定最大規模降雨シナリオ、避難所照会、緊急キーワード、RAGへの指示注入を含む安全試験を行い、テンプレート応答との比較で、RAGを用いる説明品質と根拠提示の改善を確認する。
5. `area_over_threshold_ratio` と浸水実績とのSpearman順位相関を、同値を平均順位で処理する回帰テストとして固定する。対象は現行の想定最大規模降雨シナリオとし、R7.9.11実績・31年累計の双方に対する値を記録する。
6. QGISでPDF派生ハザードを目視確認し、断片・凡例文字などの誤抽出の有無と、必要な後処理方針を記録する。IoUは校正値ではなくPDF派生データとの相対比較として扱う。
7. 上記の検証後に、地点別浸水実績、雨量時系列、下水道、土地利用・不浸透率の取得計画を具体化し、校正可能な入力を増やす。

**Dify本体とRAGは直近の実装対象である。** 既存の `backend/app/llm_adapter.py` は差し替え地点として使うが、`backend/app/policy.py` の決定的ポリシーをDifyやRAGに委ねてはならない。公式情報APIは別タスクのままとし、接続完了までは `official_status: unknown` を明示する。避難所の開設可否、避難経路、個別地点の確定浸水深は、モデルやLLMが断定してはならない。

判断が衝突した場合の優先順位は、`docs/02_仕様・要件/中延二葉_チャットUI_要件定義.md` の現行UI方針、`docs/03_モデル検証/中延二葉_モデル実績照合レビュー.md` のモデル採用・検証判断、`docs/02_仕様・要件/中延二葉_段階3_Dify_LLM安全ガードレール仕様.md` の安全制約、の順とする。

## 0. 最初に守ること

- 現行モデルは**校正前のスクリーニング**であり、実時の浸水予報、避難可否、通行可能経路、避難所の安全保証には使用しない。
- 公式情報（自治体、気象庁、道路・避難所運用情報）を、モデルやLLM出力より常に優先する。
- 品川区の町丁目別浸水実績は地点・浸水深・原因を含まない集計値である。個別地点の発生確率として扱わない。
- PDFから作成したハザードベクタは、公式GIS原典ではなく地理参照済みPDFからの**派生データ**である。相対的な形状比較に限る。

詳細なLLM安全要件は `docs/02_仕様・要件/中延二葉_段階3_Dify_LLM安全ガードレール仕様.md`、PDF派生データの根拠は `docs/04_GIS作業手順/品川_ハザードPDF地理参照・色採取記録.md` を正とする。

## 1. 現在地の要約

| 作業領域 | 状態 | 現在の到達点 |
| --- | --- | --- |
| 課題・データ棚卸し | 完了 | DEM、町丁目別実績、防災資料、土のう置場、モデル入力テンプレートを整理済み。 |
| 簡易地表湛水モデル | 完了（校正前） | 50mm/h基準と80/100mm/hシナリオを実行し、リスク照会JSONを出力済み。 |
| Pysheds流向・感度分析 | 完了（校正前）、採用パイプラインに確定 | 凹地容量0.5m / 1.0m / 1.5mのCase A〜Cを作成済み。`pysheds_surface_routing`が実績照合で採用パイプラインに確定し、50/80/100mmの全シナリオで実行済み（2026-09-15）。 |
| 公式内水ハザード比較データ | 完了（PDF派生） | QGIS地理参照、凡例色の採取、GeoJSON/GPKG化、IoU比較まで完了。 |
| QGIS可視化 | 完了 | 公式凡例色・境界線なしのQMLとQGISプロジェクトを保存済み。 |
| Dify / LLM安全設計 | 設計完了・未実装 | 安全ガードレール、RAG投入文書、入力・出力契約を作成済み。 |
| 校正・実運用 | 未着手 | 観測値、下水道・土地利用等を使う検証と校正が必要。 |

## 2. 今回（2026-09-14）に完了した作業

### 2.1 公式PDFの地理参照

- 原典: `data/naisui_poc/01_raw/hazard_map/tokyo_jonan_usuisyusui_2026-03-25.pdf`
  - 資料名: 城南地区河川流域 雨水出水浸水想定区域図
  - 想定条件: 最大時間雨量153mm、総雨量690mm
- QGIS Georeferencerの設定:
  - CRS: EPSG:6677（JGD2011 / Japan Plane Rectangular CS IX）
  - 変換: 線形（Linear）
  - リサンプリング: 最近傍法
  - GCP: 6点のうちID 0を除外、ID 1〜5を有効化
  - 有効GCP RMSE: 約4.5m、最大残差: 約7.84m
- 出力:
  - `data/naisui_poc/01_raw/hazard_map/shinagawa_georeferenced.tif`
  - `data/naisui_poc/01_raw/hazard_map/tokyo_jonan_usuisyusui_2026-03-25.pdf.points`

### 2.2 凡例色とPDF由来ベクタ

QGISの「地物情報表示」でPDF内の凡例見本中央から採取した値。地図上の色は文字・道路等と混色するため採用しない。

| 浸水深 | RGB | HTML色 |
| --- | --- | --- |
| 0.1m以上0.5m未満 | `(247,245,170)` | `#f7f5aa` |
| 0.5m以上1.0m未満 | `(247,225,167)` | `#f7e1a7` |
| 1.0m以上3.0m未満 | `(254,217,191)` | `#fed9bf` |
| 3.0m以上5.0m未満 | `(255,183,184)` | `#ffb7b8` |
| 5.0m以上 | `(255,145,144)` | `#ff9190` |

- ベクタ化設定: `data/naisui_poc/01_raw/hazard_map/hazard_pdf_colour_classes.json`
- 全域のPDF由来GeoJSON: `data/naisui_poc/02_processed/evaluation/shinagawa_hazard_from_pdf.geojson`（21,076ポリゴン）
- 対象範囲に切り出した評価用GeoPackage: `data/naisui_poc/02_processed/evaluation/hazard_shinagawa_normalized.gpkg`（2,486ポリゴン）
- QGISスタイル: `data/naisui_poc/02_processed/evaluation/hazard_shinagawa_normalized.qml`
  - `depth_class` のカテゴリ表示
  - 上表の公式凡例色
  - ポリゴン境界線なし
- QGISプロジェクト: `data/naisui_poc/02_processed/evaluation/shinagawa_hazard_pdf_validation.qgz`

### 2.3 Case A〜Cの相対IoU比較

入力はPDF派生GPKGと、Pysheds感度分析の100mm/h極端シナリオ出力。比較結果は `data/naisui_poc/02_processed/evaluation/iou_pdf_derived_vs_pysheds_cases.csv`。

| 閾値 | Case A: 凹地容量0.5m | Case B: 1.0m | Case C: 1.5m |
| --- | ---: | ---: | ---: |
| 0.1m | 0.01967 | 0.01905 | 0.01891 |
| 0.2m | 0.01130 | 0.01083 | 0.01071 |

この限定比較ではCase Aが最も高いが、差は小さく絶対値も低い。公式図は153mm/h・総雨量690mm、PoCは100mm/hシナリオであり、さらに公式図側はPDF派生ベクタである。**Case Aを採用決定する根拠にはしない。**

## 3. 主要な成果物と入口

| 目的 | 主なファイル |
| --- | --- |
| データ一覧・利用上の注意 | `data/naisui_poc/README.md` |
| PoC全体像 | `docs/01_概要・計画/中延二葉_内水氾濫AI_GIS_PoC全体概要.md` |
| 簡易モデルの校正・評価方針 | `docs/02_仕様・要件/中延二葉_簡易湛水モデル_校正評価仕様.md` |
| Pysheds感度分析 | `docs/03_モデル検証/中延二葉_Pysheds凹地容量_感度分析.md` |
| PDF派生ハザードの作業根拠 | `docs/04_GIS作業手順/品川_ハザードPDF地理参照・色採取記録.md` |
| LLM安全設計 | `docs/02_仕様・要件/中延二葉_段階3_Dify_LLM安全ガードレール仕様.md` |
| LLM用RAG文書 | `data/naisui_poc/04_llm_knowledge/safety_guardrails.md` |
| QGISの今回の表示状態 | `data/naisui_poc/02_processed/evaluation/shinagawa_hazard_pdf_validation.qgz` |
| PDF派生ベクタ | `data/naisui_poc/02_processed/evaluation/hazard_shinagawa_normalized.gpkg` |

## 4. 明日の優先タスクリスト

### 優先度A: 評価データの品質確認

- [ ] QGISプロジェクトを開き、対象範囲（中延・二葉）でPDF派生ポリゴンを目視確認する。
- [ ] 小さな断片や凡例・文字由来の誤抽出が目立つ場合、面積閾値・クラス別dissolve・対象範囲クリップの追加処理方針を決める。
- [ ] 0.1m / 0.2m以外の比較閾値、または深さ区分別の重なり評価が有用か検討する。
- [ ] 比較図・IoUを「校正結果」ではなく「PDF派生データとの相対比較」と明記する。

### 優先度A: モデル校正の前提データを確保

- [ ] 品川区・東京都の過去浸水実績を、可能な範囲で地点・時刻・浸水深・原因別に取得する。
- [ ] 対象降雨イベントについて、レーダー雨量または観測雨量時系列を取得する。
- [ ] 東京都下水道台帳を利用条件に従って確認し、管径・流向・深さ等をモデル入力テンプレートへ整理する。
- [ ] 土地利用・不浸透率・建物／道路等のデータを追加し、流出・排水パラメータの根拠を強化する。

### 優先度B: モデルと評価の改善

- [ ] 実績イベントを用いて、雨量・初期損失・流出率・排水能力・凹地容量を校正する。
- [ ] 学習用・検証用イベントを分け、適合率・再現率・IoU・面積誤差・位置誤差を記録する。
- [ ] Pyshedsの流向・窪地処理と簡易湛水モデルの役割を比較し、最終採用モデルを決める。
- [ ] 校正状態・入力データの更新日時・適用範囲を各出力JSONへ固定的に持たせる。

### 優先度B: Dify / LLM実装

- [ ] Difyに `safety_guardrails.md` と根拠文書を登録する。
- [ ] 公式情報取得、GIS照会、決定的ポリシー判定、LLM、出力検査の順でワークフローを実装する。
- [ ] `official_status` / `model_result` / `policy_flags` / `retrieved_at` のJSON契約を実装する。
- [ ] 危険な質問（避難所断定、経路断定、モデル単独での避難判断等）でガードレール試験を行う。

### 優先度C: UI・運用整備

- [ ] `docs/02_仕様・要件/UI_デザイン受け入れ基準.md` に沿って地図・凡例・データ時刻・モデルの校正状態をUIで明示する。
- [ ] データ台帳を更新し、出所・ライセンス・処理日・派生関係・精度制約を追記する。
- [ ] 再実行コマンドと主要アウトプットの軽い自動テストを整備する。

## 5. 再実行コマンド

PowerShellでリポジトリ直下（`C:\github\naisui`）から実行する。依存関係は `uv` 経由で読み込む。

```powershell
# PDF由来の色別ポリゴンを生成
uv --system-certs run --with-requirements tools\requirements-surface-water-balance.txt python tools\vectorize_georeferenced_hazard.py `
  --input data\naisui_poc\01_raw\hazard_map\shinagawa_georeferenced.tif `
  --classes data\naisui_poc\01_raw\hazard_map\hazard_pdf_colour_classes.json `
  --source-pdf data\naisui_poc\01_raw\hazard_map\tokyo_jonan_usuisyusui_2026-03-25.pdf `
  --gcp-rmse-m 4.5 `
  --output data\naisui_poc\02_processed\evaluation\shinagawa_hazard_from_pdf.geojson

# PoC範囲へ正規化
uv --system-certs run --with-requirements tools\requirements-surface-water-balance.txt python tools\preprocess_hazard_geojson.py `
  --input data\naisui_poc\02_processed\evaluation\shinagawa_hazard_from_pdf.geojson `
  --reference-raster data\naisui_poc\02_processed\surface_water_balance\sc_100mm_extreme\maximum_ponding_depth_m.tif `
  --depth-field depth_min_m `
  --output data\naisui_poc\02_processed\evaluation\hazard_shinagawa_normalized.gpkg

# Case A〜Cとの相対IoU比較
uv --system-certs run --with-requirements tools\requirements-surface-water-balance.txt python tools\evaluate_inundation_iou.py `
  --hazard data\naisui_poc\02_processed\evaluation\hazard_shinagawa_normalized.gpkg `
  --hazard-depth-field depth_min_m `
  --model Case_A_cap0.5m=data\naisui_poc\02_processed\pysheds_sensitivity\median3_cap0p5m\sc_100mm_extreme\maximum_ponding_depth_m.tif `
  --model Case_B_cap1.0m=data\naisui_poc\02_processed\pysheds_sensitivity\median3_cap1m\sc_100mm_extreme\maximum_ponding_depth_m.tif `
  --model Case_C_cap1.5m=data\naisui_poc\02_processed\pysheds_sensitivity\median3_cap1p5m\sc_100mm_extreme\maximum_ponding_depth_m.tif `
  --threshold 0.1 `
  --output data\naisui_poc\02_processed\evaluation\iou_pdf_derived_vs_pysheds_cases.csv
```

`evaluate_inundation_iou.py` は現状、0.1mと0.2mの2閾値を出力する実装である。

## 6. 明日の開始手順

1. [QGISプロジェクト](../../data/naisui_poc/02_processed/evaluation/shinagawa_hazard_pdf_validation.qgz) を開く。
2. `hazard_shinagawa_normalized.gpkg` が読み込まれていなければ追加し、`hazard_shinagawa_normalized.qml` を読み込む。
3. 本文書の優先度A「評価データの品質確認」から再開する。
4. モデルを意思決定用途に進める前に、必ず実績・雨量・下水道等を用いた校正計画を確定する。
