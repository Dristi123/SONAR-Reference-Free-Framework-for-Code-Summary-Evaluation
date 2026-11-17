import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import wilcoxon

SCRIPT_DIR = Path(__file__).resolve().parent
RESULTS_DIR = SCRIPT_DIR.parent / "results"

sys.path.insert(0, str(SCRIPT_DIR.parents[2] / "RQ2" / "scripts"))
from downstream import load_meta  # noqa: E402
from downstream import outcomes as downstream_outcomes  # noqa: E402

TASKS = ["MRR", "Edit Dist.", "Speedup"]
ID_RE = re.compile(r"^(.+)_([a-z0-9_]+?)_(Vanilla|dim_aware|few_shot)_(big_models|small_models)$")


def outcomes():
    rows = downstream_outcomes()
    out = {task: defaultdict(dict) for task in TASKS}
    for task in TASKS:
        for sid, model, value in rows[task]:
            if value is not None:
                out[task][sid][model] = float(value)
    return out


def table(meta, strategy):
    units = defaultdict(dict)
    for sid, r in meta.items():
        m = ID_RE.match(sid)
        if m and r.get("abstraction") is not None:
            units[m.group(1), m.group(2)][m.group(3)] = sid

    rows = []
    for task, values in outcomes().items():
        log = task == "Speedup"
        pairs = []
        for (fn, _), by in units.items():
            if "Vanilla" not in by or strategy not in by:
                continue
            v, g = by["Vanilla"], by[strategy]
            shared = [m for m in values.get(v, {}) if m in values.get(g, {})
                      and (not log or (values[v][m] > 0 and values[g][m] > 0))]
            if not shared:
                continue
            f = np.log if log else (lambda x: x)
            change = float(np.mean([f(values[g][m]) - f(values[v][m]) for m in shared]))
            pairs.append((fn, 100 * (meta[g]["abstraction"] - meta[v]["abstraction"]), change,
                          float(np.mean([values[v][m] for m in shared]))))
        d_abs = np.array([p[1] for p in pairs])
        change = np.array([p[2] for p in pairs])
        pct = 100 * np.expm1(change.mean()) if log else 100 * change.mean() / np.mean([p[3] for p in pairs])
        up = change[d_abs > 0]
        rows.append({"task": task, "pairs": len(pairs), "functions": len({p[0] for p in pairs}),
                     "abstraction_change_pp": round(float(d_abs.mean()), 2), "outcome_change_pct": round(float(pct), 2),
                     "wilcoxon_p": f"{wilcoxon(change).pvalue:.4g}", "pairs_abstraction_up": len(up),
                     "outcome_improved": int((up > 0).sum()), "outcome_tied": int((up == 0).sum()),
                     "outcome_worse": int((up < 0).sum())})
    return rows


def main():
    meta = load_meta()
    RESULTS_DIR.mkdir(exist_ok=True)
    for strategy in ("few_shot", "dim_aware"):
        rows = table(meta, strategy)
        with open(RESULTS_DIR / f"{strategy}_downstream.csv", "w", newline="") as f:
            w = csv.DictWriter(f, list(rows[0]))
            w.writeheader()
            w.writerows(rows)


if __name__ == "__main__":
    main()
