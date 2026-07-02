#!/usr/bin/env python3
import csv
from collections import defaultdict

import rq1_llm_only_baseline as base

SCRIPT_DIR = base.SCRIPT_DIR
GT_PATH = base.GT_PATH
SCORER_PATHS = {
    "sonar": SCRIPT_DIR / "sonar_scores.jsonl",
    "gemini": SCRIPT_DIR / "llm_scores_gemini.jsonl",
    "claude": SCRIPT_DIR / "llm_scores_claude.jsonl",
}
SCORER_LABELS = {"sonar": "SONAR", "gemini": "Gemini 3.1 Pro", "claude": "Claude Opus 4.8"}
SCORERS = ["sonar", "gemini", "claude"]

DIMS = ["correctness", "abstraction", "conciseness"]
DIM_LABELS = {"correctness": "Correctness", "abstraction": "Abstraction", "conciseness": "Conciseness"}


def main():
    data_rows = base._load_groundtruth(GT_PATH)

    scores_by_dim = {}
    for name, path in SCORER_PATHS.items():
        by_dim = defaultdict(dict)
        for rec in base._load_jsonl(path):
            by_dim[rec["dim"]][rec["summary_id"]] = rec["score"]
        scores_by_dim[name] = by_dim

    per_dim = {dim: {"n": 0, **{s: 0 for s in SCORERS}} for dim in DIMS}

    for r in data_rows:
        dim, gt = r["dimension"], r["ground_truth"]
        if dim not in per_dim:
            continue
        stats = per_dim[dim]
        stats["n"] += 1

        id_a, id_b = r["id_a"], r["id_b"]
        for name in SCORERS:
            by_dim = scores_by_dim[name][dim]
            v_a = by_dim.get(id_a)
            v_b = by_dim.get(id_b)
            if v_a is not None and v_b is not None and v_a != v_b and ("A" if v_a > v_b else "B") == gt:
                stats[name] += 1

    overall = {"n": 0, **{s: 0 for s in SCORERS}}
    for dim in DIMS:
        for k, v in per_dim[dim].items():
            overall[k] += v

    def pct(name, dim_stats):
        return round(100 * dim_stats[name] / dim_stats["n"]) if dim_stats["n"] else 0

    columns = DIMS + ["overall"]
    col_stats = {**per_dim, "overall": overall}
    col_labels = [DIM_LABELS[d] for d in DIMS] + ["Overall"]

    col_w = 12
    print(f"{'Scorer':<16}" + "".join(f"{label:>{col_w}}" for label in col_labels))
    print(f"{'n':<16}" + "".join(f"{col_stats[c]['n']:>{col_w}}" for c in columns))
    for name in SCORERS:
        print(f"{SCORER_LABELS[name]:<16}" +
              "".join(f"{pct(name, col_stats[c]):>{col_w}}" for c in columns))

    csv_path = SCRIPT_DIR.parents[0] / "results" / "agreement_table.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Scorer"] + col_labels)
        writer.writerow(["n"] + [col_stats[c]["n"] for c in columns])
        for name in SCORERS:
            writer.writerow([SCORER_LABELS[name]] + [pct(name, col_stats[c]) for c in columns])
    print(f"\n[+] CSV written to {csv_path}")


if __name__ == "__main__":
    main()
