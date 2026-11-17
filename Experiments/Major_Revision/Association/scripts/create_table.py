import csv

import numpy as np
import pandas as pd
from scipy.stats import rankdata

from data import CONCISENESS_ROWS, FAMILIES, JUDGES, METRICS, RESULTS_DIR, frames

B, SEED = 2000, 0
NAMES = {"sonar": "SONAR", "crupi": "Crupi", "coderpe": "CodeRPE", "claude": "Claude Opus 4.8", "reference": ""}
DIMS = {"correctness": "Correctness", "abstraction": "Abstraction", "conciseness": "Conciseness", "fluency": "Fluency",
        "content_adequacy": "Content Adequacy", "coherence": "Coherence", "consistency": "Consistency",
        "relevance": "Relevance", "bleu4": "BLEU-4", "rouge_l": "ROUGE-L", "meteor": "METEOR", "bleurt": "BLEURT",
        "bertscore_f1": "BERTScore F1"}


def one_model(values, fn, n_fn):
    a = np.column_stack([rankdata(values[:, j]) for j in range(values.shape[1])])
    counts = np.maximum(np.bincount(fn, minlength=n_fn), 1)
    means = np.column_stack([np.bincount(fn, weights=a[:, j], minlength=n_fn) for j in range(a.shape[1])]) / counts[:, None]
    a = a - means[fn]
    xy, z = a[:, :2], a[:, 2:]
    xy = xy - z @ np.linalg.lstsq(z, xy, rcond=None)[0]
    x, y = xy[:, 0], xy[:, 1]
    den = np.sqrt((x @ x) * (y @ y))
    return float(x @ y / den) if den > 0 else np.nan


def partial(values, llm, fn, n_fn, n_llm):
    rs = np.array([one_model(values[llm == k], fn[llm == k], n_fn) for k in range(n_llm) if (llm == k).sum() > 2])
    rs = rs[~np.isnan(rs)]
    return float(np.tanh(np.mean(np.arctanh(np.clip(rs, -0.999, 0.999))))) if len(rs) else np.nan


def estimate(d, target, controls, tasks, draws):
    values = d[[target, "y", *controls, "len"]].to_numpy(float)
    llm_codes, llms = pd.factorize(d["llm"])
    fn_codes, fn_names = pd.factorize(d["task"])
    point = partial(values, llm_codes, fn_codes, len(fn_names), len(llms))
    rows_of = {t: np.flatnonzero(d["task"].to_numpy() == t) for t in fn_names}
    boots = []
    for draw in draws:
        parts = [(k, rows_of[tasks[i]]) for k, i in enumerate(draw) if tasks[i] in rows_of]
        idx = np.concatenate([r for _, r in parts])
        fn = np.concatenate([np.full(len(r), k) for k, r in parts])
        boots.append(partial(values[idx], llm_codes[idx], fn, len(draw), len(llms)))
    boots = np.array(boots)
    return point, boots


def number(x):
    return f"{abs(x):.2f}" if x >= 0 else f"−{abs(x):.2f}"


def cell(rho, boots):
    p = max(2 * min((boots <= 0).mean(), (boots >= 0).mean()), 1 / B)
    lo, hi = np.nanpercentile(boots, [2.5, 97.5])
    star = "***" if p < .001 else "**" if p < .01 else "*" if p < .05 else ""
    return f"{number(rho)}{star} [{number(lo)}, {number(hi)}]"


def main():
    rng = np.random.default_rng(SEED)
    data = frames()
    fits = {}
    for metric in METRICS:
        d = data[metric]
        tasks = list(pd.unique(d["task"]))
        draws = [rng.integers(0, len(tasks), len(tasks)) for _ in range(B)]
        for fam in JUDGES + ["reference"]:
            for dim in FAMILIES[fam]:
                m = f"{fam}:{dim}"
                base = d[d["sonar:conciseness"] != 1.0] if m in CONCISENESS_ROWS else d
                others = [f"{fam}:{o}" for o in FAMILIES[fam] if o != dim] if fam != "reference" else []
                fits[metric, m] = estimate(base, m, others, tasks, draws)

    RESULTS_DIR.mkdir(exist_ok=True)
    with open(RESULTS_DIR / "correlation_table.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Method", "Dimension", *METRICS])
        for fam in JUDGES + ["reference"]:
            for dim in FAMILIES[fam]:
                m = f"{fam}:{dim}"
                w.writerow([NAMES[fam], DIMS[dim] + ("†" if m in CONCISENESS_ROWS else ""),
                            *[cell(*fits[metric, m]) for metric in METRICS]])


if __name__ == "__main__":
    main()
