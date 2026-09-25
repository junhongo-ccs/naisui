# Graph Report - naisui  (2026-09-25)

## Corpus Check
- 151 files · ~55,738 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 675 nodes · 1175 edges · 40 communities (38 shown, 2 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 86 edges (avg confidence: 0.83)
- Token cost: 452,879 input · 0 output

## Community Hubs (Navigation)
- Pysheds流下計算とIoU評価ツール
- 地域の背景とRAGナレッジ
- 土地利用カバレッジ・格子化ツール
- モデル実績照合レビュー
- 初期比較と凹地容量感度分析
- フロントエンド開発依存
- バックエンドのデータ読込と町丁目判定
- 町丁目の事実集計ツール
- フロントエンドpackage.json
- LLMアダプタと安全ガードレール
- 公式ハザード比較データ台帳
- RAG Markdown生成ツール
- 降雨シナリオと水収支の前提
- 町丁目の客観的事実と地域背景
- 地図パネル（凡例・レイヤー切替）
- 下水道台帳の入力スキーマ
- 引継ぎと採用パイプラインの変遷
- チャットパネル
- PLATEAUデータ取得と正規化
- フロントのApp・API
- チャットUI要件とデザイン基準
- 城南CSV座標検証と公開データ
- 湛水オーバーレイ画像の出力
- 参考文献（AI・水理ハイブリッド）
- 町丁目ボタン選択
- Oxlint設定
- 地図パネルのStorybook
- ハザードレイヤー出力
- 土のう置場のジオコーディング
- Storybook設定
- DEMのメディアン平滑化
- 国土数値情報A51（対象外）
- 湛水深オーバーレイ画像
- 防災対話アシスタントのシステム指示
- フロントエンドREADME
- Viteの既定アイコン

## God Nodes (most connected - your core abstractions)
1. `用語とデータの説明 (Terms and data explanation)` - 24 edges
2. `中延・二葉 モデル実績照合レビュー` - 23 edges
3. `中延・二葉 PoC 引継ぎ・タスクリスト` - 22 edges
4. `雨水がたまりやすい場所（試算）(modelled ponding-prone area)` - 18 edges
5. `中延・二葉 土地利用反映モデル比較（フェーズ1）` - 16 edges
6. `ground_cell_areas_m2()` - 15 edges
7. `地域の背景 (Regional background: Tachiai River valley)` - 15 edges
8. `公式の浸水想定区域 (TMG Jonan rainwater inundation assumption, 153mm/h, 690mm/24h)` - 15 edges
9. `チャット＋地図UI 要件定義` - 15 edges
10. `run()` - 14 edges

## Surprising Connections (you probably didn't know these)
- `公式の浸水想定区域 (TMG Jonan rainwater inundation assumption, 153mm/h, 690mm/24h)` --conceptually_related_to--> `scenario sc_153mmh_24h_690mm_official`  [INFERRED]
  RAG/03_用語とデータの説明.md → data/naisui_poc/01_raw/hazard_map/tokyo_opendata_jonankaisei/README.md
- `maximum_ponding_depth_m.tif (sc_100mm_extreme)` --conceptually_related_to--> `雨水がたまりやすい場所（試算）(modelled ponding-prone area)`  [INFERRED]
  data/naisui_poc/01_raw/hazard_map/README.md → RAG/03_用語とデータの説明.md
- `校正の調整順序（排水能力→地表流ルール→局所の1D要素）` --references--> `1D管網/2D地表 連成モデル`  [INFERRED]
  docs/02_仕様・要件/中延二葉_簡易湛水モデル_校正評価仕様.md → data/naisui_poc/02_processed/model_input/README.md
- `情報の優先順位（公式情報→現地観測→校正済→校正前→一般知識）` --semantically_similar_to--> `根拠の優先順位（公式情報>現地観測>モデル結果）`  [INFERRED] [semantically similar]
  docs/02_仕様・要件/中延二葉_段階3_Dify_LLM安全ガードレール仕様.md → data/naisui_poc/04_llm_knowledge/safety_guardrails.md
- `下水道台帳WebGIS SEMIS` --semantically_similar_to--> `東京都下水道台帳`  [INFERRED] [semantically similar]
  docs/01_概要・計画/公開データ活用案.md → data/naisui_poc/README.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Pattern A towns along Tachiai culvert (most 2025 flood reports)** — rag_02___________nakanobu_5chome, rag_02___________nakanobu_6chome, rag_02___________futaba_1chome, rag_02___________futaba_2chome, rag_02___________futaba_3chome, rag_02___________futaba_4chome, rag_01_______pattern_a, rag_01_______tachiaigawa_culvert [EXTRACTED 1.00]
- **RAG knowledge build pipeline** — rag_readme_build_town_facts, rag_readme_town_facts_json, rag_readme_build_rag_markdown, rag_readme_dify_knowledge [EXTRACTED 1.00]
- **Official hazard data comparison / IoU flow** — data_naisui_poc_01_raw_hazard_map_readme_tokyo_jonan_usuisyusui_pdf, data_naisui_poc_01_raw_hazard_map_readme_vectorize_georeferenced_hazard, data_naisui_poc_01_raw_hazard_map_readme_hazard_pdf_colour_classes, data_naisui_poc_01_raw_hazard_map_readme_preprocess_hazard_geojson, data_naisui_poc_01_raw_hazard_map_readme_hazard_shinagawa_normalized, data_naisui_poc_01_raw_hazard_map_readme_evaluate_inundation_iou [INFERRED 0.85]
- **LLM安全ガードレール構成（決定的ポリシー・入出力契約・優先順位）** — docs_02_仕様_要件_中延二葉_段階3_dify_llm安全ガードレール仕様_deterministic_policy_check, docs_02_仕様_要件_中延二葉_段階3_dify_llm安全ガードレール仕様_llm_input_data_contract, docs_02_仕様_要件_中延二葉_段階3_dify_llm安全ガードレール仕様_response_output_contract, docs_02_仕様_要件_中延二葉_段階3_dify_llm安全ガードレール仕様_information_priority, data_naisui_poc_04_llm_knowledge_safety_guardrails, docs_02_仕様_要件_中延二葉_段階3_dify_llm安全ガードレール仕様_dify_workflow [EXTRACTED 1.00]
- **PLATEAU導入による段階的モデル改善** — docs_01_概要_計画_plateau導入計画_phase_0b_building_normalization, docs_01_概要_計画_plateau導入計画_phase_1_landuse_runoff, docs_01_概要_計画_plateau導入計画_phase_2_building_road_flow, docs_01_概要_計画_plateau導入計画_phase_3_2d_unsteady_flow, docs_00_現状_引継ぎ_中延二葉_poc_引継ぎ_タスクリスト_plateau2025_v1_base, docs_00_現状_引継ぎ_中延二葉_poc_引継ぎ_タスクリスト_plateau2025_v3_road050 [EXTRACTED 1.00]
- **簡易湛水モデルの3評価指標** — docs_02_仕様_要件_中延二葉_簡易湛水モデル_校正評価仕様_hit_rate_metric, docs_02_仕様_要件_中延二葉_簡易湛水モデル_校正評価仕様_jaccard_overlap_metric, docs_02_仕様_要件_中延二葉_簡易湛水モデル_校正評価仕様_town_rank_consistency [EXTRACTED 1.00]
- **PLATEAU導入フェーズ1-2のモデル比較（土地利用・建物・道路）** — docs_03_モデル検証_中延二葉_土地利用反映モデル比較_plateau2025_v1_base, docs_03_モデル検証_中延二葉_建物流下遮断モデル比較_building_flow_blocking, docs_03_モデル検証_中延二葉_道路優先流下モデル比較_road_priority_routing, docs_03_モデル検証_中延二葉_建物流下遮断モデル比較_surface_fraction_plateau2025_v1, docs_03_モデル検証_中延二葉_土地利用反映モデル比較_plateau_introduction_plan [EXTRACTED 1.00]
- **実績照合による検証体系（正解データ・指標・相関）** — docs_03_モデル検証_中延二葉_モデル実績照合レビュー_inundation_history_31yr, docs_03_モデル検証_中延二葉_モデル実績照合レビュー_r7_0911_inundation_record, docs_03_モデル検証_中延二葉_モデル実績照合レビュー_spearman_tied_rank, docs_03_モデル検証_中延二葉_モデル実績照合レビュー_area_over_threshold_ratio, docs_03_モデル検証_中延二葉_モデル実績照合レビュー_building_count_normalization [EXTRACTED 1.00]
- **公式PDFハザードの派生ベクタ化とIoU比較の流れ** — docs_04_gis作業手順_品川_ハザードpdf地理参照_色採取記録_jonan_usuisyusui_pdf_2026, docs_04_gis作業手順_品川_ハザードpdf地理参照_色採取記録_shinagawa_georeferenced_tif, docs_04_gis作業手順_品川_ハザードpdf地理参照_色採取記録_legend_rgb_colors, docs_04_gis作業手順_品川_ハザードpdf地理参照_色採取記録_hazard_shinagawa_normalized_gpkg, docs_03_モデル検証_中延二葉_pysheds凹地容量_感度分析_iou_auto_evaluation [INFERRED 0.85]

## Communities (40 total, 2 thin omitted)

### Community 0 - "Pysheds流下計算とIoU評価ツール"
Cohesion: 0.06
Nodes (58): Affine, parse_args(), Namespace, Hydrologically condition GSI DEM tiles and calculate D8 flow products. Outputs…, run(), evaluate(), main(), parse_model() (+50 more)

### Community 1 - "地域の背景とRAGナレッジ"
Cohesion: 0.08
Nodes (64): Backend dependencies: FastAPI, uvicorn, pydantic, tools/export_risk_lookup.py, shinagawa_town_2020.geojson (e-Stat 2020 census town boundaries, 13109), shinagawa_disaster_map_2026-06.pdf (Shinagawa disaster map), named_roads_2026-09-25.json (OSM named roads via Overpass), Overpass API endpoint overpass.private.coffee, 整備水準 1時間50mm (50mm/h design standard), 地域の背景 (Regional background: Tachiai River valley) (+56 more)

### Community 2 - "土地利用カバレッジ・格子化ツール"
Cohesion: 0.07
Nodes (58): DatasetReader, load_landuse(), m2(), parse_args(), DataFrame, GeoDataFrame, Namespace, Path (+50 more)

### Community 3 - "モデル実績照合レビュー"
Cohesion: 0.06
Nodes (52): 中延・二葉 モデル実績照合レビュー, 指標 area_over_threshold_ratio, 建物棟数による実績正規化（フェーズ0B）, DEMアーティファクト（最大深7.32m等）, 二葉二丁目・中延三丁目の順位食い違い, 平成11年8月29日集中豪雨イベント, 品川区 町丁別浸水実績（31年累計）, 指標 max_depth_m（不適切） (+44 more)

### Community 4 - "初期比較と凹地容量感度分析"
Cohesion: 0.06
Nodes (44): 中延・二葉 100mm/h 初期定性比較, D8流向試行（不採用）, Jaccard係数による区域一致評価, Priority-Flood凹地補正と凹地貯留・越流, シナリオ sc_100mm_extreme (100mm/h), 品川区 雨水出水浸水ハザードマップ, 一律等価排水能力 50mm/h, 中延・二葉 Pysheds凹地容量 感度分析 (+36 more)

### Community 5 - "フロントエンド開発依存"
Cohesion: 0.05
Nodes (41): autoprefixer, @chromatic-com/storybook, devDependencies, autoprefixer, @chromatic-com/storybook, oxlint, playwright, postcss (+33 more)

### Community 6 - "バックエンドのデータ読込と町丁目判定"
Cohesion: 0.08
Nodes (32): _load_json(), Any, Path, Loads and caches scenario/town data at process startup. All reads happen once…, In-memory cache built once at import time., メッセージに書かれた町丁目名（TOWN_SLUGSのキー表記）を出現順に重複なく返す。 対象外の丁目（中延七丁目など）は "対象外:<表記>"…, 場所を指す言い方のうち、対象の町丁目名として読み取れないもの（「下新明」等）を返す。, Store (+24 more)

### Community 7 - "町丁目の事実集計ツール"
Cohesion: 0.14
Nodes (24): Point, culvert_facts(), direction_label(), Grid, load_culvert(), load_roads(), load_underpasses(), nearest() (+16 more)

### Community 8 - "フロントエンドpackage.json"
Cohesion: 0.11
Nodes (18): dependencies, maplibre-gl, react, react-dom, name, private, scripts, build (+10 more)

### Community 9 - "LLMアダプタと安全ガードレール"
Cohesion: 0.15
Nodes (15): Stand-in for the Dify LLM call. Dify itself is not wired up yet…, 回答形式（いま確認できること/モデル位置づけ/次の確認/不確実性）, 根拠の優先順位（公式情報>現地観測>モデル結果）, calibration_status: pre_calibration_screening, Dify＋RAGとのチャット接続タスク, RAG/ 文書群（地域の背景・町丁目・用語）, 凡例に「校正前のスクリーニング結果」常時表示, FastAPI バックエンド（GIS照会・決定的ポリシー・LLMアダプタ） (+7 more)

### Community 10 - "公式ハザード比較データ台帳"
Cohesion: 0.15
Nodes (17): 国土数値情報 A51 雨水出水浸水想定区域 (Fussa-only, excluded), 内水ハザード比較データの台帳 (hazard comparison data ledger), tools/evaluate_inundation_iou.py (IoU evaluation, not yet run), hazard_pdf_colour_classes.json (legend RGB classes), hazard_shinagawa_normalized.gpkg (EPSG:6677), IoU評価の状態と取得要件, maximum_ponding_depth_m.tif (sc_100mm_extreme), tools/preprocess_hazard_geojson.py (+9 more)

### Community 11 - "RAG Markdown生成ツール"
Cohesion: 0.25
Nodes (16): chunk_culvert(), chunk_facilities(), chunk_no_culvert(), chunk_official_hazard(), chunk_overview(), chunk_ponding_places(), chunk_records(), chunk_special() (+8 more)

### Community 12 - "降雨シナリオと水収支の前提"
Cohesion: 0.16
Nodes (16): 余剰雨水 = max(0, 降雨強度 − 排水能力 − 浸透能力), 一律等価排水能力 50mm/h, シナリオデータ README, 旧シナリオ sc_50mm_const / sc_80mm_peak / sc_100mm_extreme, 暫定ハイエトグラフ（153mm＋残り23時間均等、計690mm）, sc_153mmh_24h_690mm_official（区の想定最大規模降雨）, area_over_threshold_ratio（町丁目リスク根拠）, n=10 Spearman順位相関の統計的限界 (+8 more)

### Community 13 - "町丁目の客観的事実と地域背景"
Cohesion: 0.17
Nodes (16): 町丁目ごとの客観的事実 town_facts.md, 二葉一丁目 ふたばトンネル（鮫洲大山線）, 中延三丁目 池上線の掘割（住宅地のくぼ地ではない）, 雨水がたまりやすい場所（最大湛水深0.1m以上）, LLM知識ベース README, LLM知識ベース, town_facts.json（町丁目ごとの数値）, 中延・二葉の地域の背景 (+8 more)

### Community 14 - "地図パネル（凡例・レイヤー切替）"
Cohesion: 0.16
Nodes (13): applyLayerVisibility(), BASE_STYLE, boundsOfFeature(), fetchJson(), focusTown(), HAZARD_COLOR_BY_CLASS, HAZARD_FILL_COLOR_EXPR, HAZARD_LEGEND_LABELS (+5 more)

### Community 15 - "下水道台帳の入力スキーマ"
Cohesion: 0.21
Nodes (14): 下水道台帳 1D/2D モデル入力スキーマ README, drainage_facilities.csv（ポンプ場・貯留施設）, 1D管網/2D地表 連成モデル, sewer_links.csv（管渠）, sewer_nodes.csv（マンホール・ます・吐口）, surface_node_links.csv（地表セル-ノード接続）, 中延・二葉 内水氾濫PoC用データ README, 国土地理院5m DEMタイル（z15 PNG） (+6 more)

### Community 16 - "引継ぎと採用パイプラインの変遷"
Cohesion: 0.24
Nodes (13): 中延・二葉 PoC 引継ぎ・タスクリスト, Case A〜C 相対IoU比較（凹地容量0.5/1.0/1.5m）, PDF派生ハザードベクタ hazard_shinagawa_normalized.gpkg, 雨水出水浸水想定区域図PDFの地理参照（EPSG:6677, RMSE約4.5m）, 土地利用反映版 plateau2025_v1_base, 採用パイプライン plateau2025_v3_road050（道路優先流下）, pysheds_surface_routing（D8流向＋窪地容量スクリーニング）, PLATEAU導入計画 (+5 more)

### Community 17 - "チャットパネル"
Cohesion: 0.17
Nodes (6): ChatPanel(), conversation, Empty, ErrorState, Loading, ScenarioChangedNotice

### Community 18 - "PLATEAUデータ取得と正規化"
Cohesion: 0.29
Nodes (10): PLATEAU 3D都市モデル（品川区）README, bldg_2025_lod0.gpkg（建物外形LOD0）, PLATEAU CityGMLカタログAPI, 土地利用分類対応表 landuse_category_mapping.csv, PLATEAU建築物モデル bldg（品川区2025, CityGML）, PLATEAU土地利用モデル luse（533935）, uro:RiverFloodingRiskAttribute（城南地区河川流域, L2）, PLATEAU取得URL一覧 (+2 more)

### Community 19 - "フロントのApp・API"
Cohesion: 0.29
Nodes (6): Frontend index.html, App(), MapPanel, nextId(), useIsPC(), api

### Community 20 - "チャットUI要件とデザイン基準"
Cohesion: 0.25
Nodes (9): UI デザイン受け入れ基準, モバイルは地図なしチャットのみ, 10町丁目ボタン選択, PC 地図＋チャット2列（チャット列360〜520px）, チャット＋地図UI 要件定義, MapLibre GL JS 地図（PCのみ動的import）, モデル推定を主・浸水実績を検証材料とする提示方針, 避難所データ（中延・二葉5件, shelter_status unknown） (+1 more)

### Community 21 - "城南CSV座標検証と公開データ"
Cohesion: 0.32
Nodes (8): 東京都下水道台帳, 2026-09-24 城南地区CSV座標検証・引継ぎ, jonankaisei_csv2_tokyo_datum_working.gpkg（708,938点）, 2018年 城南地区河川流域浸水予想区域図 CSV（浸水深・地盤高）, CSV座標をTokyo Datum（EPSG:4301）と解釈, 品川区・内水氾濫GIS調査メモ（公開データ活用案）, 下水道台帳WebGIS SEMIS, 下水道の排除方式（合流式/分流式/雨水除外）

### Community 22 - "湛水オーバーレイ画像の出力"
Cohesion: 0.36
Nodes (7): color_for_depth(), parse_args(), Namespace, ndarray, Export a scenario's max ponding-depth raster to a colorized PNG overlay for…, run(), target_area_geometry_4326()

### Community 23 - "参考文献（AI・水理ハイブリッド）"
Cohesion: 0.33
Nodes (7): AIモデルと水理モデルのハイブリッド洪水予測（渡辺 2026）要約, PINNs河道モデル・多地点データ同化, RRIモデル＋DNNハイブリッド, PLATEAU UC25-04 AI環境シミュレーション高速化, iRIC Nays2D Flood, PINO（PhysicsNeMo）AI浸水シミュレータ, PLATEAU VIEW 可視化

### Community 24 - "町丁目ボタン選択"
Cohesion: 0.38
Nodes (5): groupTowns(), Interactive, NoSelection, towns, TownSelector()

### Community 25 - "Oxlint設定"
Cohesion: 0.33
Nodes (5): rules, react/only-export-components, react/rules-of-hooks, $schema, warn

### Community 26 - "地図パネルのStorybook"
Cohesion: 0.33
Nodes (5): plugins, Default, scenarioDetail, oxc, react

### Community 27 - "ハザードレイヤー出力"
Cohesion: 0.47
Nodes (5): parse_args(), Namespace, Export the QGIS-derived hazard vector layer to a web-map-ready GeoJSON.…, rgb_string_to_hex(), run()

### Community 28 - "土のう置場のジオコーディング"
Cohesion: 0.47
Nodes (5): geocode(), parse_args(), Namespace, Geocode sandbag storage locations (address-only) to lat/lon and GeoJSON. Uses…, run()

### Community 30 - "DEMのメディアン平滑化"
Cohesion: 0.50
Nodes (4): parse_args(), Namespace, Create a reversible median-filtered DEM variant for sensitivity analysis., run()

### Community 31 - "国土数値情報A51（対象外）"
Cohesion: 0.50
Nodes (3): A51-25_13_GML の収録範囲, 利用上の前提, 重要

### Community 32 - "湛水深オーバーレイ画像"
Cohesion: 0.67
Nodes (4): Ponding Depth Map Overlay (153mm/h, 24h 690mm, official scenario), Ponding (Inundation) Depth Raster, Official Design Rainfall Scenario: 153 mm/h peak, 690 mm / 24h, Transparent PNG Web Map Overlay (purple depth ramp)

### Community 33 - "防災対話アシスタントのシステム指示"
Cohesion: 0.50
Nodes (4): 中延・二葉 防災対話アシスタント: システム指示, 優先する根拠, 回答形式, 絶対に守ること

### Community 34 - "フロントエンドREADME"
Cohesion: 0.50
Nodes (3): Expanding the Oxlint configuration, React Compiler, React + Vite

## Ambiguous Edges - Review These
- `Dify knowledge chunking settings (hybrid search, blank-line separator, 1000 chars)` → `Backend dependencies: FastAPI, uvicorn, pydantic`  [AMBIGUOUS]
  backend/requirements.txt · relation: conceptually_related_to
- `tools/build_town_facts.py` → `named_roads_2026-09-25.json (OSM named roads via Overpass)`  [AMBIGUOUS]
  data/naisui_poc/01_raw/osm/README.md · relation: shares_data_with

## Knowledge Gaps
- **119 isolated node(s):** `IoU評価の状態と取得要件`, `公式PDFからの派生ベクタ化（公式GIS面データ未入手時のみ）`, `現在の比較資料（品川区）`, `評価上の注意`, `利用上の前提` (+114 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Dify knowledge chunking settings (hybrid search, blank-line separator, 1000 chars)` and `Backend dependencies: FastAPI, uvicorn, pydantic`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `tools/build_town_facts.py` and `named_roads_2026-09-25.json (OSM named roads via Overpass)`?**
  _Edge tagged AMBIGUOUS (relation: shares_data_with) - confidence is low._
- **Why does `中延・二葉 PoC 引継ぎ・タスクリスト` connect `引継ぎと採用パイプラインの変遷` to `モデル実績照合レビュー`, `町丁目の事実集計ツール`, `LLMアダプタと安全ガードレール`, `RAG Markdown生成ツール`, `降雨シナリオと水収支の前提`, `町丁目の客観的事実と地域背景`, `チャットUI要件とデザイン基準`, `城南CSV座標検証と公開データ`?**
  _High betweenness centrality (0.193) - this node is a cross-community bridge._
- **Why does `Dify＋RAGとのチャット接続タスク` connect `LLMアダプタと安全ガードレール` to `引継ぎと採用パイプラインの変遷`, `バックエンドのデータ読込と町丁目判定`?**
  _High betweenness centrality (0.072) - this node is a cross-community bridge._
- **Why does `中延・二葉 モデル実績照合レビュー` connect `モデル実績照合レビュー` to `土地利用カバレッジ・格子化ツール`, `初期比較と凹地容量感度分析`?**
  _High betweenness centrality (0.062) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `中延・二葉 モデル実績照合レビュー` (e.g. with `品川 ハザードPDF地理参照・色採取記録` and `risk_lookup_sc_{scenario}.json（Dify用ナレッジ）`) actually correct?**
  _`中延・二葉 モデル実績照合レビュー` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `雨水がたまりやすい場所（試算）(modelled ponding-prone area)` (e.g. with `maximum_ponding_depth_m.tif (sc_100mm_extreme)` and `整備水準 1時間50mm (50mm/h design standard)`) actually correct?**
  _`雨水がたまりやすい場所（試算）(modelled ponding-prone area)` has 3 INFERRED edges - model-reasoned connections that need verification._