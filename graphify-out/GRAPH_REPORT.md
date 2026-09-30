# Graph Report - naisui  (2026-09-29)

## Corpus Check
- 17 files · ~58,471 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 767 nodes · 1313 edges · 55 communities (44 shown, 11 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 113 edges (avg confidence: 0.84)
- Token cost: 161,647 input · 0 output

## Community Hubs (Navigation)
- 町丁目リスク集計と地域背景
- 流向・浸水IoU評価
- 土地利用・建物データ処理
- PLATEAU 3D都市モデル
- モデル実績照合レビュー
- 100mm/h定性比較と凹地補正
- フロント開発依存パッケージ
- 町丁目ファクト生成
- 地図パネル（MapPanel）
- チャットAPIと安全ポリシー
- フロント実行時依存
- 公式ハザード比較データ
- RAGマークダウン生成
- 町丁目の客観的事実
- バックエンドデータ読込
- チャットパネルUI
- Dify知識ベースとLLM
- PoC引継ぎと採用パイプライン
- LLMアダプタとJSON契約
- Difyプロンプトと出力契約
- アプリ全体構成（App）
- FastAPIエンドポイント
- LLM安全ガードレール仕様
- 地図UI・配色・記号
- Vercel/Renderデプロイ
- 範囲外・判断質問の検出
- 水収支による浸水予測文献
- oxlint設定
- 湛水オーバーレイ書き出し
- AI・水理ハイブリッド洪水予測
- 町丁目選択UI
- UI受け入れ基準
- ハザード層書き出し
- 土のう置場ジオコーディング
- 回答ルールと自由入力の扱い
- フロントREADME・雛形
- Storybook設定
- DEM平滑化
- チャットAPIスキーマ
- A51 GMLデータ説明
- 湛水深オーバーレイ概念
- 地図アイコンと施設色
- MapPanelストーリー
- Vite雛形の画像
- Any型(1)
- Any型(2)
- 根拠表示の削除
- アクセス制御なし
- GeoDataFrame型
- GeoSeries型
- ndarray型
- Path型

## God Nodes (most connected - your core abstractions)
1. `用語とデータの説明 (Terms and data explanation)` - 24 edges
2. `RAG README (Dify knowledge)` - 24 edges
3. `中延・二葉 モデル実績照合レビュー` - 23 edges
4. `立会川の暗渠 / 立会川幹線 (culverted river, trunk sewer)` - 18 edges
5. `雨水がたまりやすい場所（試算）(modelled ponding-prone area)` - 18 edges
6. `中延・二葉 土地利用反映モデル比較（フェーズ1）` - 16 edges
7. `二葉一丁目 (town facts)` - 16 edges
8. `中延三丁目 (town facts)` - 16 edges
9. `中延六丁目 (town facts)` - 16 edges
10. `公式の浸水想定区域 (TMG Jonan rainwater inundation assumption, 153mm/h, 690mm/24h)` - 15 edges

## Surprising Connections (you probably didn't know these)
- `暗渠（立会川）の片側への偏り（距離帯別の標高・たまりやすさ・浸水想定）` --shares_data_with--> `culvert_facts()`  [INFERRED]
  data/naisui_poc/02_processed/town_facts/town_facts.md → tools/build_town_facts.py
- `最初に守ること（校正前スクリーニング・公式情報優先）` --semantically_similar_to--> `回答のルール（出所を分ける・実績を予測根拠にしない・unknownは未確認）`  [INFERRED] [semantically similar]
  docs/00_現状・引継ぎ/中延二葉_PoC_引継ぎ・タスクリスト.md → data/naisui_poc/04_llm_knowledge/dify_llm_prompt.md
- `公式の浸水想定区域 (TMG Jonan rainwater inundation assumption, 153mm/h, 690mm/24h)` --conceptually_related_to--> `scenario sc_153mmh_24h_690mm_official`  [INFERRED]
  RAG/03_用語とデータの説明.md → data/naisui_poc/01_raw/hazard_map/tokyo_opendata_jonankaisei/README.md
- `maximum_ponding_depth_m.tif (sc_100mm_extreme)` --conceptually_related_to--> `雨水がたまりやすい場所（試算）(modelled ponding-prone area)`  [INFERRED]
  data/naisui_poc/01_raw/hazard_map/README.md → RAG/03_用語とデータの説明.md
- `品川区 町丁別浸水実績一覧 / 防災地図 (flood records)` --references--> `shinagawa_disaster_map_2026-06.pdf (Shinagawa disaster map)`  [INFERRED]
  RAG/03_用語とデータの説明.md → data/naisui_poc/01_raw/hazard_map/README.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **チャット要求の安全パイプライン（決定的ポリシー→Dify→契約検証→フォールバック）** — backend_app_policy, backend_app_llm_adapter, data_naisui_poc_04_llm_knowledge_dify_llm_prompt_dify_chatflow, data_naisui_poc_04_llm_knowledge_dify_llm_prompt_json_output_contract, data_naisui_poc_04_llm_knowledge_dify_llm_prompt_template_fallback [EXTRACTED 1.00]
- **Vercel（画面）＋Render（バックエンド）のデプロイ構成** — docs_00_poc_vercel_frontend_deploy, docs_00_poc_render_backend_deploy, render_naisui_api, render_build_filter, render_env_vars [EXTRACTED 1.00]
- **採用モデルの系譜とリスク指標** — docs_00_poc_pysheds_surface_routing, docs_00_poc_landuse_pipeline_v1_base, docs_00_poc_adopted_pipeline_road050, docs_00_poc_area_over_threshold_ratio, docs_00_poc_scenario_153mmh_690mm [INFERRED 0.85]
- **簡易湛水モデルの3評価指標** — docs_02_仕様_要件_中延二葉_簡易湛水モデル_校正評価仕様_hit_rate_metric, docs_02_仕様_要件_中延二葉_簡易湛水モデル_校正評価仕様_jaccard_overlap_metric, docs_02_仕様_要件_中延二葉_簡易湛水モデル_校正評価仕様_town_rank_consistency [EXTRACTED 1.00]
- **Pattern A towns along Tachiai culvert (most 2025 flood reports)** — rag_02___________nakanobu_5chome, rag_02___________nakanobu_6chome, rag_02___________futaba_1chome, rag_02___________futaba_2chome, rag_02___________futaba_3chome, rag_02___________futaba_4chome, rag_01_______pattern_a, rag_01_______tachiaigawa_culvert [EXTRACTED 1.00]
- **PLATEAU導入フェーズ1-2のモデル比較（土地利用・建物・道路）** — docs_03_モデル検証_中延二葉_土地利用反映モデル比較_plateau2025_v1_base, docs_03_モデル検証_中延二葉_建物流下遮断モデル比較_building_flow_blocking, docs_03_モデル検証_中延二葉_道路優先流下モデル比較_road_priority_routing, docs_03_モデル検証_中延二葉_建物流下遮断モデル比較_surface_fraction_plateau2025_v1, docs_03_モデル検証_中延二葉_土地利用反映モデル比較_plateau_introduction_plan [EXTRACTED 1.00]
- **PLATEAU導入による段階的モデル改善** — docs_01_概要_計画_plateau導入計画_phase_0b_building_normalization, docs_01_概要_計画_plateau導入計画_phase_1_landuse_runoff, docs_01_概要_計画_plateau導入計画_phase_2_building_road_flow, docs_01_概要_計画_plateau導入計画_phase_3_2d_unsteady_flow [EXTRACTED 1.00]
- **Pattern A towns (culvert runs through, valley-floor side)** — rag_02___________nakanobu_5chome, rag_02___________nakanobu_6chome, rag_02___________futaba_1chome, rag_02___________futaba_2chome, rag_02___________futaba_3chome, rag_02___________futaba_4chome, rag_01_______pattern_a, rag_01_______tachiaigawa_culvert [EXTRACTED 1.00]
- **三間通り ponding corridor across 中延5/6・二葉3/4** — rag_02___________sangen_dori, rag_02___________nakanobu_5chome, rag_02___________nakanobu_6chome, rag_02___________futaba_3chome, rag_02___________futaba_4chome [EXTRACTED 1.00]
- **LLM安全ガードレール構成（決定的ポリシー・入出力契約・優先順位）** — docs_02_仕様_要件_中延二葉_段階3_dify_llm安全ガードレール仕様_deterministic_policy_check, docs_02_仕様_要件_中延二葉_段階3_dify_llm安全ガードレール仕様_llm_input_data_contract, docs_02_仕様_要件_中延二葉_段階3_dify_llm安全ガードレール仕様_information_priority, data_naisui_poc_04_llm_knowledge_safety_guardrails, docs_02_仕様_要件_中延二葉_段階3_dify_llm安全ガードレール仕様_dify_workflow [EXTRACTED 1.00]
- **実績照合による検証体系（正解データ・指標・相関）** — docs_03_モデル検証_中延二葉_モデル実績照合レビュー_inundation_history_31yr, docs_03_モデル検証_中延二葉_モデル実績照合レビュー_r7_0911_inundation_record, docs_03_モデル検証_中延二葉_モデル実績照合レビュー_spearman_tied_rank, docs_03_モデル検証_中延二葉_モデル実績照合レビュー_area_over_threshold_ratio, docs_03_モデル検証_中延二葉_モデル実績照合レビュー_building_count_normalization [EXTRACTED 1.00]
- **Official hazard data comparison / IoU flow** — data_naisui_poc_01_raw_hazard_map_readme_tokyo_jonan_usuisyusui_pdf, data_naisui_poc_01_raw_hazard_map_readme_vectorize_georeferenced_hazard, data_naisui_poc_01_raw_hazard_map_readme_hazard_pdf_colour_classes, data_naisui_poc_01_raw_hazard_map_readme_preprocess_hazard_geojson, data_naisui_poc_01_raw_hazard_map_readme_hazard_shinagawa_normalized, data_naisui_poc_01_raw_hazard_map_readme_evaluate_inundation_iou [INFERRED 0.85]
- **公式PDFハザードの派生ベクタ化とIoU比較の流れ** — docs_04_gis作業手順_品川_ハザードpdf地理参照_色採取記録_jonan_usuisyusui_pdf_2026, docs_04_gis作業手順_品川_ハザードpdf地理参照_色採取記録_shinagawa_georeferenced_tif, docs_04_gis作業手順_品川_ハザードpdf地理参照_色採取記録_legend_rgb_colors, docs_04_gis作業手順_品川_ハザードpdf地理参照_色採取記録_hazard_shinagawa_normalized_gpkg, docs_03_モデル検証_中延二葉_pysheds凹地容量_感度分析_iou_auto_evaluation [INFERRED 0.85]
- **town_facts -> RAG markdown -> Dify knowledge pipeline** — rag_readme_build_town_facts, rag_readme_town_facts_json, rag_readme_build_rag_markdown, rag_readme_dify_knowledge [INFERRED 0.85]

## Communities (55 total, 11 thin omitted)

### Community 0 - "町丁目リスク集計と地域背景"
Cohesion: 0.09
Nodes (73): tools/export_risk_lookup.py, shinagawa_town_2020.geojson (e-Stat 2020 census town boundaries, 13109), named_roads_2026-09-25.json (OSM named roads via Overpass), Overpass API endpoint overpass.private.coffee, 整備水準 1時間50mm (50mm/h design standard), 地域の背景 (Regional background: Tachiai River valley), 平成11年8月29日集中豪雨 (1999 rainstorm, 2,009 buildings flooded), 令和7年9月11日の大雨 (2025 rain, ~120mm/h near Shinagawa) (+65 more)

### Community 1 - "流向・浸水IoU評価"
Cohesion: 0.06
Nodes (59): Affine, parse_args(), Namespace, Hydrologically condition GSI DEM tiles and calculate D8 flow products. Outputs…, run(), evaluate(), main(), parse_model() (+51 more)

### Community 2 - "土地利用・建物データ処理"
Cohesion: 0.07
Nodes (58): DatasetReader, load_landuse(), m2(), parse_args(), DataFrame, GeoDataFrame, Namespace, Path (+50 more)

### Community 3 - "PLATEAU 3D都市モデル"
Cohesion: 0.05
Nodes (53): PLATEAU 3D都市モデル（品川区）README, bldg_2025_lod0.gpkg（建物外形LOD0）, PLATEAU CityGMLカタログAPI, 土地利用分類対応表 landuse_category_mapping.csv, PLATEAU建築物モデル bldg（品川区2025, CityGML）, PLATEAU土地利用モデル luse（533935）, uro:RiverFloodingRiskAttribute（城南地区河川流域, L2）, PLATEAU取得URL一覧 (+45 more)

### Community 4 - "モデル実績照合レビュー"
Cohesion: 0.08
Nodes (44): 中延・二葉 モデル実績照合レビュー, 指標 area_over_threshold_ratio, 建物棟数による実績正規化（フェーズ0B）, DEMアーティファクト（最大深7.32m等）, 二葉二丁目・中延三丁目の順位食い違い, 平成11年8月29日集中豪雨イベント, 品川区 町丁別浸水実績（31年累計）, 指標 max_depth_m（不適切） (+36 more)

### Community 5 - "100mm/h定性比較と凹地補正"
Cohesion: 0.07
Nodes (40): 中延・二葉 100mm/h 初期定性比較, D8流向試行（不採用）, Jaccard係数による区域一致評価, Priority-Flood凹地補正と凹地貯留・越流, シナリオ sc_100mm_extreme (100mm/h), 品川区 雨水出水浸水ハザードマップ, 一律等価排水能力 50mm/h, 中延・二葉 Pysheds凹地容量 感度分析 (+32 more)

### Community 6 - "フロント開発依存パッケージ"
Cohesion: 0.05
Nodes (41): autoprefixer, @chromatic-com/storybook, devDependencies, autoprefixer, @chromatic-com/storybook, oxlint, playwright, postcss (+33 more)

### Community 7 - "町丁目ファクト生成"
Cohesion: 0.14
Nodes (25): GeoDataFrame, GeoSeries, ndarray, Path, Point, culvert_facts(), direction_label(), facility() (+17 more)

### Community 8 - "地図パネル（MapPanel）"
Cohesion: 0.12
Nodes (20): addSvgImage(), applyLayerVisibility(), BASE_STYLE, boundsOfFeature(), FACILITY_POPUPS, facilityLayersAt(), facilityPopupContent(), fetchJson() (+12 more)

### Community 9 - "チャットAPIと安全ポリシー"
Cohesion: 0.15
Nodes (18): chat(), _to_chat_response(), ambiguous_location_response(), detect_emergency(), emergency_response(), _no_claims(), official_status_stub(), out_of_scope_response() (+10 more)

### Community 10 - "フロント実行時依存"
Cohesion: 0.11
Nodes (18): dependencies, maplibre-gl, react, react-dom, name, private, scripts, build (+10 more)

### Community 11 - "公式ハザード比較データ"
Cohesion: 0.14
Nodes (18): 国土数値情報 A51 雨水出水浸水想定区域 (Fussa-only, excluded), 内水ハザード比較データの台帳 (hazard comparison data ledger), tools/evaluate_inundation_iou.py (IoU evaluation, not yet run), hazard_pdf_colour_classes.json (legend RGB classes), hazard_shinagawa_normalized.gpkg (EPSG:6677), IoU評価の状態と取得要件, maximum_ponding_depth_m.tif (sc_100mm_extreme), tools/preprocess_hazard_geojson.py (+10 more)

### Community 12 - "RAGマークダウン生成"
Cohesion: 0.25
Nodes (16): chunk_culvert(), chunk_facilities(), chunk_no_culvert(), chunk_official_hazard(), chunk_overview(), chunk_ponding_places(), chunk_records(), chunk_special() (+8 more)

### Community 13 - "町丁目の客観的事実"
Cohesion: 0.17
Nodes (16): 町丁目ごとの客観的事実 town_facts.md, 暗渠（立会川）の片側への偏り（距離帯別の標高・たまりやすさ・浸水想定）, 集計から除いた鉄道用地・アンダーパス, 二葉一丁目 ふたばトンネル（鮫洲大山線）, 中延三丁目 池上線の掘割（住宅地のくぼ地ではない）, 公式の浸水想定区域（城南地区河川流域）, 雨水がたまりやすい場所（最大湛水深0.1m以上）, 通り別のたまりやすさ表（沿道10m） (+8 more)

### Community 14 - "バックエンドデータ読込"
Cohesion: 0.19
Nodes (10): _load_json(), Any, Path, Loads and caches scenario/town data at process startup. All reads happen once…, In-memory cache built once at import time., メッセージに書かれた町丁目名（TOWN_SLUGSのキー表記）を出現順に重複なく返す。 対象外の丁目（中延七丁目など）は "対象外:<表記>"…, 場所を指す言い方のうち、対象の町丁目名として読み取れないもの（「下新明」等）を返す。, Store (+2 more)

### Community 15 - "チャットパネルUI"
Cohesion: 0.15
Nodes (7): ChatPanel(), FOLLOW_UP_QUESTIONS, conversation, Empty, ErrorState, Loading, ScenarioChangedNotice

### Community 16 - "Dify知識ベースとLLM"
Cohesion: 0.18
Nodes (11): Dify LLMノードのプロンプト (dify_llm_prompt.md), Difyチャットフロー（開始→知識検索→LLM→回答）, Gemini 3.8 Flash（有料枠）モデル設定, LLM知識ベース README, LLM知識ベース, town_facts.json（町丁目ごとの数値）, 回答形式（いま確認できること/モデル位置づけ/次の確認/不確実性）, 中延・二葉 防災対話アシスタント: システム指示 (+3 more)

### Community 17 - "PoC引継ぎと採用パイプライン"
Cohesion: 0.18
Nodes (12): 開始ノードの入力変数（town_name, scenario_label, calibration_status, risk_level, area_ratio_pct, official_status）, 中延・二葉 内水氾濫PoC 引継ぎ・タスクリスト, 採用パイプライン plateau2025_v3_road050（道路優先流下版）, リスク指標 area_over_threshold_ratio（max_depth_mから切替）, 次回開始時の判断契約と優先順位, 土地利用反映版 plateau2025_v1_base（PLATEAU流出係数）, モデルを主、浸水実績は校正・検証材料とする方針, pysheds_surface_routing（採用基盤モデル） (+4 more)

### Community 18 - "LLMアダプタとJSON契約"
Cohesion: 0.38
Nodes (10): Any, _dify_contract(), generate(), _parse_json(), Dify LLM call, with the deterministic template as fallback. Builds the response…, JSON契約で検証する。違反はValueErrorにし、呼び出し側でテンプレートに戻す。, _sources(), _template() (+2 more)

### Community 19 - "Difyプロンプトと出力契約"
Cohesion: 0.18
Nodes (11): Dify無料プランのナレッジ検索レート上限, LLM出力JSON契約（headline/status/facts/model_context/safe_next_steps/prohibited_claim_check）, Difyナレッジ naisui-knowledge, prohibited_claim_check（route_instruction, shelter_safety_guarantee, ungrounded_depth_forecast）, SYSTEMプロンプト（雨水のたまりやすさマップの説明係）, バックエンドの契約検証とテンプレート応答へのフォールバック, Difyナレッジのチャンク設定（高品質・ハイブリッド検索・区切り\n\n・オーバーラップ0）, 回答下の質問例5つ（固定の章立てに対応） (+3 more)

### Community 20 - "アプリ全体構成（App）"
Cohesion: 0.27
Nodes (6): App(), MapPanel, nextId(), useIsPC(), api, react

### Community 21 - "FastAPIエンドポイント"
Cohesion: 0.29
Nodes (7): get_scenario(), get_scenarios(), get_towns(), health(), _mtime(), Backend dependencies: FastAPI, uvicorn, pydantic, get

### Community 22 - "LLM安全ガードレール仕様"
Cohesion: 0.22
Nodes (10): 根拠の優先順位（公式情報>現地観測>モデル結果）, LLM必須ルール safety_guardrails.txt, 中延・二葉 内水氾濫AI/GIS PoC 全体概要, PoC段階構成（1基盤/2a簡易湛水/2b集計検証/2c高度化/3 AI）, 町丁目別 risk_lookup JSON, 段階3 Dify/LLM安全ガードレール仕様, ガードレール受入テスト（緊急・注入・避難所等）, 決定的ポリシー判定（LLM前段） (+2 more)

### Community 23 - "地図UI・配色・記号"
Cohesion: 0.20
Nodes (10): 配色（brandを避難所の緑系に、白文字は700以上）, Case A〜C（凹地容量0.5/1.0/1.5m）の相対IoU比較, 避難所・土のう置場の地図記号（SVG）と吹き出し, 公式PDF（城南地区河川流域 雨水出水浸水想定区域図）の地理参照とPDF派生ベクタ, 地図レイヤー（ハザードオーバーレイ・土のう置場・避難所）, モバイル 地図なしチャットのみUI, PC 地図＋チャット2列構成（チャット列360〜520px）, 技術前提（React+Vite+Tailwind+MapLibre GL JS / FastAPI+uv） (+2 more)

### Community 24 - "Vercel/Renderデプロイ"
Cohesion: 0.33
Nodes (9): 本番ビルドでMapLibre workerが出力されない問題の修正（setWorkerUrl, worker.format es）, Renderデプロイ（バックエンド naisui-api.onrender.com、Blueprint naisui-shinagawa）, Vercelデプロイ（画面 naisui.vercel.app、Root Directory frontend）, 検収チェックリスト, Render無料プランのコールドスタート懸念, 避難所5件・土のう置場の国土地理院APIジオコーディング, buildFilter（backend・shelter・web_map・pysheds_surface_routing_roadsの変更のみ再デプロイ）, 環境変数（DIFY_BASE_URL, DIFY_TIMEOUT_SECONDS, DIFY_API_KEY, ALLOWED_ORIGINS） (+1 more)

### Community 25 - "範囲外・判断質問の検出"
Cohesion: 0.36
Nodes (4): detect_out_of_scope(), 判断を求める質問なら "judgment"、今の状況・予報を聞く質問なら "realtime" を返す。, DetectOutOfScopeTest, このマップが答えない質問（判断・今の状況）の判定の回帰テスト。 実行: backend/ で `python -m unittest discover…

### Community 26 - "水収支による浸水予測文献"
Cohesion: 0.25
Nodes (8): 簡易水収支 surface_water_balance v1（参考扱いへ降格）, GISを利用した内水氾濫の危険予測および検証（久保 2018）要約, Q1+Q2>Q3+Q4 内水氾濫水収支, 港北区高田西一丁目 検証（一致率86.6%）, GISを用いた浸水予測モデル（解説）, 4解析ステップ（地形・流出・下水道・地表氾濫）, 流入量>排出量 水収支（浸水発生条件）, 湛水量=max(0,湛水量+(降雨×流出係数−等価排水能力)Δt)

### Community 27 - "oxlint設定"
Cohesion: 0.25
Nodes (7): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema, oxc, warn

### Community 28 - "湛水オーバーレイ書き出し"
Cohesion: 0.36
Nodes (7): color_for_depth(), parse_args(), Namespace, ndarray, Export a scenario's max ponding-depth raster to a colorized PNG overlay for…, run(), target_area_geometry_4326()

### Community 29 - "AI・水理ハイブリッド洪水予測"
Cohesion: 0.33
Nodes (7): AIモデルと水理モデルのハイブリッド洪水予測（渡辺 2026）要約, PINNs河道モデル・多地点データ同化, RRIモデル＋DNNハイブリッド, PLATEAU UC25-04 AI環境シミュレーション高速化, iRIC Nays2D Flood, PINO（PhysicsNeMo）AI浸水シミュレータ, PLATEAU VIEW 可視化

### Community 30 - "町丁目選択UI"
Cohesion: 0.38
Nodes (5): groupTowns(), Interactive, NoSelection, towns, TownSelector()

### Community 31 - "UI受け入れ基準"
Cohesion: 0.33
Nodes (6): calibration_status: pre_calibration_screening, UI デザイン受け入れ基準, モバイルは地図なしチャットのみ, 凡例に「校正前のスクリーニング結果」常時表示, 10町丁目ボタン選択, LLM入力データ契約（official_status / model_result）

### Community 32 - "ハザード層書き出し"
Cohesion: 0.47
Nodes (5): parse_args(), Namespace, Export the QGIS-derived hazard vector layer to a web-map-ready GeoJSON.…, rgb_string_to_hex(), run()

### Community 33 - "土のう置場ジオコーディング"
Cohesion: 0.47
Nodes (5): geocode(), parse_args(), Namespace, Geocode sandbag storage locations (address-only) to lat/lon and GeoJSON. Uses…, run()

### Community 34 - "回答ルールと自由入力の扱い"
Cohesion: 0.40
Nodes (5): 回答のルール（出所を分ける・実績を予測根拠にしない・unknownは未確認）, 最初に守ること（校正前スクリーニング・公式情報優先）, 大前提の見直し：ハザードマップ「中延・二葉 雨水のたまりやすさマップ」, 自由入力の扱いの決定（2026-09-29、判断・今の状況の質問はDifyを呼ばず定型応答）, 範囲外・特定できない場所の扱い（データ範囲を示し選択へ誘導）

### Community 35 - "フロントREADME・雛形"
Cohesion: 0.40
Nodes (4): Frontend index.html, Expanding the Oxlint configuration, React Compiler, React + Vite

### Community 37 - "DEM平滑化"
Cohesion: 0.50
Nodes (4): parse_args(), Namespace, Create a reversible median-filtered DEM variant for sensitivity analysis., run()

### Community 38 - "チャットAPIスキーマ"
Cohesion: 0.67
Nodes (3): ChatRequest, ChatResponse, BaseModel

### Community 39 - "A51 GMLデータ説明"
Cohesion: 0.50
Nodes (3): A51-25_13_GML の収録範囲, 利用上の前提, 重要

### Community 40 - "湛水深オーバーレイ概念"
Cohesion: 0.67
Nodes (4): Ponding Depth Map Overlay (153mm/h, 24h 690mm, official scenario), Ponding (Inundation) Depth Raster, Official Design Rainfall Scenario: 153 mm/h peak, 690 mm / 24h, Transparent PNG Web Map Overlay (purple depth ramp)

### Community 41 - "地図アイコンと施設色"
Cohesion: 0.50
Nodes (4): Amber #d97706 (sandbag color family), Green #16a34a (shelter color family), Sandbag Map Icon (土のう置場), Shelter Map Icon (避難所)

## Ambiguous Edges - Review These
- `named_roads_2026-09-25.json (OSM named roads via Overpass)` → `tools/build_town_facts.py`  [AMBIGUOUS]
  data/naisui_poc/01_raw/osm/README.md · relation: shares_data_with

## Knowledge Gaps
- **137 isolated node(s):** `name`, `private`, `build`, `build-storybook`, `dev` (+132 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `named_roads_2026-09-25.json (OSM named roads via Overpass)` and `tools/build_town_facts.py`?**
  _Edge tagged AMBIGUOUS (relation: shares_data_with) - confidence is low._
- **Why does `町丁目ごとの客観的事実 town_facts.md` connect `町丁目の客観的事実` to `Dify知識ベースとLLM`, `町丁目ファクト生成`?**
  _High betweenness centrality (0.133) - this node is a cross-community bridge._
- **Why does `避難所・土のう置場（住所・袋の数）` connect `町丁目の客観的事実` to `地図パネル（MapPanel）`?**
  _High betweenness centrality (0.117) - this node is a cross-community bridge._
- **Why does `リスク指標 area_over_threshold_ratio（max_depth_mから切替）` connect `PoC引継ぎと採用パイプライン` to `モデル実績照合レビュー`?**
  _High betweenness centrality (0.099) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `中延・二葉 モデル実績照合レビュー` (e.g. with `品川 ハザードPDF地理参照・色採取記録` and `risk_lookup_sc_{scenario}.json（Dify用ナレッジ）`) actually correct?**
  _`中延・二葉 モデル実績照合レビュー` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `name`, `private`, `build` to the rest of the system?**
  _137 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `町丁目リスク集計と地域背景` be split into smaller, more focused modules?**
  _Cohesion score 0.0867579908675799 - nodes in this community are weakly interconnected._