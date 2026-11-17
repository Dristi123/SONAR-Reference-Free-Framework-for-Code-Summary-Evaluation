import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

SCRIPT_DIR = Path(__file__).resolve().parent
RESULTS_DIR = SCRIPT_DIR.parent / "results"
RQ1_DIR = SCRIPT_DIR.parents[2] / "RQ1" / "scripts"
DIMENSIONS = ["correctness", "abstraction", "conciseness"]
BLUES = LinearSegmentedColormap.from_list("blues", ["#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"])
INK, INK_ON_DARK = "#1f1f1e", "#ffffff"


def preference(a, b):
    if a is None or b is None or a == b:
        return "tie"
    return "A" if a > b else "B"


def plot(confusions):
    sonar_labels = ["A", "B"] + (["tie"] if any(c[h, "tie"] for c, _ in confusions.values() for h in "AB") else [])
    fig, axes = plt.subplots(1, len(confusions), figsize=(3.2 * len(confusions), 3.0))
    plt.rcParams["font.family"] = "DejaVu Sans"
    for ax, (dim, (counts, agreement)) in zip(axes, confusions.items()):
        grid = [[counts[h, s] for s in sonar_labels] for h in "AB"]
        top = max(max(row) for row in grid)
        ax.imshow(grid, cmap=BLUES, vmin=0, vmax=top)
        for i, row in enumerate(grid):
            for j, value in enumerate(row):
                ax.text(j, i, value, ha="center", va="center", fontsize=13,
                        color=INK_ON_DARK if value > 0.55 * top else INK)
        ax.set_xticks(range(len(sonar_labels)), [f"SONAR: {s}" for s in sonar_labels], fontsize=9, color=INK)
        ax.set_yticks(range(2), ["Human: A", "Human: B"], fontsize=9, color=INK)
        ax.set_title(f"{dim.capitalize()} ({agreement}% agreement)", fontsize=10, color=INK)
        ax.tick_params(length=0)
        for spine in ax.spines.values():
            spine.set_visible(False)
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "confusion_matrices.png", dpi=300, facecolor="white")
    plt.close(fig)


def main():
    csv.field_size_limit(10 ** 8)
    with open(RQ1_DIR / "groundtruth.csv", newline="", encoding="utf-8") as f:
        pairs = list(csv.DictReader(f))
    with open(RQ1_DIR / "sonar_scores.jsonl", encoding="utf-8") as f:
        scores = {(r["summary_id"], r["dim"]): r["score"] for r in map(json.loads, f) if r}

    rows, confusions = [], {}
    for dim in DIMENSIONS:
        counts = {(h, s): 0 for h in "AB" for s in ("A", "B", "tie")}
        for p in pairs:
            if p["dimension"] == dim:
                sonar = preference(scores.get((p["id_a"], dim)), scores.get((p["id_b"], dim)))
                counts[p["ground_truth"], sonar] += 1
        n_a = sum(counts["A", s] for s in ("A", "B", "tie"))
        n_b = sum(counts["B", s] for s in ("A", "B", "tie"))
        agree = counts["A", "A"] + counts["B", "B"]
        confusions[dim] = (counts, f"{100 * agree / (n_a + n_b):.1f}")
        rows.append({
            "dimension": dim.capitalize(), "pairs": n_a + n_b,
            "human_A": n_a, "human_B": n_b,
            "human_A_sonar_A": counts["A", "A"], "human_A_sonar_B": counts["A", "B"], "human_A_sonar_tie": counts["A", "tie"],
            "human_B_sonar_B": counts["B", "B"], "human_B_sonar_A": counts["B", "A"], "human_B_sonar_tie": counts["B", "tie"],
            "agreement": f"{100 * agree / (n_a + n_b):.1f}",
            "balanced_agreement": f"{50 * (counts['A', 'A'] / n_a + counts['B', 'B'] / n_b):.1f}",
            "majority_label_baseline": f"{100 * max(n_a, n_b) / (n_a + n_b):.1f}",
        })

    RESULTS_DIR.mkdir(exist_ok=True)
    with open(RESULTS_DIR / "label_table.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    plot(confusions)


if __name__ == "__main__":
    main()
