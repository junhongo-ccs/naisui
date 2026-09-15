# Graph Report - naisui  (2026-09-15)

## Corpus Check
- 100 files · ~24,151 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 458 nodes · 533 edges · 40 communities (38 shown, 2 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 12 edges (avg confidence: 0.68)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- 簡易地表湛水モデル
- export_risk_lookup.py
- run_surface_water_balance.py
- App.jsx
- devDependencies
- main.py
- 中延・二葉 内水氾濫PoC：モデル–浸水実績 照合レビュー
- package.json
- 中延・二葉 内水氾濫PoC：引継ぎ・タスクリスト
- 中延・二葉PoC 段階3: Dify / LLM安全ガードレール仕様
- 中延・二葉 内水氾濫AI/GIS PoC — チャット＋地図UI 要件定義
- 「内水浸水想定区域図作成マニュアル（案）」要約
- 「AIモデルと水理モデルのハイブリッド活用による洪水予測技術の高度化に関する研究」要約
- 「発生～終息に至る内水氾濫観測結果にもとづくGISシミュレーションとエリア排水能力評価」要約
- _load_json
- 「GISを利用した内水氾濫の危険予測および検証」要約
- 中延・二葉 100mm/hシナリオ — 初期定性比較
- AIを活用した環境シミュレーションの高速化技術の開発（PLATEAUユースケース）
- .oxlintrc.json
- export_web_ponding_overlay.py
- 内水氾濫AI/GIS PoC UI — デザイン受け入れ基準
- 中延・二葉 簡易湛水モデル — 校正・評価仕様
- 品川区内水ハザードPDF：地理参照・色採取記録
- evaluate_inundation_iou.py
- vectorize_georeferenced_hazard.py
- 内水ハザード比較データの台帳
- 中延・二葉 Pysheds凹地容量 — 感度分析
- export_web_hazard_layer.py
- geocode_sandbag_locations.py
- preprocess_hazard_geojson.py
- main.js
- extract_depression_candidates.py
- smooth_dem_median.py
- A51-25_13_GML の収録範囲
- React + Vite
- 04_llm_knowledge/README.md

## God Nodes (most connected - your core abstractions)
1. `「内水浸水想定区域図作成マニュアル（案）」要約` - 12 edges
2. `「発生～終息に至る内水氾濫観測結果にもとづくGISシミュレーションとエリア排水能力評価」要約` - 11 edges
3. `chat()` - 10 edges
4. `run()` - 10 edges
5. `load_dem_tiles()` - 10 edges
6. `中延・二葉 内水氾濫PoC：引継ぎ・タスクリスト` - 10 edges
7. `中延・二葉 内水氾濫AI/GIS PoC — チャット＋地図UI 要件定義` - 10 edges
8. `中延・二葉PoC 段階3: Dify / LLM安全ガードレール仕様` - 10 edges
9. `react` - 9 edges
10. `write_geotiff()` - 9 edges

## Surprising Connections (you probably didn't know these)
- `国土地理院5m DEM` --semantically_similar_to--> `国土地理院5m DEMタイル`  [INFERRED] [semantically similar]
  docs/C52.pdf → data/naisui_poc/README.md
- `50mm/h 地表水収支モデル` --semantically_similar_to--> `簡易地表湛水モデル`  [INFERRED] [semantically similar]
  docs/中延二葉_内水氾濫AI_GIS_PoC全体概要.md → tools/README_surface_water_balance.md
- `内水浸水想定区域図作成マニュアル` --conceptually_related_to--> `中延・二葉 内水氾濫AI GIS PoC`  [INFERRED]
  docs/naisui_manual.pdf → docs/中延二葉_内水氾濫AI_GIS_PoC全体概要.md
- `降雨シナリオ` --shares_data_with--> `簡易地表湛水モデル`  [EXTRACTED]
  data/naisui_poc/03_scenarios/README.md → tools/README_surface_water_balance.md
- `一律排水能力50mm毎時` --implements--> `簡易地表湛水モデル`  [EXTRACTED]
  data/naisui_poc/02_processed/model_input/README.md → tools/README_surface_water_balance.md

## Import Cycles
- None detected.

## Communities (40 total, 2 thin omitted)

### Community 0 - "簡易地表湛水モデル"
Cohesion: 0.13
Nodes (15): 令和2年国勢調査町丁目境界データ, 一律排水能力50mm毎時, 降雨シナリオ, 防災LLM安全ガードレール, 国土地理院5m DEMタイル, 中延・二葉 内水氾濫PoC, 根拠カードとデータ品質ダッシュボード, 町丁目ポリゴンによるゾーン集計 (+7 more)

### Community 1 - "export_risk_lookup.py"
Cohesion: 0.33
Nodes (9): parse_args(), parse_elapsed_minutes(), Namespace, ndarray, Path, raster_values(), Aggregate a scenario's GeoTIFFs by town polygon and write risk_lookup JSON.…, risk_level() (+1 more)

### Community 2 - "run_surface_water_balance.py"
Cohesion: 0.10
Nodes (38): parse_args(), Namespace, Hydrologically condition GSI DEM tiles and calculate D8 flow products. Outputs…, run(), main(), parse_args(), Namespace, Run 0.5m, 1.0m, and 1.5m depression-cap sensitivity cases on a smoothed DEM. (+30 more)

### Community 3 - "App.jsx"
Cohesion: 0.06
Nodes (35): App(), MapPanel, nextId(), useIsPC(), ChatPanel(), conversation, Empty, ErrorState (+27 more)

### Community 4 - "devDependencies"
Cohesion: 0.05
Nodes (41): autoprefixer, @chromatic-com/storybook, devDependencies, autoprefixer, @chromatic-com/storybook, oxlint, playwright, postcss (+33 more)

### Community 5 - "main.py"
Cohesion: 0.13
Nodes (21): generate(), Any, Stand-in for the Dify LLM call. Dify itself is not wired up yet…, chat(), get_scenario(), get_scenarios(), get_towns(), health() (+13 more)

### Community 6 - "中延・二葉 内水氾濫PoC：モデル–浸水実績 照合レビュー"
Cohesion: 0.11
Nodes (18): 0. このレビューの位置づけ, 1. 正解データ：品川区 町丁別浸水実績, 2.1 重要な訂正: 正解データは実質「1999年の1イベント」（2026-09-15追記）, 2.2 R7.9.11データによる追加検証と正解データの方針確定（2026-09-15追記）, 2. 照合結果：モデル順位 vs 実績順位（Spearman順位相関）, 3. 付随して検出したデータ品質の問題, 4. 既存IoU評価との関係, 5. 推奨する設計判断 (+10 more)

### Community 7 - "package.json"
Cohesion: 0.11
Nodes (18): dependencies, maplibre-gl, react, react-dom, name, private, scripts, build (+10 more)

### Community 8 - "中延・二葉 内水氾濫PoC：引継ぎ・タスクリスト"
Cohesion: 0.11
Nodes (18): 0. 最初に守ること, 1. 現在地の要約, 2026-09-15 追記: モデル実績照合とパイプライン確定, 2.1 公式PDFの地理参照, 2.2 凡例色とPDF由来ベクタ, 2.3 Case A〜Cの相対IoU比較, 2. 今回（2026-09-14）に完了した作業, 3. 主要な成果物と入口 (+10 more)

### Community 9 - "中延・二葉PoC 段階3: Dify / LLM安全ガードレール仕様"
Cohesion: 0.12
Nodes (15): 中延・二葉 防災対話アシスタント: システム指示, 優先する根拠, 回答形式, 絶対に守ること, 1. 目的と適用範囲, 2. 情報の優先順位, 3. Difyワークフロー, 4. LLMへ渡すデータ契約 (+7 more)

### Community 10 - "中延・二葉 内水氾濫AI/GIS PoC — チャット＋地図UI 要件定義"
Cohesion: 0.14
Nodes (13): 1. 作るもの / 作らないもの, 2. 主ユーザーと利用状況, 3. 画面構成（テキストワイヤー）, 4. 状態一覧, 5. 技術前提, 6. 制約（安全）, 7. 検収チェックリスト, 8. 未確定の前提（推測で埋めた箇所） (+5 more)

### Community 11 - "「内水浸水想定区域図作成マニュアル（案）」要約"
Cohesion: 0.15
Nodes (12): このマニュアルの目的, 事前に集める主なデータ, 作成の流れ, 内水浸水想定の3手法, 「内水浸水想定区域図作成マニュアル（案）」要約, 参照, 図面に示す主な情報, 実務上の要点 (+4 more)

### Community 12 - "「AIモデルと水理モデルのハイブリッド活用による洪水予測技術の高度化に関する研究」要約"
Cohesion: 0.17
Nodes (11): 1. RRIモデルと深層学習の統合, 2. リアルタイム運用への適用, 3. PINNsによる河道モデルとデータ同化, 「AIモデルと水理モデルのハイブリッド活用による洪水予測技術の高度化に関する研究」要約, 参照, 文書情報, 研究の中核, 章構成 (+3 more)

### Community 13 - "「発生～終息に至る内水氾濫観測結果にもとづくGISシミュレーションとエリア排水能力評価」要約"
Cohesion: 0.17
Nodes (11): GISによる解析手法, 主な結果, 内水氾濫の捉え方, 参照, 実務への示唆, 文書情報, 「発生～終息に至る内水氾濫観測結果にもとづくGISシミュレーションとエリア排水能力評価」要約, 背景と目的 (+3 more)

### Community 14 - "_load_json"
Cohesion: 0.29
Nodes (6): _load_json(), Any, Path, Loads and caches scenario/town data at process startup. All reads happen once…, In-memory cache built once at import time., Store

### Community 15 - "「GISを利用した内水氾濫の危険予測および検証」要約"
Cohesion: 0.22
Nodes (8): 「GISを利用した内水氾濫の危険予測および検証」要約, 参考, 手法, 文書情報, 結果と検証, 背景と目的, 要旨, 課題と示唆

### Community 16 - "中延・二葉 100mm/hシナリオ — 初期定性比較"
Cohesion: 0.22
Nodes (8): D8流向の試行結果（採用前）, 中延・二葉 100mm/hシナリオ — 初期定性比較, 原因の仮説, 安全上の扱い, 対象, 校正の順序, 次の定量評価に必要なもの, 確認結果

### Community 17 - "AIを活用した環境シミュレーションの高速化技術の開発（PLATEAUユースケース）"
Cohesion: 0.25
Nodes (7): AIを活用した環境シミュレーションの高速化技術の開発（PLATEAUユースケース）, システムの全体像と構成要素, プロジェクトの概要と背景, ユーザー評価と今後の課題・展望, 実現したい価値と目指す世界, 実証実験の検証方法と結果, 技術的アプローチと実装方法

### Community 18 - ".oxlintrc.json"
Cohesion: 0.25
Nodes (7): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema, oxc, warn

### Community 19 - "export_web_ponding_overlay.py"
Cohesion: 0.36
Nodes (7): color_for_depth(), parse_args(), Namespace, ndarray, Export a scenario's max ponding-depth raster to a colorized PNG overlay for…, run(), target_area_geometry_4326()

### Community 20 - "内水氾濫AI/GIS PoC UI — デザイン受け入れ基準"
Cohesion: 0.29
Nodes (6): 内水氾濫AI/GIS PoC UI — デザイン受け入れ基準, 対象, 必須要件, 推奨画面構成, 検収チェック, 非機能・安全要件

### Community 21 - "中延・二葉 簡易湛水モデル — 校正・評価仕様"
Cohesion: 0.29
Nodes (6): 中延・二葉 簡易湛水モデル — 校正・評価仕様, 位置づけ, 入力ファイル, 校正手順, 解釈上の注意, 評価指標

### Community 22 - "品川区内水ハザードPDF：地理参照・色採取記録"
Cohesion: 0.29
Nodes (6): 原典, 品川区内水ハザードPDF：地理参照・色採取記録, 地理参照, 後続処理の注意, 採取済みの凡例カラー, 生成・相対比較の実行結果

### Community 23 - "evaluate_inundation_iou.py"
Cohesion: 0.48
Nodes (6): evaluate(), main(), parse_model(), GeoDataFrame, Path, Evaluate model inundation masks against an official hazard polygon by IoU.

### Community 24 - "vectorize_georeferenced_hazard.py"
Cohesion: 0.48
Nodes (6): load_classes(), main(), GeoDataFrame, Path, Vectorize colour-coded inland-inundation classes from a georeferenced raster.…, write_vector()

### Community 25 - "内水ハザード比較データの台帳"
Cohesion: 0.33
Nodes (5): IoU評価の状態と取得要件, 公式PDFからの派生ベクタ化（公式GIS面データ未入手時のみ）, 内水ハザード比較データの台帳, 現在の比較資料（品川区）, 評価上の注意

### Community 26 - "中延・二葉 Pysheds凹地容量 — 感度分析"
Cohesion: 0.33
Nodes (5): IoUの自動評価, ケース定義と実行結果, 中延・二葉 Pysheds凹地容量 — 感度分析, 共通条件, 比較方法

### Community 27 - "export_web_hazard_layer.py"
Cohesion: 0.47
Nodes (5): parse_args(), Namespace, Export the QGIS-derived hazard vector layer to a web-map-ready GeoJSON.…, rgb_string_to_hex(), run()

### Community 28 - "geocode_sandbag_locations.py"
Cohesion: 0.47
Nodes (5): geocode(), parse_args(), Namespace, Geocode sandbag storage locations (address-only) to lat/lon and GeoJSON. Uses…, run()

### Community 29 - "preprocess_hazard_geojson.py"
Cohesion: 0.47
Nodes (5): find_depth_field(), main(), normalized_depth_min_m(), Validate and normalize an official inland-inundation polygon dataset. This tool…, Return the lower bound of a Japanese depth-class label, where possible.

### Community 31 - "extract_depression_candidates.py"
Cohesion: 0.50
Nodes (4): parse_args(), Namespace, Extract DEM depression candidates as ranked CSV and GeoJSON for review., run()

### Community 32 - "smooth_dem_median.py"
Cohesion: 0.50
Nodes (4): parse_args(), Namespace, Create a reversible median-filtered DEM variant for sensitivity analysis., run()

### Community 33 - "A51-25_13_GML の収録範囲"
Cohesion: 0.50
Nodes (3): A51-25_13_GML の収録範囲, 利用上の前提, 重要

### Community 34 - "React + Vite"
Cohesion: 0.50
Nodes (3): Expanding the Oxlint configuration, React Compiler, React + Vite

## Knowledge Gaps
- **195 isolated node(s):** `$schema`, `oxc`, `react/rules-of-hooks`, `warn`, `config` (+190 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `devDependencies` connect `devDependencies` to `package.json`?**
  _High betweenness centrality (0.015) - this node is a cross-community bridge._
- **Why does `react` connect `App.jsx` to `.oxlintrc.json`?**
  _High betweenness centrality (0.008) - this node is a cross-community bridge._
- **Why does `plugins` connect `.oxlintrc.json` to `App.jsx`?**
  _High betweenness centrality (0.004) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `chat()` (e.g. with `ChatRequest` and `ChatResponse`) actually correct?**
  _`chat()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `$schema`, `oxc`, `react/rules-of-hooks` to the rest of the system?**
  _195 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `簡易地表湛水モデル` be split into smaller, more focused modules?**
  _Cohesion score 0.13333333333333333 - nodes in this community are weakly interconnected._
- **Should `run_surface_water_balance.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09639953542392567 - nodes in this community are weakly interconnected._