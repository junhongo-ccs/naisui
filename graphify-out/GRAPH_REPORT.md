# Graph Report - naisui  (2026-09-30)

## Corpus Check
- 37 files · ~69,087 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 824 nodes · 1435 edges · 58 communities (46 shown, 12 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 132 edges (avg confidence: 0.85)
- Token cost: 219,518 input · 0 output

## Community Hubs (Navigation)
- pysheds地表流計算
- 地域の背景と水害史
- 土地利用・流出係数の前処理
- バックエンドのデータ層
- PLATEAUデータ
- Difyチャットフロー設定
- フロントの開発依存
- 町丁目の事実づくり
- このマップについて（資料）
- 地図パネル
- 引継ぎ・タスクリスト
- 凹地容量の感度分析
- LLMアダプタ（Dify呼び出し）
- フロントのパッケージ
- 公式ハザードとIoU評価
- 町丁目の集計
- RAG資料の生成
- 町丁目ごとの客観的事実
- チャットパネル
- 土地利用反映モデル比較
- デプロイと検収
- 城南地区CSV座標検証
- 100mm初期定性比較
- アプリ本体（ヘッダー・開閉）
- Difyナレッジ構成
- モデル実績照合レビュー
- 水収支モデルの先行研究
- 地域の選択（折りたたみ）
- 湛水オーバーレイ出力
- AI洪水予測の先行研究
- ハザードPDFのベクタ化
- index.htmlとOGP
- Oxlint設定
- Storybook地図
- ハザード層の出力
- 土のう置場のジオコーディング
- ハザードGeoJSON前処理
- Storybook設定
- DEM平滑化
- A51データの注意
- 湛水深オーバーレイ画像
- 前提の見直しと質問の扱い
- 避難所・土のうの記号
- OGP画像
- リスク表の出力
- ファビコン（波）
- 旧ファビコン（Vite）
- 型 Any
- ChatRequest
- ChatResponse
- アクセス制御なし
- 型 Path
- 型 GeoDataFrame
- 型 GeoSeries
- 型 ndarray

## God Nodes (most connected - your core abstractions)
1. `中延・二葉 内水氾濫PoC 引継ぎ・タスクリスト` - 27 edges
2. `用語とデータの説明 (Terms and data explanation)` - 25 edges
3. `中延・二葉 モデル実績照合レビュー` - 23 edges
4. `立会川の暗渠 / 立会川幹線 (culverted river, trunk sewer)` - 21 edges
5. `このマップについて (About the map, RAG)` - 21 edges
6. `chat()` - 17 edges
7. `RAG README (Dify knowledge)` - 17 edges
8. `中延・二葉 土地利用反映モデル比較（フェーズ1）` - 16 edges
9. `中延六丁目 (town facts)` - 16 edges
10. `雨水がたまりやすい場所（試算）(modelled ponding-prone area)` - 16 edges

## Surprising Connections (you probably didn't know these)
- `使っているデータ` --semantically_similar_to--> `用語とデータの説明 (Terms and data explanation)`  [INFERRED] [semantically similar]
  frontend/public/about.html → RAG/03_用語とデータの説明.md
- `暗渠（立会川）の片側への偏り（距離帯別の標高・たまりやすさ・浸水想定）` --shares_data_with--> `culvert_facts()`  [INFERRED]
  data/naisui_poc/02_processed/town_facts/town_facts.md → tools/build_town_facts.py
- `town_facts.json（町丁目ごとの数値）` --semantically_similar_to--> `town_facts.json (02_processed/town_facts)`  [INFERRED] [semantically similar]
  data/naisui_poc/04_llm_knowledge/README.md → RAG/README.md
- `最大の深さから面積の割合への切替（ρ=−0.30→同じ向き、2026-09-15）` --semantically_similar_to--> `リスク指標 area_over_threshold_ratio（max_depth_mから切替）`  [INFERRED] [semantically similar]
  RAG/04_このマップについて.md → docs/00_現状・引継ぎ/中延二葉_PoC_引継ぎ・タスクリスト.md
- `応答JSON契約（headline/status/facts/model_context/safe_next_steps/prohibited_claim_check/sources）` --semantically_similar_to--> `LLM出力JSON契約（headline/status/facts/model_context/safe_next_steps/prohibited_claim_check）`  [INFERRED] [semantically similar]
  docs/02_仕様・要件/中延二葉_チャットUI_要件定義.md → data/naisui_poc/04_llm_knowledge/dify_llm_prompt.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **暗渠が町内を通る地形パターンAの町丁目（浸水実績上位）** — rag_02___________nakanobu_5chome, rag_02___________nakanobu_6chome, rag_02___________futaba_1chome, rag_02___________futaba_2chome, rag_02___________futaba_3chome, rag_02___________futaba_4chome, rag_01_______pattern_a, rag_01_______tachiaigawa_culvert [EXTRACTED 1.00]
- **雨水がたまりやすい場所の試算パイプライン** — rag_04___________dem_d8_flow, rag_04___________runoff_coefficients, rag_04___________rain_and_drainage, rag_04___________road_priority_routing, rag_04___________risk_classes, rag_03___________ponding_prone_area [EXTRACTED 1.00]
- **チャットの安全な回答フロー（決定的判定→知識検索→LLM→契約検証）** — data_naisui_poc_04_llm_knowledge_dify_chatflow_setup_backend_policy, rag_readme_dify_chatflow_retrieval_node, data_naisui_poc_04_llm_knowledge_dify_llm_prompt_system_prompt, data_naisui_poc_04_llm_knowledge_dify_llm_prompt_json_output_contract, data_naisui_poc_04_llm_knowledge_dify_llm_prompt_prohibited_claim_check, data_naisui_poc_04_llm_knowledge_dify_chatflow_setup_backend_responsibilities [INFERRED 0.85]
- **簡易湛水モデルの3評価指標** — docs_02_仕様_要件_中延二葉_簡易湛水モデル_校正評価仕様_hit_rate_metric, docs_02_仕様_要件_中延二葉_簡易湛水モデル_校正評価仕様_jaccard_overlap_metric, docs_02_仕様_要件_中延二葉_簡易湛水モデル_校正評価仕様_town_rank_consistency [EXTRACTED 1.00]
- **Pattern A towns along Tachiai culvert (most 2025 flood reports)** — rag_02___________nakanobu_5chome, rag_02___________nakanobu_6chome, rag_02___________futaba_1chome, rag_02___________futaba_2chome, rag_02___________futaba_3chome, rag_02___________futaba_4chome, rag_01_______pattern_a, rag_01_______tachiaigawa_culvert [EXTRACTED 1.00]
- **PLATEAU導入フェーズ1-2のモデル比較（土地利用・建物・道路）** — docs_03_モデル検証_中延二葉_土地利用反映モデル比較_plateau2025_v1_base, docs_03_モデル検証_中延二葉_建物流下遮断モデル比較_building_flow_blocking, docs_03_モデル検証_中延二葉_道路優先流下モデル比較_road_priority_routing, docs_03_モデル検証_中延二葉_建物流下遮断モデル比較_surface_fraction_plateau2025_v1, docs_03_モデル検証_中延二葉_土地利用反映モデル比較_plateau_introduction_plan [EXTRACTED 1.00]
- **PLATEAU導入による段階的モデル改善** — docs_01_概要_計画_plateau導入計画_phase_0b_building_normalization, docs_01_概要_計画_plateau導入計画_phase_1_landuse_runoff, docs_01_概要_計画_plateau導入計画_phase_2_building_road_flow, docs_01_概要_計画_plateau導入計画_phase_3_2d_unsteady_flow [EXTRACTED 1.00]
- **LLM安全ガードレール構成（決定的ポリシー・入出力契約・優先順位）** — docs_02_仕様_要件_中延二葉_段階3_dify_llm安全ガードレール仕様_deterministic_policy_check, docs_02_仕様_要件_中延二葉_段階3_dify_llm安全ガードレール仕様_llm_input_data_contract, docs_02_仕様_要件_中延二葉_段階3_dify_llm安全ガードレール仕様_information_priority, data_naisui_poc_04_llm_knowledge_safety_guardrails, docs_02_仕様_要件_中延二葉_段階3_dify_llm安全ガードレール仕様_dify_workflow [EXTRACTED 1.00]
- **実績照合による検証体系（正解データ・指標・相関）** — docs_03_モデル検証_中延二葉_モデル実績照合レビュー_inundation_history_31yr, docs_03_モデル検証_中延二葉_モデル実績照合レビュー_r7_0911_inundation_record, docs_03_モデル検証_中延二葉_モデル実績照合レビュー_spearman_tied_rank, docs_03_モデル検証_中延二葉_モデル実績照合レビュー_area_over_threshold_ratio, docs_03_モデル検証_中延二葉_モデル実績照合レビュー_building_count_normalization [EXTRACTED 1.00]
- **Official hazard data comparison / IoU flow** — data_naisui_poc_01_raw_hazard_map_readme_tokyo_jonan_usuisyusui_pdf, data_naisui_poc_01_raw_hazard_map_readme_vectorize_georeferenced_hazard, data_naisui_poc_01_raw_hazard_map_readme_hazard_pdf_colour_classes, data_naisui_poc_01_raw_hazard_map_readme_preprocess_hazard_geojson, data_naisui_poc_01_raw_hazard_map_readme_hazard_shinagawa_normalized, data_naisui_poc_01_raw_hazard_map_readme_evaluate_inundation_iou [INFERRED 0.85]
- **公式PDFハザードの派生ベクタ化とIoU比較の流れ** — docs_04_gis作業手順_品川_ハザードpdf地理参照_色採取記録_jonan_usuisyusui_pdf_2026, docs_04_gis作業手順_品川_ハザードpdf地理参照_色採取記録_shinagawa_georeferenced_tif, docs_04_gis作業手順_品川_ハザードpdf地理参照_色採取記録_legend_rgb_colors, docs_04_gis作業手順_品川_ハザードpdf地理参照_色採取記録_hazard_shinagawa_normalized_gpkg, docs_03_モデル検証_中延二葉_pysheds凹地容量_感度分析_iou_auto_evaluation [INFERRED 0.85]

## Communities (58 total, 12 thin omitted)

### Community 0 - "pysheds地表流計算"
Cohesion: 0.06
Nodes (58): Affine, parse_args(), Namespace, Hydrologically condition GSI DEM tiles and calculate D8 flow products. Outputs…, run(), evaluate(), main(), parse_model() (+50 more)

### Community 1 - "地域の背景と水害史"
Cohesion: 0.10
Nodes (62): named_roads_2026-09-25.json (OSM named roads via Overpass), Overpass API endpoint overpass.private.coffee, 整備水準 1時間50mm (50mm/h design standard), 地域の背景 (Regional background: Tachiai River valley), 平成11年8月29日集中豪雨 (1999 rainstorm, 2,009 buildings flooded), 令和7年9月11日の大雨 (2025 rain, ~120mm/h near Shinagawa), 東京管区気象台 令和7年9月11日大雨速報 (source 3), 内水はん濫 (pluvial / internal flooding) (+54 more)

### Community 2 - "土地利用・流出係数の前処理"
Cohesion: 0.07
Nodes (58): DatasetReader, load_landuse(), m2(), parse_args(), DataFrame, GeoDataFrame, Namespace, Path (+50 more)

### Community 3 - "バックエンドのデータ層"
Cohesion: 0.06
Nodes (44): _load_json(), Any, Path, Loads and caches scenario/town data at process startup. All reads happen once…, In-memory cache built once at import time., メッセージに書かれた町丁目名（TOWN_SLUGSのキー表記）を出現順に重複なく返す。 対象外の丁目（中延七丁目など）は "対象外:<表記>"…, 場所を指す言い方のうち、対象の町丁目名として読み取れないもの（「下新明」等）を返す。, Store (+36 more)

### Community 4 - "PLATEAUデータ"
Cohesion: 0.06
Nodes (46): PLATEAU 3D都市モデル（品川区）README, bldg_2025_lod0.gpkg（建物外形LOD0）, PLATEAU CityGMLカタログAPI, 土地利用分類対応表 landuse_category_mapping.csv, PLATEAU建築物モデル bldg（品川区2025, CityGML）, PLATEAU土地利用モデル luse（533935）, uro:RiverFloodingRiskAttribute（城南地区河川流域, L2）, PLATEAU取得URL一覧 (+38 more)

### Community 5 - "Difyチャットフロー設定"
Cohesion: 0.07
Nodes (42): Dify チャットフローの設定と注意 (dify_chatflow_setup.md), このマップ・用語の質問モード（town_name=このマップ全般、policy.detect_about_map）, backend/app/llm_adapter.py, backend/app/policy.py, バックエンド側で行うこと（sources付与、契約検証、緊急ワード判定 policy.detect_emergency）, Difyのナレッジとリポジトリの差（「校正前」表記の残存）, モデル設定（Gemini 3.8 Flash 有料枠、Thinking Low、Temperature 0.2、Output 4096）, SYSTEMの貼り方（変数チップ、開始ノードID 1790583408474、公開→更新） (+34 more)

### Community 6 - "フロントの開発依存"
Cohesion: 0.05
Nodes (41): autoprefixer, @chromatic-com/storybook, devDependencies, autoprefixer, @chromatic-com/storybook, oxlint, playwright, postcss (+33 more)

### Community 7 - "町丁目の事実づくり"
Cohesion: 0.14
Nodes (25): GeoDataFrame, GeoSeries, ndarray, Point, culvert_facts(), direction_label(), facility(), Grid (+17 more)

### Community 8 - "このマップについて（資料）"
Cohesion: 0.14
Nodes (22): Dify無料プランのナレッジ検索レート上限（約10回でHTTP 400→テンプレート応答）, このマップについて (about.html 解説ページ), 計算のしかた（pipeline・流出係数・雨の配分図）, チャットのしくみ（AIに渡している知識RAG、回答のルール）, 実績との照合, 使っているデータ, 経緯, 導入した技術・サービス (+14 more)

### Community 9 - "地図パネル"
Cohesion: 0.12
Nodes (19): addSvgImage(), applyLayerVisibility(), BASE_STYLE, boundsOfFeature(), FACILITY_POPUPS, facilityLayersAt(), facilityPopupContent(), fetchJson() (+11 more)

### Community 10 - "引継ぎ・タスクリスト"
Cohesion: 0.16
Nodes (21): 中延・二葉 内水氾濫PoC 引継ぎ・タスクリスト, 採用パイプライン plateau2025_v3_road050（道路優先流下版）, リスク指標 area_over_threshold_ratio（max_depth_mから切替）, 配色（brandを避難所の緑系に、白文字は700以上）, Dify前段CloudflareのUser-Agent拒否（403 error 1010）, 次回開始時の判断契約と優先順位, Case A〜C（凹地容量0.5/1.0/1.5m）の相対IoU比較, 土地利用反映版 plateau2025_v1_base（PLATEAU流出係数） (+13 more)

### Community 11 - "凹地容量の感度分析"
Cohesion: 0.14
Nodes (21): 中延・二葉 Pysheds凹地容量 感度分析, Case A 凹地容量0.5m (median3_cap0p5m), Case B 凹地容量1.0m (median3_cap1m), Case C 凹地容量1.5m (median3_cap1p5m), dem_median_3x3.tif 平滑化DEM, depression_candidates.geojson, IoU自動評価（0.1m/0.2m閾値）, 採用パイプライン pysheds_surface_routing (+13 more)

### Community 12 - "LLMアダプタ（Dify呼び出し）"
Cohesion: 0.18
Nodes (19): _call_dify(), _dify_contract(), generate(), generate_about_map(), _parse_json(), Any, Dify LLM call, with the deterministic template as fallback. Builds the response…, このマップ（Webツール）についての質問に答える。町丁目の数値は渡さない。 (+11 more)

### Community 13 - "フロントのパッケージ"
Cohesion: 0.11
Nodes (18): dependencies, maplibre-gl, react, react-dom, name, private, scripts, build (+10 more)

### Community 14 - "公式ハザードとIoU評価"
Cohesion: 0.14
Nodes (18): 国土数値情報 A51 雨水出水浸水想定区域 (Fussa-only, excluded), 内水ハザード比較データの台帳 (hazard comparison data ledger), tools/evaluate_inundation_iou.py (IoU evaluation, not yet run), hazard_pdf_colour_classes.json (legend RGB classes), hazard_shinagawa_normalized.gpkg (EPSG:6677), IoU評価の状態と取得要件, maximum_ponding_depth_m.tif (sc_100mm_extreme), tools/preprocess_hazard_geojson.py (+10 more)

### Community 15 - "町丁目の集計"
Cohesion: 0.18
Nodes (16): EPSG:3857名目画素面積→地上面積補正（約1.52倍過大の修正）, 町丁目ポリゴン取得・空間集計手順, e-Stat 町丁目境界（令和2年国勢調査小地域, S_NAME）, risk_lookup_sc_{scenario}.json（Dify用ナレッジ）, ゾーン統計（ラスタ×町丁目ポリゴン）, parse_args(), parse_elapsed_minutes(), Namespace (+8 more)

### Community 16 - "RAG資料の生成"
Cohesion: 0.25
Nodes (16): chunk_culvert(), chunk_facilities(), chunk_no_culvert(), chunk_official_hazard(), chunk_overview(), chunk_ponding_places(), chunk_records(), chunk_special() (+8 more)

### Community 17 - "町丁目ごとの客観的事実"
Cohesion: 0.17
Nodes (16): 町丁目ごとの客観的事実 town_facts.md, 暗渠（立会川）の片側への偏り（距離帯別の標高・たまりやすさ・浸水想定）, 集計から除いた鉄道用地・アンダーパス, 二葉一丁目 ふたばトンネル（鮫洲大山線）, 中延三丁目 池上線の掘割（住宅地のくぼ地ではない）, 公式の浸水想定区域（城南地区河川流域）, 雨水がたまりやすい場所（最大湛水深0.1m以上）, 通り別のたまりやすさ表（沿道10m） (+8 more)

### Community 18 - "チャットパネル"
Cohesion: 0.13
Nodes (8): ChatPanel(), FOLLOW_UP_QUESTIONS, MAP_FOLLOW_UP_QUESTIONS, conversation, Empty, ErrorState, Loading, ScenarioChangedNotice

### Community 19 - "土地利用反映モデル比較"
Cohesion: 0.27
Nodes (15): DEMアーティファクト（最大深7.32m等）, 二葉二丁目・中延三丁目の順位食い違い, シナリオ sc_153mmh_24h_690mm_official（153mm/h・690mm）, 中延・二葉 土地利用反映モデル比較（フェーズ1）, 土地利用反映版 plateau2025_v1_base, PLATEAU bldg 2025 建物外形 lod0RoofEdge, PLATEAU導入計画（docs/01_概要・計画/PLATEAU導入計画.md）, PLATEAU luse 土地利用（東京都土地利用現況調査2021） (+7 more)

### Community 20 - "デプロイと検収"
Cohesion: 0.24
Nodes (12): 本番ビルドでMapLibre workerが出力されない問題の修正（setWorkerUrl, worker.format es）, Renderデプロイ（バックエンド naisui-api.onrender.com、Blueprint naisui-shinagawa）, Vercelデプロイ（画面 naisui.vercel.app、Root Directory frontend）, 検収チェックリスト, 地図レイヤー（ハザードオーバーレイ・土のう置場・避難所）, Render無料プランのコールドスタート懸念, 避難所5件・土のう置場の国土地理院APIジオコーディング, 使っているAIと公開先（Dify, Gemini 3.8 Flash, gemini-embedding-001, Vercel, Render） (+4 more)

### Community 21 - "城南地区CSV座標検証"
Cohesion: 0.21
Nodes (11): 2026-09-24 城南地区CSV座標検証・引継ぎ, jonankaisei_csv2_tokyo_datum_working.gpkg（708,938点）, 2018年 城南地区河川流域浸水予想区域図 CSV（浸水深・地盤高）, CSV座標をTokyo Datum（EPSG:4301）と解釈, 品川区・内水氾濫GIS調査メモ（公開データ活用案）, ハザードマップGIS化方法（A:公式CSV/B:PDFジオリファレンス/C:手動デジタイズ）, risk_score 試作指標（浸水深+低標高+実績+排水不確実性+不浸透面）, 下水道の排除方式（合流式/分流式/雨水除外） (+3 more)

### Community 22 - "100mm初期定性比較"
Cohesion: 0.20
Nodes (12): 中延・二葉 100mm/h 初期定性比較, D8流向試行（不採用）, Jaccard係数による区域一致評価, Priority-Flood凹地補正と凹地貯留・越流, シナリオ sc_100mm_extreme (100mm/h), 品川区 雨水出水浸水ハザードマップ, 一律等価排水能力 50mm/h, 上流集水面積仮説（谷筋上流/下流） (+4 more)

### Community 23 - "アプリ本体（ヘッダー・開閉）"
Cohesion: 0.23
Nodes (6): App(), MapPanel, nextId(), useIsPC(), api, backendUrl()

### Community 24 - "Difyナレッジ構成"
Cohesion: 0.29
Nodes (10): アプリの構成（開始→知識検索→LLM→回答、sys.queryに町丁目名/「このマップについて」を前置）, tools/build_town_facts.py, Chunk rule: 1 chunk = 1 topic, ## heading with town name, ~500 chars max, no blank lines inside, Dify chatflow 知識検索 node, Dify knowledge naisui-knowledge (hybrid search 0.5/0.5, top-K 5, chunk separator \n\n, overlap 0), RAG README (Dify knowledge), gemini-embedding-001 (embedding model), town_facts.json (02_processed/town_facts) (+2 more)

### Community 25 - "モデル実績照合レビュー"
Cohesion: 0.24
Nodes (10): 中延・二葉 モデル実績照合レビュー, 指標 area_over_threshold_ratio, 建物棟数による実績正規化（フェーズ0B）, 平成11年8月29日集中豪雨イベント, 品川区 町丁別浸水実績（31年累計）, 指標 max_depth_m（不適切）, 令和7年9月11日浸水実績図（R7.9.11）, シナリオ sc_50mm_const (+2 more)

### Community 26 - "水収支モデルの先行研究"
Cohesion: 0.25
Nodes (8): 簡易水収支 surface_water_balance v1（参考扱いへ降格）, GISを利用した内水氾濫の危険予測および検証（久保 2018）要約, Q1+Q2>Q3+Q4 内水氾濫水収支, 港北区高田西一丁目 検証（一致率86.6%）, GISを用いた浸水予測モデル（解説）, 4解析ステップ（地形・流出・下水道・地表氾濫）, 流入量>排出量 水収支（浸水発生条件）, 湛水量=max(0,湛水量+(降雨×流出係数−等価排水能力)Δt)

### Community 27 - "地域の選択（折りたたみ）"
Cohesion: 0.32
Nodes (6): groupTowns(), CollapsedWithSelection, Interactive, NoSelection, towns, TownSelector()

### Community 28 - "湛水オーバーレイ出力"
Cohesion: 0.36
Nodes (7): color_for_depth(), parse_args(), Namespace, ndarray, Export a scenario's max ponding-depth raster to a colorized PNG overlay for…, run(), target_area_geometry_4326()

### Community 29 - "AI洪水予測の先行研究"
Cohesion: 0.33
Nodes (7): AIモデルと水理モデルのハイブリッド洪水予測（渡辺 2026）要約, PINNs河道モデル・多地点データ同化, RRIモデル＋DNNハイブリッド, PLATEAU UC25-04 AI環境シミュレーション高速化, iRIC Nays2D Flood, PINO（PhysicsNeMo）AI浸水シミュレータ, PLATEAU VIEW 可視化

### Community 30 - "ハザードPDFのベクタ化"
Cohesion: 0.48
Nodes (6): load_classes(), main(), GeoDataFrame, Path, Vectorize colour-coded inland-inundation classes from a georeferenced raster.…, write_vector()

### Community 31 - "index.htmlとOGP"
Cohesion: 0.33
Nodes (5): Frontend index.html, OGP/Twitterカード メタ情報（naisui.vercel.app, ogp.png 1200x630）, Expanding the Oxlint configuration, React Compiler, React + Vite

### Community 32 - "Oxlint設定"
Cohesion: 0.33
Nodes (5): rules, react/only-export-components, react/rules-of-hooks, $schema, warn

### Community 33 - "Storybook地図"
Cohesion: 0.33
Nodes (5): plugins, Default, scenarioDetail, oxc, react

### Community 34 - "ハザード層の出力"
Cohesion: 0.47
Nodes (5): parse_args(), Namespace, Export the QGIS-derived hazard vector layer to a web-map-ready GeoJSON.…, rgb_string_to_hex(), run()

### Community 35 - "土のう置場のジオコーディング"
Cohesion: 0.47
Nodes (5): geocode(), parse_args(), Namespace, Geocode sandbag storage locations (address-only) to lat/lon and GeoJSON. Uses…, run()

### Community 36 - "ハザードGeoJSON前処理"
Cohesion: 0.47
Nodes (5): find_depth_field(), main(), normalized_depth_min_m(), Validate and normalize an official inland-inundation polygon dataset. This tool…, Return the lower bound of a Japanese depth-class label, where possible.

### Community 38 - "DEM平滑化"
Cohesion: 0.50
Nodes (4): parse_args(), Namespace, Create a reversible median-filtered DEM variant for sensitivity analysis., run()

### Community 39 - "A51データの注意"
Cohesion: 0.50
Nodes (3): A51-25_13_GML の収録範囲, 利用上の前提, 重要

### Community 40 - "湛水深オーバーレイ画像"
Cohesion: 0.67
Nodes (4): Ponding Depth Map Overlay (153mm/h, 24h 690mm, official scenario), Ponding (Inundation) Depth Raster, Official Design Rainfall Scenario: 153 mm/h peak, 690 mm / 24h, Transparent PNG Web Map Overlay (purple depth ramp)

### Community 41 - "前提の見直しと質問の扱い"
Cohesion: 0.50
Nodes (4): 大前提の見直し：ハザードマップ「中延・二葉 雨水のたまりやすさマップ」, 自由入力の扱いの決定（2026-09-29、判断・今の状況の質問はDifyを呼ばず定型応答）, 範囲外・特定できない場所の扱い（データ範囲を示し選択へ誘導）, このマップが伝えないこと（予報・今の状況ではない平時のハザードマップ）

### Community 42 - "避難所・土のうの記号"
Cohesion: 0.50
Nodes (4): Amber #d97706 (sandbag color family), Green #16a34a (shelter color family), Sandbag Map Icon (土のう置場), Shelter Map Icon (避難所)

### Community 43 - "OGP画像"
Cohesion: 0.83
Nodes (4): 品川区 中延・二葉地区 (Shinagawa Nakanobu-Futaba District), OGP Image (雨水たまりやすさマップ share card), 雨水たまりやすさマップ (Rainwater Pooling Susceptibility Map), Urban Pluvial Flooding (内水氾濫) illustration

## Ambiguous Edges - Review These
- `named_roads_2026-09-25.json (OSM named roads via Overpass)` → `tools/build_town_facts.py`  [AMBIGUOUS]
  data/naisui_poc/01_raw/osm/README.md · relation: shares_data_with

## Knowledge Gaps
- **145 isolated node(s):** `公式の浸水想定区域（城南地区河川流域）`, `雨水がたまりやすい場所（最大湛水深0.1m以上）`, `通り別のたまりやすさ表（沿道10m）`, `LLM知識ベース`, `name` (+140 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `named_roads_2026-09-25.json (OSM named roads via Overpass)` and `tools/build_town_facts.py`?**
  _Edge tagged AMBIGUOUS (relation: shares_data_with) - confidence is low._
- **Why does `町丁目ごとの客観的事実 town_facts.md` connect `町丁目ごとの客観的事実` to `町丁目の事実づくり`?**
  _High betweenness centrality (0.147) - this node is a cross-community bridge._
- **Why does `中延・二葉 内水氾濫PoC 引継ぎ・タスクリスト` connect `引継ぎ・タスクリスト` to `Difyチャットフロー設定`, `前提の見直しと質問の扱い`, `LLMアダプタ（Dify呼び出し）`, `デプロイと検収`, `Difyナレッジ構成`?**
  _High betweenness centrality (0.142) - this node is a cross-community bridge._
- **Why does `立会川暗渠（立会川幹線）と浸水件数上位町丁目の対応` connect `引継ぎ・タスクリスト` to `地域の背景と水害史`, `町丁目の事実づくり`?**
  _High betweenness centrality (0.140) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `中延・二葉 モデル実績照合レビュー` (e.g. with `品川 ハザードPDF地理参照・色採取記録` and `risk_lookup_sc_{scenario}.json（Dify用ナレッジ）`) actually correct?**
  _`中延・二葉 モデル実績照合レビュー` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `立会川の暗渠 / 立会川幹線 (culverted river, trunk sewer)` (e.g. with `立会川暗渠（立会川幹線）と浸水件数上位町丁目の対応` and `内水はん濫（内水氾濫）`) actually correct?**
  _`立会川の暗渠 / 立会川幹線 (culverted river, trunk sewer)` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `公式の浸水想定区域（城南地区河川流域）`, `雨水がたまりやすい場所（最大湛水深0.1m以上）`, `通り別のたまりやすさ表（沿道10m）` to the rest of the system?**
  _145 weakly-connected nodes found - possible documentation gaps or missing edges._