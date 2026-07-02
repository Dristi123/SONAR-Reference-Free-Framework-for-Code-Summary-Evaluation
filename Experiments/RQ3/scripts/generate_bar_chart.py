#!/usr/bin/env python3
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
IN_PATH = SCRIPT_DIR / "common_pool_for_all_prompting.jsonl"
OUT_PATH = SCRIPT_DIR.parent / "results" / "bar_chart.png"

DIMS = ["correctness", "abstraction", "conciseness", "fluency"]
STRATS = ["Vanilla", "dim_aware", "few_shot"]
LABELS = {"Vanilla": "Vanilla-Prompting", "dim_aware": "Dimension-Aware Prompting",
          "few_shot": "Few-shot prompting"}
COLORS = {"Vanilla": "#A8D8FF", "dim_aware": "#FFAFAF", "few_shot": "#B5E8B8"}


def load_rows() -> list:
    with open(IN_PATH) as f:
        return [json.loads(line) for line in f]


def strategy_means(rows: list) -> dict:
    by_dim_strat = {d: {s: [] for s in STRATS} for d in DIMS}
    for r in rows:
        s = r["strategy"]
        for d in DIMS:
            v = r.get(d)
            if v is not None:
                by_dim_strat[d][s].append(v)

    means = {d: {} for d in DIMS}
    for d in DIMS:
        for s in STRATS:
            vals = by_dim_strat[d][s]
            means[d][s] = sum(vals) / len(vals) if vals else 0.0
    return means


def draw_bar_chart(means: dict):
    x = np.arange(len(DIMS))
    width = 0.15
    spacing = 0.2

    all_vals = [means[d][s] for d in DIMS for s in STRATS]
                                                                                     
    floor = max(0.0, min(all_vals) - 0.05)
    ceiling = min(1.0, max(all_vals) + 0.08)

    plt.rcParams["font.family"] = "DejaVu Sans"

    fig, ax = plt.subplots(figsize=(3.4, 2.8))
    for i, s in enumerate(STRATS):
        vals = [means[d][s] for d in DIMS]
        offset = (i - 1) * spacing
        bars = ax.bar(x + offset, vals, width, label=LABELS[s], color=COLORS[s],
                      edgecolor="black", linewidth=0.4)
        ax.bar_label(bars, fmt="%.2f", fontsize=4, padding=1)

    ax.set_xticks(x)
    ax.set_xticklabels([d.capitalize() for d in DIMS], fontsize=6, fontweight="bold")
    ax.tick_params(axis="y", labelsize=6)
    ax.set_ylim(floor, ceiling)
    for spine in ax.spines.values():
        spine.set_color("#888888")
        spine.set_linewidth(0.7)
    ax.legend(fontsize=5, loc="lower center", bbox_to_anchor=(0.5, 1.0),
              ncol=3, framealpha=0.85, columnspacing=0.8, handlelength=1.2)
    fig.tight_layout()

    fig.savefig(OUT_PATH, dpi=300)
    plt.close(fig)
    print(f"Saved -> {OUT_PATH}  (y-axis zoomed to [{floor:.2f}, {ceiling:.2f}])")


def main():
    rows = load_rows()
    means = strategy_means(rows)
    for d in DIMS:
        scores = "  ".join(f"{s}={means[d][s]:.3f}" for s in STRATS)
        print(f"{d.capitalize():<14}{scores}")
    draw_bar_chart(means)


if __name__ == "__main__":
    main()
