# 中延・二葉 内水氾濫 AI/GIS PoC — 全体概要

## 目的

品川区の中延・二葉を対象に、豪雨時の地表湛水リスクをGIS上で可視化し、将来はDify / ChatGPTから根拠付きで照会できるようにするPoCです。

初期段階は、下水道管網を精密に水理計算するものではありません。DEM、降雨、**等価排水能力50mm/h**から危険箇所を保守的に絞るスクリーニングモデルです。

## 全体の流れ

```text
DEM・ハザード・浸水実績・町丁目境界・避難関連データ
                         ↓
      GISデータ基盤（中延・二葉に対象を限定）
                         ↓
降雨シナリオ + 一律等価排水能力50mm/h + 簡易地表流
                         ↓
時刻別／最大湛水深 GeoTIFF + 水収支CSV + シナリオJSON
                         ↓
町丁目別 risk_lookup JSON
                         ↓
  Difyワークフロー / ChatGPTの根拠付き対話・要約UI
```

## 段階別の成果物

| 段階 | 内容 | 主な成果物 | 状態 |
|---|---|---|---|
| 1. 基盤PoC | 地形、実績、ハザード、避難関連データを整理 | `data/naisui_poc/01_raw/`、統合GISデータ | 進行中 |
| 2a. 簡易湛水モデル | DEM上で降雨と一律50mm/h排水の水収支を計算 | GeoTIFF、CSV、`scenario_summary.json` | 実装・試行済み |
| 2b. 町丁目集計・検証 | 町丁目別リスク化、行政ハザード・実績と比較 | `risk_lookup_*.json`、一致評価 | 集計実装・標準3ケース出力済み。空間一致の校正入力待ち |
| 2c. 高度化 | 必要箇所だけ下水道管網／1D-2D水理を導入 | 管網モデル、検証済み基準データ | 未着手 |
| 3. AI/LLM PoC | シナリオ実行、結果要約、根拠付き対話 | Difyワークフロー、対話UI、ガードレール | 未着手 |

## 現在動く処理

1. `rainfall_scenarios.csv` で降雨シナリオを管理する。
2. `run_surface_water_balance.py --scenario-id ...` が時刻別・最大湛水深を計算する。
3. シナリオごとにGeoTIFF、CSV、`scenario_summary.json`を別フォルダへ出力する。
4. 町丁目境界を配置後、`export_risk_lookup.py` が中延・二葉の町丁目別JSONを出力する。

## 標準降雨シナリオ

- `sc_50mm_const`: 等価排水能力と同水準の基準ケース
- `sc_80mm_peak`: 強い集中豪雨の比較ケース
- `sc_100mm_extreme`: 近年の短時間極端降雨を想定する厳しいストレステスト

各ケースについてGeoTIFF、時系列CSV、シナリオ要約、町丁目別`risk_lookup`を出力済みです。

## 入出力の所在

| 種別 | 場所 |
|---|---|
| 一次データ | `data/naisui_poc/01_raw/` |
| 排水・管網入力テンプレート | `data/naisui_poc/02_processed/model_input/` |
| 降雨シナリオ | `data/naisui_poc/03_scenarios/rainfall_scenarios.csv` |
| 計算結果 | `data/naisui_poc/02_processed/surface_water_balance/{scenario_id}/` |
| LLMガードレール | `data/naisui_poc/04_llm_knowledge/safety_guardrails.txt` |
| 計算・集計コード | `tools/run_surface_water_balance.py`、`tools/export_risk_lookup.py` |

## 重要な制約

- 50mm/hは初期PoCの等価的な排水能力であり、特定下水管の実能力を意味しません。
- 出力は危険箇所を見つけるためのスクリーニング結果であり、個別地点の浸水予報・避難判断には使いません。
- Dify/LLMは、公式の警報・避難情報を優先し、断定的な避難誘導を行わない設計とします。
