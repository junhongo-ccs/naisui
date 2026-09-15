# 町丁目境界データ

ここには、令和2年国勢調査の小地域（町丁・字等）境界データを置きます。

- 想定ファイル名: `shinagawa_town_2020.geojson`
- 対象: 東京都品川区（標準地域コード 13109）
- 必要な属性: 町丁目名（e-Stat Shape形式では通常 `S_NAME`。実データで確認すること）
- 出典: e-Stat「令和2年国勢調査 町丁・字等境界データ」

元データは加工せず保管し、ファイル名・取得日・ライセンスを併記してください。`tools/export_risk_lookup.py` はGeoJSON、GeoPackage、Shapefile等を読み込めます。
