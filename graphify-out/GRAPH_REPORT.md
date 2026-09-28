# Graph Report - naisui  (2026-09-28)

## Corpus Check
- 21 files · ~57,187 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 719 nodes · 1272 edges · 44 communities (37 shown, 7 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 111 edges (avg confidence: 0.84)
- Token cost: 188,622 input · 0 output

## Community Hubs (Navigation)
- 地域の背景とRAGナレッジ
- Pysheds流下計算とIoU評価ツール
- 土地利用カバレッジ・格子化ツール
- バックエンドのデータ読込と町丁目判定
- モデル実績照合レビュー
- 初期比較と凹地容量感度分析
- フロントエンド開発依存
- PLATEAUデータ取得と正規化
- 町丁目の事実集計ツール
- 下水道台帳の入力スキーマ
- フロントエンドpackage.json
- 公式ハザード比較データ台帳
- 地図パネルと避難所・土のう置場
- チャットUI要件とデザイン基準
- RAG Markdown生成ツール
- 湛水オーバーレイ画像の出力
- チャットパネル
- 安全ガードレール（見直し前）
- Difyチャットフローと接続
- フロントのApp・API
- 町丁目の客観的事実
- 立会川の暗渠と地域の背景
- 引継ぎと採用パイプラインの変遷
- 簡易水収支と参考文献
- 参考文献（AI・水理ハイブリッド）
- 町丁目ボタン選択
- Oxlint設定
- 地図パネルのStorybook
- ハザードレイヤー出力
- フロントエンドREADME
- Storybook設定
- DEMのメディアン平滑化
- 国土数値情報A51（対象外）
- 湛水深オーバーレイ画像
- Viteの既定アイコン
- 型ヒント Any
- 型ヒント GeoDataFrame
- 型ヒント GeoSeries
- 型ヒント ndarray
- 型ヒント Path

## God Nodes (most connected - your core abstractions)
1. `RAG README (Dify knowledge)` - 25 edges
2. `用語とデータの説明 (Terms and data explanation)` - 24 edges
3. `中延・二葉 モデル実績照合レビュー` - 23 edges
4. `立会川の暗渠 / 立会川幹線 (culverted river, trunk sewer)` - 18 edges
5. `雨水がたまりやすい場所（試算）(modelled ponding-prone area)` - 18 edges
6. `中延・二葉 土地利用反映モデル比較（フェーズ1）` - 16 edges
7. `中延三丁目 (town facts)` - 16 edges
8. `中延六丁目 (town facts)` - 16 edges
9. `二葉一丁目 (town facts)` - 16 edges
10. `公式の浸水想定区域 (TMG Jonan rainwater inundation assumption, 153mm/h, 690mm/24h)` - 15 edges

## Surprising Connections (you probably didn't know these)
- `暗渠（立会川）の片側への偏り（距離帯別の標高・たまりやすさ・浸水想定）` --shares_data_with--> `culvert_facts()`  [INFERRED]
  data/naisui_poc/02_processed/town_facts/town_facts.md → tools/build_town_facts.py
- `PDF派生ハザードベクタ hazard_shinagawa_normalized.gpkg` --semantically_similar_to--> `公式の浸水想定区域（城南地区河川流域）`  [AMBIGUOUS] [semantically similar]
  docs/00_現状・引継ぎ/中延二葉_PoC_引継ぎ・タスクリスト.md → data/naisui_poc/02_processed/town_facts/town_facts.md
- `次回タスク: 避難所・土のう置場の記号SVGと凡例追加（2026-09-29）` --conceptually_related_to--> `MapLegend()`  [INFERRED]
  docs/00_現状・引継ぎ/中延二葉_PoC_引継ぎ・タスクリスト.md → frontend/src/components/MapPanel.jsx
- `開始ノードの入力変数（town_name, scenario_label, calibration_status, risk_level, area_ratio_pct, official_status）` --shares_data_with--> `official_status_stub()`  [INFERRED]
  data/naisui_poc/04_llm_knowledge/dify_llm_prompt.md → backend/app/policy.py
- `公式の浸水想定区域 (TMG Jonan rainwater inundation assumption, 153mm/h, 690mm/24h)` --conceptually_related_to--> `scenario sc_153mmh_24h_690mm_official`  [INFERRED]
  RAG/03_用語とデータの説明.md → data/naisui_poc/01_raw/hazard_map/tokyo_opendata_jonankaisei/README.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Pattern A towns (culvert runs through, valley-floor side)** — rag_02___________nakanobu_5chome, rag_02___________nakanobu_6chome, rag_02___________futaba_1chome, rag_02___________futaba_2chome, rag_02___________futaba_3chome, rag_02___________futaba_4chome, rag_01_______pattern_a, rag_01_______tachiaigawa_culvert [EXTRACTED 1.00]
- **三間通り ponding corridor across 中延5/6・二葉3/4** — rag_02___________sangen_dori, rag_02___________nakanobu_5chome, rag_02___________nakanobu_6chome, rag_02___________futaba_3chome, rag_02___________futaba_4chome [EXTRACTED 1.00]
- **town_facts -> RAG markdown -> Dify knowledge pipeline** — rag_readme_build_town_facts, rag_readme_town_facts_json, rag_readme_build_rag_markdown, rag_readme_dify_knowledge [INFERRED 0.85]
- **Difyチャット回答の流れ（決定的判定→Dify知識検索＋LLM→JSON契約検証→フォールバック）** — docs_00_現状_引継ぎ_中延二葉_poc_引継ぎ_タスクリスト_deterministic_policy_before_dify, data_naisui_poc_04_llm_knowledge_dify_llm_prompt_chatflow, data_naisui_poc_04_llm_knowledge_dify_llm_prompt_json_contract, data_naisui_poc_04_llm_knowledge_dify_llm_prompt_template_fallback, backend_app_llm_adapter [EXTRACTED 1.00]
- **町丁目の事実からDifyナレッジへのデータの流れ** — tools_build_town_facts, data_naisui_poc_02_processed_town_facts_town_facts, data_naisui_poc_04_llm_knowledge_readme_town_facts_json, tools_build_rag_markdown, docs_00_現状_引継ぎ_中延二葉_poc_引継ぎ_タスクリスト_rag_folder [INFERRED 0.85]
- **採用モデルの系譜（一律版→土地利用反映版→道路優先版）** — docs_00_現状_引継ぎ_中延二葉_poc_引継ぎ_タスクリスト_pysheds_surface_routing, docs_00_現状_引継ぎ_中延二葉_poc_引継ぎ_タスクリスト_plateau2025_v1_base, docs_00_現状_引継ぎ_中延二葉_poc_引継ぎ_タスクリスト_plateau2025_v3_road050 [EXTRACTED 1.00]
- **簡易湛水モデルの3評価指標** — docs_02_仕様_要件_中延二葉_簡易湛水モデル_校正評価仕様_hit_rate_metric, docs_02_仕様_要件_中延二葉_簡易湛水モデル_校正評価仕様_jaccard_overlap_metric, docs_02_仕様_要件_中延二葉_簡易湛水モデル_校正評価仕様_town_rank_consistency [EXTRACTED 1.00]
- **Pattern A towns along Tachiai culvert (most 2025 flood reports)** — rag_02___________nakanobu_5chome, rag_02___________nakanobu_6chome, rag_02___________futaba_1chome, rag_02___________futaba_2chome, rag_02___________futaba_3chome, rag_02___________futaba_4chome, rag_01_______pattern_a, rag_01_______tachiaigawa_culvert [EXTRACTED 1.00]
- **PLATEAU導入フェーズ1-2のモデル比較（土地利用・建物・道路）** — docs_03_モデル検証_中延二葉_土地利用反映モデル比較_plateau2025_v1_base, docs_03_モデル検証_中延二葉_建物流下遮断モデル比較_building_flow_blocking, docs_03_モデル検証_中延二葉_道路優先流下モデル比較_road_priority_routing, docs_03_モデル検証_中延二葉_建物流下遮断モデル比較_surface_fraction_plateau2025_v1, docs_03_モデル検証_中延二葉_土地利用反映モデル比較_plateau_introduction_plan [EXTRACTED 1.00]
- **PLATEAU導入による段階的モデル改善** — docs_01_概要_計画_plateau導入計画_phase_0b_building_normalization, docs_01_概要_計画_plateau導入計画_phase_1_landuse_runoff, docs_01_概要_計画_plateau導入計画_phase_2_building_road_flow, docs_01_概要_計画_plateau導入計画_phase_3_2d_unsteady_flow, docs_00_現状_引継ぎ_中延二葉_poc_引継ぎ_タスクリスト_plateau2025_v1_base, docs_00_現状_引継ぎ_中延二葉_poc_引継ぎ_タスクリスト_plateau2025_v3_road050 [EXTRACTED 1.00]
- **LLM安全ガードレール構成（決定的ポリシー・入出力契約・優先順位）** — docs_02_仕様_要件_中延二葉_段階3_dify_llm安全ガードレール仕様_deterministic_policy_check, docs_02_仕様_要件_中延二葉_段階3_dify_llm安全ガードレール仕様_llm_input_data_contract, docs_02_仕様_要件_中延二葉_段階3_dify_llm安全ガードレール仕様_information_priority, data_naisui_poc_04_llm_knowledge_safety_guardrails, docs_02_仕様_要件_中延二葉_段階3_dify_llm安全ガードレール仕様_dify_workflow [EXTRACTED 1.00]
- **実績照合による検証体系（正解データ・指標・相関）** — docs_03_モデル検証_中延二葉_モデル実績照合レビュー_inundation_history_31yr, docs_03_モデル検証_中延二葉_モデル実績照合レビュー_r7_0911_inundation_record, docs_03_モデル検証_中延二葉_モデル実績照合レビュー_spearman_tied_rank, docs_03_モデル検証_中延二葉_モデル実績照合レビュー_area_over_threshold_ratio, docs_03_モデル検証_中延二葉_モデル実績照合レビュー_building_count_normalization [EXTRACTED 1.00]
- **Official hazard data comparison / IoU flow** — data_naisui_poc_01_raw_hazard_map_readme_tokyo_jonan_usuisyusui_pdf, data_naisui_poc_01_raw_hazard_map_readme_vectorize_georeferenced_hazard, data_naisui_poc_01_raw_hazard_map_readme_hazard_pdf_colour_classes, data_naisui_poc_01_raw_hazard_map_readme_preprocess_hazard_geojson, data_naisui_poc_01_raw_hazard_map_readme_hazard_shinagawa_normalized, data_naisui_poc_01_raw_hazard_map_readme_evaluate_inundation_iou [INFERRED 0.85]
- **公式PDFハザードの派生ベクタ化とIoU比較の流れ** — docs_04_gis作業手順_品川_ハザードpdf地理参照_色採取記録_jonan_usuisyusui_pdf_2026, docs_04_gis作業手順_品川_ハザードpdf地理参照_色採取記録_shinagawa_georeferenced_tif, docs_04_gis作業手順_品川_ハザードpdf地理参照_色採取記録_legend_rgb_colors, docs_04_gis作業手順_品川_ハザードpdf地理参照_色採取記録_hazard_shinagawa_normalized_gpkg, docs_03_モデル検証_中延二葉_pysheds凹地容量_感度分析_iou_auto_evaluation [INFERRED 0.85]

## Communities (44 total, 7 thin omitted)

### Community 0 - "地域の背景とRAGナレッジ"
Cohesion: 0.08
Nodes (74): tools/export_risk_lookup.py, shinagawa_town_2020.geojson (e-Stat 2020 census town boundaries, 13109), named_roads_2026-09-25.json (OSM named roads via Overpass), Overpass API endpoint overpass.private.coffee, Difyナレッジを高品質・ハイブリッド検索（ウェイト設定）・区切り\n\nに修正, 整備水準 1時間50mm (50mm/h design standard), 地域の背景 (Regional background: Tachiai River valley), 平成11年8月29日集中豪雨 (1999 rainstorm, 2,009 buildings flooded) (+66 more)

### Community 1 - "Pysheds流下計算とIoU評価ツール"
Cohesion: 0.06
Nodes (59): Affine, parse_args(), Namespace, Hydrologically condition GSI DEM tiles and calculate D8 flow products. Outputs…, run(), evaluate(), main(), parse_model() (+51 more)

### Community 2 - "土地利用カバレッジ・格子化ツール"
Cohesion: 0.07
Nodes (58): DatasetReader, load_landuse(), m2(), parse_args(), DataFrame, GeoDataFrame, Namespace, Path (+50 more)

### Community 3 - "バックエンドのデータ読込と町丁目判定"
Cohesion: 0.06
Nodes (44): Any, _load_json(), Any, Path, Loads and caches scenario/town data at process startup. All reads happen once…, In-memory cache built once at import time., メッセージに書かれた町丁目名（TOWN_SLUGSのキー表記）を出現順に重複なく返す。 対象外の丁目（中延七丁目など）は "対象外:<表記>"…, 場所を指す言い方のうち、対象の町丁目名として読み取れないもの（「下新明」等）を返す。 (+36 more)

### Community 4 - "モデル実績照合レビュー"
Cohesion: 0.08
Nodes (44): 中延・二葉 モデル実績照合レビュー, 指標 area_over_threshold_ratio, 建物棟数による実績正規化（フェーズ0B）, DEMアーティファクト（最大深7.32m等）, 二葉二丁目・中延三丁目の順位食い違い, 平成11年8月29日集中豪雨イベント, 品川区 町丁別浸水実績（31年累計）, 指標 max_depth_m（不適切） (+36 more)

### Community 5 - "初期比較と凹地容量感度分析"
Cohesion: 0.07
Nodes (40): 中延・二葉 100mm/h 初期定性比較, D8流向試行（不採用）, Jaccard係数による区域一致評価, Priority-Flood凹地補正と凹地貯留・越流, シナリオ sc_100mm_extreme (100mm/h), 品川区 雨水出水浸水ハザードマップ, 一律等価排水能力 50mm/h, 中延・二葉 Pysheds凹地容量 感度分析 (+32 more)

### Community 6 - "フロントエンド開発依存"
Cohesion: 0.05
Nodes (41): autoprefixer, @chromatic-com/storybook, devDependencies, autoprefixer, @chromatic-com/storybook, oxlint, playwright, postcss (+33 more)

### Community 7 - "PLATEAUデータ取得と正規化"
Cohesion: 0.09
Nodes (30): PLATEAU 3D都市モデル（品川区）README, bldg_2025_lod0.gpkg（建物外形LOD0）, PLATEAU CityGMLカタログAPI, 土地利用分類対応表 landuse_category_mapping.csv, PLATEAU建築物モデル bldg（品川区2025, CityGML）, PLATEAU土地利用モデル luse（533935）, uro:RiverFloodingRiskAttribute（城南地区河川流域, L2）, PLATEAU取得URL一覧 (+22 more)

### Community 8 - "町丁目の事実集計ツール"
Cohesion: 0.14
Nodes (25): GeoDataFrame, GeoSeries, ndarray, Path, Point, culvert_facts(), direction_label(), facility() (+17 more)

### Community 9 - "下水道台帳の入力スキーマ"
Cohesion: 0.10
Nodes (28): 下水道台帳 1D/2D モデル入力スキーマ README, drainage_facilities.csv（ポンプ場・貯留施設）, 1D管網/2D地表 連成モデル, sewer_links.csv（管渠）, sewer_nodes.csv（マンホール・ます・吐口）, surface_node_links.csv（地表セル-ノード接続）, 余剰雨水 = max(0, 降雨強度 − 排水能力 − 浸透能力), 一律等価排水能力 50mm/h (+20 more)

### Community 10 - "フロントエンドpackage.json"
Cohesion: 0.11
Nodes (18): dependencies, maplibre-gl, react, react-dom, name, private, scripts, build (+10 more)

### Community 11 - "公式ハザード比較データ台帳"
Cohesion: 0.14
Nodes (18): 国土数値情報 A51 雨水出水浸水想定区域 (Fussa-only, excluded), 内水ハザード比較データの台帳 (hazard comparison data ledger), tools/evaluate_inundation_iou.py (IoU evaluation, not yet run), hazard_pdf_colour_classes.json (legend RGB classes), hazard_shinagawa_normalized.gpkg (EPSG:6677), IoU評価の状態と取得要件, maximum_ponding_depth_m.tif (sc_100mm_extreme), tools/preprocess_hazard_geojson.py (+10 more)

### Community 12 - "地図パネルと避難所・土のう置場"
Cohesion: 0.15
Nodes (16): 避難所・土のう置場（住所・袋の数）, 次回タスク: 避難所・土のう置場の記号SVGと凡例追加（2026-09-29）, applyLayerVisibility(), BASE_STYLE, boundsOfFeature(), fetchJson(), focusTown(), HAZARD_COLOR_BY_CLASS (+8 more)

### Community 13 - "チャットUI要件とデザイン基準"
Cohesion: 0.15
Nodes (17): calibration_status: pre_calibration_screening, UI デザイン受け入れ基準, モバイルは地図なしチャットのみ, 凡例に「校正前のスクリーニング結果」常時表示, 10町丁目ボタン選択, PC 地図＋チャット2列（チャット列360〜520px）, チャット＋地図UI 要件定義, FastAPI バックエンド（GIS照会・決定的ポリシー・LLMアダプタ） (+9 more)

### Community 14 - "RAG Markdown生成ツール"
Cohesion: 0.25
Nodes (16): chunk_culvert(), chunk_facilities(), chunk_no_culvert(), chunk_official_hazard(), chunk_overview(), chunk_ponding_places(), chunk_records(), chunk_special() (+8 more)

### Community 15 - "湛水オーバーレイ画像の出力"
Cohesion: 0.19
Nodes (12): color_for_depth(), parse_args(), Namespace, ndarray, Export a scenario's max ponding-depth raster to a colorized PNG overlay for…, run(), target_area_geometry_4326(), geocode() (+4 more)

### Community 16 - "チャットパネル"
Cohesion: 0.17
Nodes (6): ChatPanel(), conversation, Empty, ErrorState, Loading, ScenarioChangedNotice

### Community 17 - "安全ガードレール（見直し前）"
Cohesion: 0.17
Nodes (11): 雨水がたまりやすい場所（最大湛水深0.1m以上）, SYSTEMプロンプト（雨水のたまりやすさマップの説明係）, 回答形式（いま確認できること/モデル位置づけ/次の確認/不確実性）, 根拠の優先順位（公式情報>現地観測>モデル結果）, LLM必須ルール safety_guardrails.txt, 中延・二葉 防災対話アシスタント: システム指示, 優先する根拠, 回答形式 (+3 more)

### Community 18 - "Difyチャットフローと接続"
Cohesion: 0.31
Nodes (9): Dify チャットフロー: LLMノードのプロンプト dify_llm_prompt.md, Difyチャットフロー（開始→知識検索 naisui-knowledge→LLM→回答）, Gemini 3.8 Flash（有料枠、Temperature 0.2、Thinking Low）, 出力JSON契約（headline/status/facts/model_context/safe_next_steps/prohibited_claim_check）, prohibited_claim_check（経路指示・避難所安全保証・根拠のない浸水深予測）, Gemini無料枠・Difyナレッジ検索のレート上限（HTTP 400/429）, テンプレート応答へのフォールバック（契約違反・true・タイムアウト）, Dify＋RAGとのチャット接続タスク（2026-09-28完了） (+1 more)

### Community 19 - "フロントのApp・API"
Cohesion: 0.33
Nodes (5): App(), MapPanel, nextId(), useIsPC(), api

### Community 20 - "町丁目の客観的事実"
Cohesion: 0.32
Nodes (8): 町丁目ごとの客観的事実 town_facts.md, 集計から除いた鉄道用地・アンダーパス, 二葉一丁目 ふたばトンネル（鮫洲大山線）, 中延三丁目 池上線の掘割（住宅地のくぼ地ではない）, 通り別のたまりやすさ表（沿道10m）, LLM知識ベース README, LLM知識ベース, town_facts.json（町丁目ごとの数値）

### Community 21 - "立会川の暗渠と地域の背景"
Cohesion: 0.36
Nodes (8): 暗渠（立会川）の片側への偏り（距離帯別の標高・たまりやすさ・浸水想定）, 中延・二葉の地域の背景, 平成11年8月29日 集中豪雨（浸水2,009棟）, 内水はん濫（下水道排水能力不足による浸水）, 令和7年9月11日の大雨（品川区付近約120mm/h）, 立会川の暗渠（立会川幹線・立会道路）, 立会川幹線雨水放流管（内径5.0m×2本）, 立会川の谷（荏原台と目黒台の間）

### Community 22 - "引継ぎと採用パイプラインの変遷"
Cohesion: 0.32
Nodes (8): 公式の浸水想定区域（城南地区河川流域）, 中延・二葉 PoC 引継ぎ・タスクリスト, Case A〜C 相対IoU比較（凹地容量0.5/1.0/1.5m）, PDF派生ハザードベクタ hazard_shinagawa_normalized.gpkg, 雨水出水浸水想定区域図PDFの地理参照（EPSG:6677, RMSE約4.5m）, 採用パイプライン plateau2025_v3_road050（道路優先流下）, R7.9.11浸水実績を主とする校正参照, ハザード区域との重なり率（Jaccard）

### Community 23 - "簡易水収支と参考文献"
Cohesion: 0.25
Nodes (8): 簡易水収支 surface_water_balance v1（参考扱いへ降格）, GISを利用した内水氾濫の危険予測および検証（久保 2018）要約, Q1+Q2>Q3+Q4 内水氾濫水収支, 港北区高田西一丁目 検証（一致率86.6%）, GISを用いた浸水予測モデル（解説）, 4解析ステップ（地形・流出・下水道・地表氾濫）, 流入量>排出量 水収支（浸水発生条件）, 湛水量=max(0,湛水量+(降雨×流出係数−等価排水能力)Δt)

### Community 24 - "参考文献（AI・水理ハイブリッド）"
Cohesion: 0.33
Nodes (7): AIモデルと水理モデルのハイブリッド洪水予測（渡辺 2026）要約, PINNs河道モデル・多地点データ同化, RRIモデル＋DNNハイブリッド, PLATEAU UC25-04 AI環境シミュレーション高速化, iRIC Nays2D Flood, PINO（PhysicsNeMo）AI浸水シミュレータ, PLATEAU VIEW 可視化

### Community 25 - "町丁目ボタン選択"
Cohesion: 0.38
Nodes (5): groupTowns(), Interactive, NoSelection, towns, TownSelector()

### Community 26 - "Oxlint設定"
Cohesion: 0.33
Nodes (5): rules, react/only-export-components, react/rules-of-hooks, $schema, warn

### Community 27 - "地図パネルのStorybook"
Cohesion: 0.33
Nodes (5): plugins, Default, scenarioDetail, oxc, react

### Community 28 - "ハザードレイヤー出力"
Cohesion: 0.47
Nodes (5): parse_args(), Namespace, Export the QGIS-derived hazard vector layer to a web-map-ready GeoJSON.…, rgb_string_to_hex(), run()

### Community 29 - "フロントエンドREADME"
Cohesion: 0.40
Nodes (4): Frontend index.html, Expanding the Oxlint configuration, React Compiler, React + Vite

### Community 31 - "DEMのメディアン平滑化"
Cohesion: 0.50
Nodes (4): parse_args(), Namespace, Create a reversible median-filtered DEM variant for sensitivity analysis., run()

### Community 32 - "国土数値情報A51（対象外）"
Cohesion: 0.50
Nodes (3): A51-25_13_GML の収録範囲, 利用上の前提, 重要

### Community 33 - "湛水深オーバーレイ画像"
Cohesion: 0.67
Nodes (4): Ponding Depth Map Overlay (153mm/h, 24h 690mm, official scenario), Ponding (Inundation) Depth Raster, Official Design Rainfall Scenario: 153 mm/h peak, 690 mm / 24h, Transparent PNG Web Map Overlay (purple depth ramp)

## Ambiguous Edges - Review These
- `named_roads_2026-09-25.json (OSM named roads via Overpass)` → `tools/build_town_facts.py`  [AMBIGUOUS]
  data/naisui_poc/01_raw/osm/README.md · relation: shares_data_with
- `公式の浸水想定区域（城南地区河川流域）` → `PDF派生ハザードベクタ hazard_shinagawa_normalized.gpkg`  [AMBIGUOUS]
  docs/00_現状・引継ぎ/中延二葉_PoC_引継ぎ・タスクリスト.md · relation: semantically_similar_to

## Knowledge Gaps
- **119 isolated node(s):** `IoU評価の状態と取得要件`, `公式PDFからの派生ベクタ化（公式GIS面データ未入手時のみ）`, `現在の比較資料（品川区）`, `評価上の注意`, `BASE_STYLE` (+114 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `named_roads_2026-09-25.json (OSM named roads via Overpass)` and `tools/build_town_facts.py`?**
  _Edge tagged AMBIGUOUS (relation: shares_data_with) - confidence is low._
- **What is the exact relationship between `公式の浸水想定区域（城南地区河川流域）` and `PDF派生ハザードベクタ hazard_shinagawa_normalized.gpkg`?**
  _Edge tagged AMBIGUOUS (relation: semantically_similar_to) - confidence is low._
- **Why does `中延・二葉 PoC 引継ぎ・タスクリスト` connect `引継ぎと採用パイプラインの変遷` to `地域の背景とRAGナレッジ`, `PLATEAUデータ取得と正規化`, `町丁目の事実集計ツール`, `地図パネルと避難所・土のう置場`, `安全ガードレール（見直し前）`, `Difyチャットフローと接続`, `立会川の暗渠と地域の背景`?**
  _High betweenness centrality (0.337) - this node is a cross-community bridge._
- **Why does `RAG README (Dify knowledge)` connect `地域の背景とRAGナレッジ` to `引継ぎと採用パイプラインの変遷`?**
  _High betweenness centrality (0.191) - this node is a cross-community bridge._
- **Why does `Dify＋RAGとのチャット接続タスク（2026-09-28完了）` connect `Difyチャットフローと接続` to `バックエンドのデータ読込と町丁目判定`, `地図パネルと避難所・土のう置場`, `引継ぎと採用パイプラインの変遷`?**
  _High betweenness centrality (0.129) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `中延・二葉 モデル実績照合レビュー` (e.g. with `品川 ハザードPDF地理参照・色採取記録` and `risk_lookup_sc_{scenario}.json（Dify用ナレッジ）`) actually correct?**
  _`中延・二葉 モデル実績照合レビュー` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `IoU評価の状態と取得要件`, `公式PDFからの派生ベクタ化（公式GIS面データ未入手時のみ）`, `現在の比較資料（品川区）` to the rest of the system?**
  _119 weakly-connected nodes found - possible documentation gaps or missing edges._