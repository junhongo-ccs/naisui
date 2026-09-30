# LLM知識ベース

DifyまたはChatGPTが参照する、防災情報・データ出所・モデルの前提条件を保存する。計算結果そのものは保存せず、結果は構造化データベースまたはGIS APIから取得する。

収録候補:

- 品川区の公式避難・防災情報
- ハザードマップと内水浸水想定の前提・限界
- データセットの出所、更新日、利用制約
- `safety_guardrails.txt`

## 収録済み（2026-09-25）

- `region_background.md`: 中延・二葉の地域の背景（立会川の谷と暗渠、水害の歴史、R7.9.11の大雨、整備水準）。出典付き
- `dify_llm_prompt.md`: DifyチャットフローのLLMノードのSYSTEMに貼る中身（2026-09-28）。ファイル全体をそのまま貼る。`safety_guardrails.md` を見直し後の前提とJSON契約に合わせたもの
- `dify_chatflow_setup.md`: チャットフローの構成、入力変数、モデル設定、SYSTEMの貼り方と確かめ方、USERの中身（2026-09-30に `dify_llm_prompt.md` から分けた）
- 町丁目ごとの数値は `../02_processed/town_facts/town_facts.json`（`tools/build_town_facts.py` で生成）
