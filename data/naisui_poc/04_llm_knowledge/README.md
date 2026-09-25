# LLM知識ベース

DifyまたはChatGPTが参照する、防災情報・データ出所・モデルの前提条件を保存する。計算結果そのものは保存せず、結果は構造化データベースまたはGIS APIから取得する。

収録候補:

- 品川区の公式避難・防災情報
- ハザードマップと内水浸水想定の前提・限界
- データセットの出所、更新日、利用制約
- `safety_guardrails.txt`

## 収録済み（2026-09-25）

- `region_background.md`: 中延・二葉の地域の背景（立会川の谷と暗渠、水害の歴史、R7.9.11の大雨、整備水準）。出典付き
- 町丁目ごとの数値は `../02_processed/town_facts/town_facts.json`（`tools/build_town_facts.py` で生成）
