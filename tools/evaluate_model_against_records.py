"""Compare model runs against town-level inundation records (before and after normalization).

PLATEAU導入計画 5章の評価設計を実装する。同じDEM・同じ降雨シナリオ・同じ町丁目境界で
実行した複数のモデル結果（risk_lookup JSON）を並べ、次を出力する。

  model_comparison_rank_correlation.csv  各実行×各実績指標のSpearman ρ（平均順位法）
  model_comparison_town_ranks.csv        町丁目別のモデル指標・順位と実績の順位
  model_comparison_water_balance.csv     湛水面積・最大深・貯留体積（非現実的な急増・消失の点検用）

実績は tools/count_buildings_by_town.py の出力（inundation_history_normalized.csv）を使う。
n=9〜10のため、ρの小さな差を改善・悪化と判定しない（計画 2.1節）。順位が入れ替わった
町丁目を町丁目別の表で確認すること。
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

from count_buildings_by_town import average_ranks, normalize_town_name, spearman


R7_CLASS_ORDER = ["0件", "1-5件", "6-15件", "16-30件", "31-50件", "51-75件", "76-110件"]
TARGETS = {
    "history_total_buildings": "31年累計 棟数（正規化前）",
    "history_total_rate": "31年累計 率（正規化後）",
    "history_abovefloor_rate": "31年累計 床上率（正規化後）",
    "r7_class": "R7.9.11 階級（正規化前）",
    "r7_rate_lower": "R7.9.11 率（正規化後、階級下限）",
}


def read_records(path: Path) -> dict[str, dict[str, float]]:
    series: dict[str, dict[str, float]] = {key: {} for key in TARGETS}
    with path.open(encoding="utf-8") as file:
        for row in csv.DictReader(file):
            town = row["town"]
            for key in ("history_total_buildings", "history_total_rate", "history_abovefloor_rate", "r7_rate_lower"):
                if row.get(key):
                    series[key][town] = float(row[key])
            if row.get("r7_class_label"):
                if row["r7_class_label"] not in R7_CLASS_ORDER:
                    raise ValueError(f"Unknown R7.9.11 class: {row['r7_class_label']}")
                series["r7_class"][town] = float(R7_CLASS_ORDER.index(row["r7_class_label"]))
    return series


def read_run(label: str, lookup_path: Path, metric: str) -> dict[str, object]:
    lookup = json.loads(lookup_path.read_text(encoding="utf-8"))
    towns = {normalize_town_name(name): float(values[metric]) for name, values in lookup["towns"].items()}
    summary_path = lookup_path.parent / "water_balance_summary.csv"
    water: dict[str, float] = {}
    if summary_path.exists():
        with summary_path.open(encoding="utf-8") as file:
            steps = list(csv.DictReader(file))
        water = {
            "peak_stored_volume_m3": max(float(step["stored_volume_m3"]) for step in steps),
            "peak_ponded_area_m2": max(float(step["ponded_area_m2"]) for step in steps),
            "peak_maximum_depth_m": max(float(step["maximum_depth_m"]) for step in steps),
        }
    return {"label": label, "scenario_id": lookup.get("scenario_id", ""), "towns": towns, "water": water}


def run(args: argparse.Namespace) -> None:
    if len(args.labels) != len(args.risk_lookup):
        raise ValueError("--labels and --risk-lookup must have the same length.")
    records = read_records(args.records)
    runs = [read_run(label, path, args.metric) for label, path in zip(args.labels, args.risk_lookup)]
    scenario_ids = {run_["scenario_id"] for run_ in runs}
    if len(scenario_ids) > 1:
        raise ValueError(f"Compare runs of the same rainfall scenario only: {sorted(scenario_ids)}")
    args.output_dir.mkdir(parents=True, exist_ok=True)

    correlation_rows = []
    for run_ in runs:
        for key, description in TARGETS.items():
            rho, n, note = spearman(run_["towns"], records[key])  # type: ignore[arg-type]
            correlation_rows.append({
                "run": run_["label"], "target": key, "description": description, "n": n,
                "spearman_rho": "" if rho is None else round(rho, 4), "note": note,
            })
    write_csv(args.output_dir / "model_comparison_rank_correlation.csv", correlation_rows)

    all_towns = sorted({town for run_ in runs for town in run_["towns"]})  # type: ignore[union-attr]
    record_ranks = {key: average_ranks(values) for key, values in records.items() if values}
    town_rows = []
    for town in all_towns:
        row: dict[str, object] = {"town": town}
        for key in ("history_total_rate", "r7_class"):
            row[f"record_rank_{key}"] = record_ranks.get(key, {}).get(town, "")
        for run_ in runs:
            values = run_["towns"]  # type: ignore[assignment]
            ranks = average_ranks(values)
            row[f"{run_['label']}_{args.metric}"] = round(values.get(town, math.nan), 6)
            row[f"{run_['label']}_rank"] = ranks.get(town, "")
        town_rows.append(row)
    write_csv(args.output_dir / "model_comparison_town_ranks.csv", town_rows)

    water_rows = [{"run": run_["label"], **run_["water"]} for run_ in runs if run_["water"]]  # type: ignore[dict-item]
    if water_rows:
        write_csv(args.output_dir / "model_comparison_water_balance.csv", water_rows)

    print(f"Compared {len(runs)} runs of {scenario_ids.pop()} -> {args.output_dir}")
    header = f"{'run':<28}" + "".join(f"{key:>26}" for key in TARGETS)
    print(header)
    for run_ in runs:
        cells = [row for row in correlation_rows if row["run"] == run_["label"]]
        print(f"{run_['label']:<28}" + "".join(f"{str(cell['spearman_rho'] or '-'):>26}" for cell in cells))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[1]
    processed = root / "data/naisui_poc/02_processed"
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--risk-lookup", type=Path, nargs="+", required=True, help="比較するrisk_lookup JSON")
    parser.add_argument("--labels", nargs="+", required=True, help="各risk_lookupの表示名（同じ順）")
    parser.add_argument("--records", type=Path, default=processed / "plateau/inundation_history_normalized.csv")
    parser.add_argument("--metric", default="area_over_threshold_ratio", help="risk_lookup内のモデル指標")
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
