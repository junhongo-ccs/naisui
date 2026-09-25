"""Write per-town RAG Markdown files for Dify from town_facts.json.

町丁目ごとの事実（tools/build_town_facts.py の town_facts.json）を、Difyのナレッジに取り込みやすい
チャンク単位のMarkdownにする。1チャンク＝1つの話題で、見出しと1行目に町丁目名と話題を必ず書く
（検索で単独で取り出されても意味が通るようにする）。チャンクの中に空行を入れず、チャンクの間を
空行1つで区切るので、Difyの既定の区切り（\\n\\n）でそのまま分割できる。

地域の背景（01_地域の背景.md）と用語の説明（03_用語とデータの説明.md）は手で書いた固定の文書で、
このスクリプトは作らない。

出力（既定では リポジトリ直下の RAG/）:
  02_町丁目_<町丁目名>.md  10町丁目分
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


CAVEAT = "（雨水がたまりやすい場所は、校正前の試算で、実際の浸水予報ではない。避難の判断は品川区・気象庁などの公式情報による）"
# 1989〜2020年の累計のうち、平成11年8月29日の集中豪雨1回が占める割合（区の町丁別浸水実績一覧から算出。
# docs/03_モデル検証/中延二葉_モデル実績照合レビュー.md 2.1節）。記載の無い町丁目は述べない。
H11_SHARE = {
    "二葉四丁目": 0.974, "中延三丁目": 0.889, "二葉二丁目": 0.880, "二葉一丁目": 0.850,
    "二葉三丁目": 0.824, "中延五丁目": 0.760, "中延二丁目": 0.667, "中延六丁目": 0.619,
}


def pct(value: float, digits: int = 0) -> str:
    return f"{value * 100:.{digits}f}%"


def pattern_of(facts: dict) -> tuple[str, str]:
    culvert = facts["culvert"]
    if culvert["passes_through_town"]:
        return "A", "立会川の暗渠が町内を通り、その片側が谷底になっている町"
    if culvert["distance_from_town_m"] <= 150:
        return "B", "立会川の暗渠に近いが、一段高い台地の上にある町"
    return "C", "立会川の暗渠から離れた台地の上の町"


def valley_side(facts: dict) -> dict | None:
    sides = facts["culvert"].get("sides", [])
    if not sides:
        return None
    return max(sides, key=lambda side: (side["share_of_town_official_hazard"] + side["share_of_town_ponding"]))


def chunk_overview(facts: dict) -> str:
    town = facts["town"]
    code, label = pattern_of(facts)
    culvert = facts["culvert"]
    records = facts["records"]
    history = records["history_1989_2020_buildings"]
    history_text = f"{history}棟" if history is not None else "区の原典で0棟"
    if culvert["passes_through_town"]:
        culvert_text = f"立会川の暗渠（上部は立会道路）が町内を約{culvert['length_in_town_m']}m通る。"
    else:
        culvert_text = f"立会川の暗渠（立会道路）は町内を通らず、町から約{culvert['distance_from_town_m']}m離れている。"
    return "\n".join([
        f"## {town}の概要（地形のパターン{code}）",
        f"{town}は、{label}である。{culvert_text}",
        f"標高は最低{facts['elevation_m']['min']}m・中央{facts['elevation_m']['median']}m・最高{facts['elevation_m']['max']}m。",
        f"令和7年9月11日の大雨で区に報告された浸水は{records['r7_0911_class']}、1989〜2020年の累計の浸水は{history_text}。",
        f"公式の浸水想定区域（1時間153mm・24時間690mmの大雨）は町の面積の{pct(facts['official_hazard']['share_of_town'], 1)}。",
    ])


def chunk_culvert(facts: dict) -> str | None:
    town = facts["town"]
    side = valley_side(facts)
    if side is None:
        return None
    other = next((s for s in facts["culvert"]["sides"] if s is not side), None)
    no_hazard = facts["official_hazard"]["share_of_town"] == 0
    hazard_text = "" if no_hazard else f"、公式の浸水想定区域の{pct(side['share_of_town_official_hazard'])}"
    lines = [
        f"## {town}の地形と立会川の暗渠",
        f"{town}では、立会川の暗渠の{side['direction']}側に、雨水がたまりやすい場所の{pct(side['share_of_town_ponding'])}{hazard_text}がある"
        f"（{side['direction']}側は町の面積の{pct(side['share_of_town_area'])}）。" + ("町内に公式の浸水想定区域はない。" if no_hazard else ""),
    ]
    for band in side["bands"]:
        lines.append(
            f"暗渠の{side['direction']}側{band['from_m']}〜{band['to_m']}m: 標高{band['elevation_median_m']}m、"
            f"雨水がたまりやすい{pct(band['ponding_share'], 1)}、浸水想定{pct(band['official_hazard_share'], 1)}。"
        )
    if other and other["bands"]:
        highest = max(other["bands"], key=lambda band: band["elevation_median_m"])
        lines.append(
            f"反対の{other['direction']}側は、暗渠から{highest['from_m']}〜{highest['to_m']}mで標高{highest['elevation_median_m']}mまで高くなり、"
            f"雨水がたまりやすい場所の{pct(other['share_of_town_ponding'])}、浸水想定区域の{pct(other['share_of_town_official_hazard'])}しかない。"
        )
    elif other:
        lines.append(f"暗渠の{other['direction']}側には、町の面積がほとんどない。")
    return "\n".join(lines)


def chunk_no_culvert(facts: dict) -> str | None:
    if facts["culvert"]["passes_through_town"]:
        return None
    town = facts["town"]
    terrain = facts["terrain"]
    return "\n".join([
        f"## {town}の地形（暗渠からの距離とくぼ地）",
        f"{town}は立会川の暗渠から約{facts['culvert']['distance_from_town_m']}m離れた、標高{facts['elevation_m']['min']}〜{facts['elevation_m']['max']}mの土地にある。",
        f"深さ0.1m以上のくぼ地は町の面積の{pct(terrain['depression_share_of_town'], 1)}（{terrain['depression_count_2cells_or_more']}か所）で、"
        f"くぼ地の深さの上位5%値は{terrain['depression_depth_p95_m']}m。",
        f"雨水がたまりやすい場所は町の面積の{pct(facts['ponding']['share_of_town'], 1)}で、その{pct(terrain['ponding_in_depressions_share'])}がくぼ地にある。",
    ])


def chunk_ponding_places(facts: dict) -> str:
    town = facts["town"]
    lines = [
        f"## {town}で雨水がたまりやすい場所",
        f"{town}で雨水がたまりやすい場所（試算で最大の深さ0.1m以上）は{facts['ponding']['area_m2']:,}m²で、町の面積の{pct(facts['ponding']['share_of_town'], 1)}。"
        f"深さの上位5%値は{facts['ponding']['depth_p95_m']}m。",
    ]
    for road in [road for road in facts["roads"] if road["share_of_town_ponding"] >= 0.05][:3]:
        lower = road["lower_than_surroundings_m"]
        relief = "" if lower is None else (f"沿道は周りより{lower:.2f}m低い。" if lower > 0 else f"沿道は周りより{-lower:.2f}m高い。")
        hazard = (
            f"沿道の{pct(road['official_hazard_share_of_corridor'])}が公式の浸水想定区域（{'・'.join(road['official_hazard_classes'])}）に入る。"
            if road["official_hazard_classes"]
            else "沿道に公式の浸水想定区域はない。"
        )
        lines.append(
            f"{road['road']}沿い（町内約{road['length_in_town_m']}m、両側10m）に、町内のたまりやすい面積の{pct(road['share_of_town_ponding'])}がある。{relief}{hazard}"
        )
    off = facts["off_road_ponding"]
    for cluster in off["largest"][:2]:
        if cluster["share_of_town_ponding"] < 0.1:
            continue
        lines.append(
            f"名前の付いた通りから外れた町の{cluster['direction_in_town']}側（{cluster['nearest_named_road']}から約{cluster['nearest_named_road_m']}m）に、"
            f"たまりやすい面積の{pct(cluster['share_of_town_ponding'])}がまとまっている。"
        )
    lines.append(CAVEAT)
    return "\n".join(lines)


def chunk_official_hazard(facts: dict) -> str:
    town = facts["town"]
    hazard = facts["official_hazard"]
    classes = "、".join(f"{name} {pct(share, 1)}" for name, share in hazard["share_by_depth_class"].items()) or "なし"
    return "\n".join([
        f"## {town}の公式の浸水想定区域",
        f"{town}のうち、東京都の雨水出水浸水想定区域図（1時間153mm・24時間690mmの想定最大規模の大雨）で浸水が想定される区域は、町の面積の{pct(hazard['share_of_town'], 1)}。",
        f"深さの区分ごとの面積割合: {classes}。",
        f"雨水がたまりやすい場所（試算）のうち、公式の浸水想定区域と重なるのは{pct(facts['ponding_in_official_hazard']['share_of_ponding'])}。",
        "公式の浸水想定区域は、公式PDFの地図を位置合わせして作った派生データで、位置に数m程度の誤差がある。",
    ])


def chunk_records(facts: dict) -> str:
    town = facts["town"]
    records = facts["records"]
    history = records["history_1989_2020_buildings"]
    lines = [f"## {town}の過去の浸水実績"]
    lines.append(
        f"令和7年9月11日の大雨（品川区付近で1時間約120ミリ）で、{town}では{records['r7_0911_class']}の浸水が区に報告された"
        + ("（地図の判読が不確かで未確定）。" if records["r7_0911_confidence"] == "uncertain" else "。")
    )
    if history is None:
        lines.append(f"1989年から2020年3月までの累計では、{town}の浸水は区の原典で0棟である。")
    else:
        lines.append(
            f"1989年から2020年3月までの累計では、{town}で{history}棟（うち床上{records['history_1989_2020_abovefloor']}棟）が浸水した。"
            + (f"このうち{pct(H11_SHARE[town])}は平成11年8月29日の集中豪雨（1時間77ミリ）1回によるもの。" if town in H11_SHARE else "")
        )
    return "\n".join(lines)


def chunk_special(facts: dict) -> str | None:
    town = facts["town"]
    lines = []
    for underpass in facts.get("underpasses", []):
        lines.append(
            f"{town}には、線路の下をくぐる道路トンネル「{underpass['name']}」がある。地形データでは出入口の坂が周りより最大{underpass['depression_depth_max_m']}m低く、"
            "線路の下をくぐる低い道路は大雨のときに注意が必要な場所である。"
        )
    for note in facts.get("field_notes", []):
        lines.append(f"確認事項（{note['confirmed_on']}）: {note['note']}。")
    if not lines:
        return None
    return "\n".join([f"## {town}の注意点（アンダーパス・地形データの注意）", *lines])


def chunk_facilities(facts: dict) -> str:
    town = facts["town"]
    facilities = facts["facilities"]
    shelters = "、".join(facilities["shelters_in_town"]) or "なし"
    sandbags = "、".join(facilities["sandbags_in_town"]) or "なし"
    return "\n".join([
        f"## {town}の避難所と土のう置場",
        f"{town}の町内の避難所: {shelters}。最寄りの避難所は{facilities['nearest_shelter']['name']}（町の中心から約{facilities['nearest_shelter']['distance_m']}m）。",
        f"{town}の町内の土のう置場: {sandbags}。最寄りの土のう置場は{facilities['nearest_sandbag']['name']}（町の中心から約{facilities['nearest_sandbag']['distance_m']}m）。",
        "避難所の開設状況は、品川区の公式情報で確認する。",
    ])


def town_markdown(facts: dict, generated_at: str) -> str:
    chunks = [
        f"# {facts['town']}（品川区）の雨水のたまりやすさに関する事実\n"
        f"データから機械的に作成（{generated_at}、tools/build_rag_markdown.py）。出典と前提は「03_用語とデータの説明」を参照。",
        chunk_overview(facts),
        chunk_culvert(facts),
        chunk_no_culvert(facts),
        chunk_ponding_places(facts),
        chunk_official_hazard(facts),
        chunk_records(facts),
        chunk_special(facts),
        chunk_facilities(facts),
    ]
    return "\n\n".join(chunk for chunk in chunks if chunk) + "\n"


def run(args: argparse.Namespace) -> None:
    data = json.loads(args.facts.read_text(encoding="utf-8"))
    generated_at = data["metadata"]["generated_at"][:10]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    longest = 0
    for facts in data["towns"]:
        text = town_markdown(facts, generated_at)
        longest = max(longest, *(len(chunk) for chunk in text.split("\n\n")))
        (args.output_dir / f"02_町丁目_{facts['town']}.md").write_text(text, encoding="utf-8")
    print(f"Wrote {len(data['towns'])} town files to {args.output_dir} (longest chunk {longest} chars)")


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--facts", type=Path, default=root / "data/naisui_poc/02_processed/town_facts/town_facts.json")
    parser.add_argument("--output-dir", type=Path, default=root / "RAG")
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
