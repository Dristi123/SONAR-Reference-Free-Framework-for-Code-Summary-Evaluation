import csv
import warnings
from collections import defaultdict
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

SCRIPT_DIR = Path(__file__).resolve().parent
RESULTS_DIR = SCRIPT_DIR.parent / "results"
DIMS = ["correctness", "conciseness", "abstraction"]
N_BOOT = 10_000
ROWS = [("Repeated Runs", "Run 1", ("default", "0")), ("Repeated Runs", "Run 2", ("default", "1")),
        ("Decoding Parameters", "Temp. = 0", ("T0.0", "0")), ("Decoding Parameters", "Temp. = 0.5", ("T0.5", "0")),
        ("Decoding Parameters", "Temp. = (0.2, 0.5, 0.8)", ("set_low", "0")),
        ("Decoding Parameters", "Temp. = (0.8, 1.0, 1.2)", ("set_high", "0")),
        ("Decoding Parameters", "Top-p = 0.5", ("P0.5", "0")), ("Decoding Parameters", "Top-p = 0.8", ("P0.8", "0")),
        ("Model Selection", "G: Qwen", ("G_qwen", "")), ("Model Selection", "G: OLMo", ("G_olmo", "")),
        ("Model Selection", "P: Qwen", ("P_qwen", "")), ("Model Selection", "P: OLMo", ("P_olmo", "")),
        ("Model Selection", "Gemini -> Kimi K2.5", ("swap_gemini_to_kimi", "1")),
        ("Model Selection", "Qwen -> Codestral-22B", ("swap_qwen_to_codestral", "1")),
        ("Model Selection", "OLMo -> GLM-4-32B", ("swap_olmo_to_glm", "1")),
        ("Model Selection", "All three replaced (Kimi, Codestral, GLM)", ("swap_all", "1")),
        ("Pool Size", "V = 2 (6 implementations)", ("pool_6", "1")),
        ("Pool Size", "V = 1 (3 implementations)", ("pool_3", "1")),
        ("Context-Only", "Empty summary", None)]


def fmt(x):
    return str(Decimal(f"{x:.4f}").quantize(Decimal("0.001"), ROUND_HALF_UP))


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def mad_spearman(pairs):
    a, b = np.array([p[0] for p in pairs], float), np.array([p[1] for p in pairs], float)
    rng = np.random.default_rng(0)
    rhos = np.empty(N_BOOT)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for k in range(N_BOOT):
            pick = rng.integers(len(a), size=len(a))
            x, y = a[pick], b[pick]
            rhos[k] = spearmanr(x, y)[0] if x.std() and y.std() else np.nan
    lo, hi = np.nanpercentile(rhos, [2.5, 97.5])
    return {"mad": np.abs(a - b).mean(), "spearman": spearmanr(a, b)[0], "ci": (lo, hi)}


def main():
    scores, sample = defaultdict(dict), {}
    for r in read_csv(SCRIPT_DIR / "sensitivity_scores.csv"):
        scores[r["dimension"], r["setting"], r["run"]][r["summary_id"]] = float(r["score"])
        if r["sample_rank"]:
            sample[r["summary_id"]] = int(r["sample_rank"])
    sample = sorted(sample, key=sample.get)
    selection = defaultdict(list)
    for r in read_csv(SCRIPT_DIR / "model_selection_scores.csv"):
        if r["alternative"]:
            selection[r["dimension"], r["setting"]].append((float(r["original"]), float(r["alternative"])))
    empty = defaultdict(list)
    for r in read_csv(SCRIPT_DIR / "empty_summary_scores.csv"):
        empty[r["dimension"]].append((float(r["reported"]), float(r["empty_summary"])))

    table = []
    for factor, label, key in ROWS:
        row = {"factor": factor, "configuration": label}
        for d in DIMS:
            if key is None:
                cell = mad_spearman(empty[d])
            elif key[0].startswith(("G_", "P_")):
                if (d, key[0]) not in selection:
                    continue
                cell = mad_spearman(selection[d, key[0]])
            elif (d, *key) in scores:
                got = scores[(d, *key)]
                if key[0].startswith("pool_"):
                    base = scores[d, "pool_9", key[1]]
                else:
                    base = scores[d, "reported", ""]
                cell = mad_spearman([(base[i], got[i]) for i in sample if i in got and i in base])
            else:
                continue
            row[f"{d}_mad"] = fmt(cell["mad"])
            row[f"{d}_spearman"] = fmt(cell["spearman"])
            row[f"{d}_spearman_95ci"] = f"[{fmt(cell['ci'][0])}, {fmt(cell['ci'][1])}]"
        table.append(row)

    header = ["factor", "configuration"] + [f"{d}_{c}" for d in DIMS for c in
                                             ("mad", "spearman", "spearman_95ci")]
    RESULTS_DIR.mkdir(exist_ok=True)
    with open(RESULTS_DIR / "sensitivity_table.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, header)
        w.writeheader()
        w.writerows(table)


if __name__ == "__main__":
    main()
