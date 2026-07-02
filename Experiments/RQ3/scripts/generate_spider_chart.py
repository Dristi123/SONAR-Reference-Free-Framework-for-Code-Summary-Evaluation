#!/usr/bin/env python3
import json
import math
from pathlib import Path

import matplotlib.pyplot as plt

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_PATH = SCRIPT_DIR / "vanilla_scores.jsonl"
OUT_PATH = SCRIPT_DIR.parent / "results" / "spider_chart.png"

BIG_MODELS = ["gemini", "kimi", "olmo", "qwen"]
SMALL_MODELS = ["codegemma", "codellama", "codestral", "mistral"]
SMALLER_MODELS = ["codet5_sum", "phi35_mini", "starcoder2"]
ALL_MODELS = BIG_MODELS + SMALL_MODELS + SMALLER_MODELS

DIMS = ["correctness", "abstraction", "conciseness", "fluency"]

COLORS = ['#2196F3', '#F44336', '#4CAF50', '#FF9800', '#9C27B0', '#00BCD4',
          '#795548', '#607D8B', '#E91E63', '#3F51B5', '#009688']

STYLES = ['-'] * 4 + ['--'] * 4 + [':'] * 3
MARKERS = ['o', 's', '^', 'D', 'v', 'P', 'X', '*', 'h', 'p', '<']
LEGEND_FONTSIZE = 17


def load_setting() -> tuple:
    means = {}
    corpus_values = {d: [] for d in DIMS}
    with open(DATA_PATH) as f:
        rows = [json.loads(l) for l in f]
    bucket = {}
    for r in rows:
        m = r.get("model")
        if not m:
            continue
        if m not in bucket:
            bucket[m] = {d: [] for d in DIMS}
        for d in DIMS:
            v = r.get(d)
            if v is not None:
                try:
                    fv = float(v)
                except (ValueError, TypeError):
                    continue
                bucket[m][d].append(fv)
                corpus_values[d].append(fv)
    for m, dim_vals in bucket.items():
        means[m] = {d: (sum(vs) / len(vs) if vs else 0.0) for d, vs in dim_vals.items()}
    return means, corpus_values


def normalize_means(means: dict, corpus_values: dict) -> dict:
    normalized = {model: {} for model in means}
    for dim in DIMS:
        low = min(corpus_values[dim])
        high = max(corpus_values[dim])
        span = high - low
        for model in means:
            normalized[model][dim] = 0.0 if span == 0 else (means[model][dim] - low) / span
    return normalized


def draw_spider(means: dict):
    n = len(DIMS)
    angles = [2 * math.pi * i / n for i in range(n)]
    angles_closed = angles + angles[:1]

    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection="polar")

    ax.set_theta_offset(math.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_thetagrids([math.degrees(a) for a in angles], [''] * n)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(['0.25', '0.50', '0.75', '1.00'], fontsize=11, color='grey')

    for theta, dim in zip(angles, DIMS):
        display_angle = math.pi / 2 - theta
        cos_a, sin_a = math.cos(display_angle), math.sin(display_angle)

        if cos_a > 0.3:
            ha = 'left'
        elif cos_a < -0.3:
            ha = 'right'
        else:
            ha = 'center'

        if sin_a > 0.3:
            va = 'bottom'
        elif sin_a < -0.3:
            va = 'top'
        else:
            va = 'center'

        ax.text(theta, 1.12, dim.capitalize(), ha=ha, va=va,
                 fontsize=LEGEND_FONTSIZE, fontstyle='italic', fontweight='bold')

    for model, color, ls, marker in zip(ALL_MODELS, COLORS, STYLES, MARKERS):
        if model not in means:
            continue
        vals = [means[model][d] for d in DIMS]
        vals = vals + [vals[0]]
        lw = 2.5 if ls == '-' else 1.8
        ax.plot(angles_closed, vals, color=color, linewidth=lw, linestyle=ls,
                marker=marker, markersize=7, markerfacecolor=color,
                markeredgecolor='white', markeredgewidth=0.6, label=model.capitalize())

    ax.legend(loc='upper left', bbox_to_anchor=(1.0, 1.18),
              fontsize=LEGEND_FONTSIZE, framealpha=0.8)

    fig.savefig(OUT_PATH, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved -> {OUT_PATH}")


def main():
    means, corpus_values = load_setting()

    for m in ALL_MODELS:
        if m in means:
            scores = '  '.join(f"{d}={means[m][d]:.3f}" for d in DIMS)
            print(f"  {m:12s}: {scores}")
        else:
            print(f"  {m:12s}: MISSING")

    for d in DIMS:
        print(f"  corpus {d}: min={min(corpus_values[d]):.3f} max={max(corpus_values[d]):.3f} (n={len(corpus_values[d])})")

    draw_spider(normalize_means(means, corpus_values))


if __name__ == "__main__":
    main()
