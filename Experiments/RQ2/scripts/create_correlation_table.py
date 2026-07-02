#!/usr/bin/env python3
import csv
import json
from collections import defaultdict
from itertools import combinations
from pathlib import Path

import numpy as np
from rapidfuzz.distance import Levenshtein
from scipy.stats import rankdata, spearmanr
from scipy.stats import t as student_t

SCRIPT_DIR        = Path(__file__).resolve().parent
TRANSLATION_DIR   = SCRIPT_DIR / "translation"
ORACLE_GEN_DIR    = SCRIPT_DIR / "oracle_gen"
DS_SUMMARIES      = SCRIPT_DIR / "summary_pool.jsonl"
OPTIMIZATION_DIR  = SCRIPT_DIR / "optimization"
RETRIEVAL_METRICS = SCRIPT_DIR / "retrieval" / "retrieval_metrics.jsonl"
RESULTS_DIR       = SCRIPT_DIR.parent / "results"
FULL_CSV          = RESULTS_DIR / "correlation_table.csv"
PARTIAL_CSV       = RESULTS_DIR / "correlation_partial.csv"

SONAR_DIMS = ["correctness", "abstraction", "conciseness", "fluency"]
BASE_DIMS  = ["bleu4", "meteor", "rouge_l", "bleurt", "bertscore_f1"]
ALL_DIMS   = SONAR_DIMS + BASE_DIMS
DIM_LABELS = {
    "correctness": "Correctness", "abstraction": "Abstraction",
    "conciseness": "Conciseness", "fluency": "Fluency",
    "bleu4": "BLEU-4", "meteor": "METEOR", "rouge_l": "ROUGE-L",
    "bleurt": "BLEURT", "bertscore_f1": "BERTScore",
}
COLUMNS = ["MRR", "CA@1", "Edit Dist.", "Pass@1", "Speedup", "Success Rate"]
MIN_N   = 10
ALPHA   = 0.05


def dim_rows(rows, dim):
    sub = [r for r in rows if r.get(dim) is not None]
    if dim == "conciseness":
        sub = [r for r in sub if r["conciseness"] != 1.0]  # discarded due to broken fuzzing scripts
    return sub


def load_meta() -> dict:
    meta = {}
    with open(DS_SUMMARIES) as f:
        for line in f:
            r = json.loads(line)
            meta[r["ID"]] = r
    return meta


def fisher_combine(rhos, ps, p_method="max"):
    zs = np.arctanh(np.clip(rhos, -0.999, 0.999))
    fisher_rho = float(np.tanh(np.mean(zs)))
    std_rho = float(np.std(rhos, ddof=1)) if len(rhos) > 1 else 0.0
    combined_p = float(np.max(ps)) if p_method == "max" else float(np.mean(ps))
    return fisher_rho, std_rho, combined_p


def sig_stars(p):
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "**"
    if round(p, 2) <= 0.05:
        return "*"
    return ""


def _merge_with_meta(rows_by_model, value_key, meta):
    out = {}
    for model_name, rows in rows_by_model.items():
        merged = []
        for r in rows:
            m = meta.get(r["summary_id"])
            if not m or r.get(value_key) is None:
                continue
            merged.append({**{d: m.get(d) for d in ALL_DIMS}, value_key: r[value_key]})
        out[model_name] = merged
    return out


def marginal_per_dim(merged, value_key, dims):
    per_dim = {}
    for dim in dims:
        sub = dim_rows(merged, dim)
        pairs = [(r[dim], r[value_key]) for r in sub]
        if len(pairs) < MIN_N:
            continue
        xs, ys = zip(*pairs)
        rho, p = spearmanr(xs, ys)
        per_dim[dim] = (rho, p)
    return per_dim


def _partial_spearman(merged, dim, value_key):
    controls = [d for d in SONAR_DIMS if d != dim]
    sub = dim_rows(merged, dim)
    sub = [r for r in sub if r.get(value_key) is not None
           and all(r.get(c) is not None for c in controls)]
    n, k = len(sub), len(controls)
    if n < MIN_N + k + 2:
        return None

    x = rankdata([r[dim] for r in sub]).astype(float)
    y = rankdata([r[value_key] for r in sub]).astype(float)
    z = np.column_stack([rankdata([r[c] for r in sub]) for c in controls]).astype(float)
    z1 = np.column_stack([z, np.ones(n)])

    bx, *_ = np.linalg.lstsq(z1, x, rcond=None)
    by, *_ = np.linalg.lstsq(z1, y, rcond=None)
    rx, ry = x - z1 @ bx, y - z1 @ by

    denom = np.linalg.norm(rx) * np.linalg.norm(ry)
    if denom == 0:
        return None
    rho = float(np.dot(rx, ry) / denom)

    df = n - 2 - k
    if df <= 0:
        return None
    if abs(rho) >= 1.0:
        return rho, 0.0
    tstat = rho * np.sqrt(df / (1 - rho ** 2))
    p = float(2 * (1 - student_t.cdf(abs(tstat), df)))
    return rho, p


def partial_per_dim(merged, value_key, dims):
    per_dim = {}
    for dim in dims:
        res = _partial_spearman(merged, dim, value_key)
        if res is not None:
            per_dim[dim] = res
    return per_dim


def _combine_models(per_model, dims):
    collect = defaultdict(lambda: {"rhos": [], "ps": []})
    for per_dim in per_model.values():
        for dim in dims:
            rho, p = per_dim.get(dim, (0.0, 1.0))
            collect[dim]["rhos"].append(rho)
            collect[dim]["ps"].append(p)
    result = {}
    for dim, d in collect.items():
        result[dim] = fisher_combine(d["rhos"], d["ps"], p_method="max")
    return result


def marginal_table(merged_by_model, value_key, dims=ALL_DIMS):
    per_model = {m: marginal_per_dim(rows, value_key, dims) for m, rows in merged_by_model.items()}
    return _combine_models(per_model, dims)


def partial_table(merged_by_model, value_key, dims=SONAR_DIMS):
    per_model = {m: partial_per_dim(rows, value_key, dims) for m, rows in merged_by_model.items()}
    return _combine_models(per_model, dims)


def task_retrieval():
    if RETRIEVAL_METRICS.exists():
        rows_by_model = defaultdict(list)
        with open(RETRIEVAL_METRICS) as f:
            for line in f:
                row = json.loads(line)
                model = row.pop("model")
                rows_by_model[model].append(row)
        return {"MRR": (dict(rows_by_model), "MRR")}

    from retrieval.calculate_retrieval_results import (
        get_overlap, load_positives, load_queries, compute_metrics,
        MODELS as EMBED_MODELS, CACHE_DIR,
    )
    he_overlap, mbpp_overlap = get_overlap()
    overlap_tids = he_overlap | mbpp_overlap
    ja_tids = load_positives(overlap_tids)
    queries = load_queries(he_overlap, mbpp_overlap)
    ja_idx_local = defaultdict(set)
    for i, t in enumerate(ja_tids):
        ja_idx_local[t].add(i)

    merged_by_model = {}
    for model_short, subdir in EMBED_MODELS.items():
        cache = CACHE_DIR / subdir
        ja_cache, q_cache = cache / "java_pos_vecs.npy", cache / "query_vecs.npy"
        py_dist_cache = cache / "unicor_python_vecs.npy"
        ja_dist_cache = cache / "unicor_java_vecs.npy"
        if not all(p.exists() for p in (ja_cache, q_cache, py_dist_cache, ja_dist_cache)):
            continue
        ja_vecs, query_vecs = np.load(ja_cache), np.load(q_cache)
        py_dist_vecs, ja_dist_vecs = np.load(py_dist_cache), np.load(ja_dist_cache)
        if query_vecs.shape[0] != len(queries):
            continue
        cross_pool = np.concatenate([ja_vecs, py_dist_vecs, ja_dist_vecs], axis=0)
        scores = query_vecs @ cross_pool.T
        merged_by_model[model_short] = compute_metrics(scores, ja_idx_local, queries)

    return {"MRR": (merged_by_model, "MRR")}


def _same_model_diversity_rows(model_name):
    p = TRANSLATION_DIR / f"translation_diversity_{model_name}.jsonl"
    if not p.exists():
        return []
    grouped = defaultdict(dict)
    with open(p) as f:
        for line in f:
            r = json.loads(line)
            grouped[(r["task_id"], r["summary_id"])][r["sample_idx"]] = r.get("code")

    rows = []
    for (task_id, summary_id), by_idx in grouped.items():
        codes = [c for c in by_idx.values() if c]
        if len(codes) < 2:
            continue
        dists = [Levenshtein.normalized_distance(a, b) for a, b in combinations(codes, 2)]
        rows.append({"summary_id": summary_id, "diversity_string": sum(dists) / len(dists)})
    return rows


def task_translation(meta):
    ca1_rows = {}
    for model_name in ["qwen", "olmo", "gemini"]:
        p = TRANSLATION_DIR / f"translation_{model_name}.jsonl"
        rows = [json.loads(line) for line in open(p)] if p.exists() else []
        for r in rows:
            r["pass_rate"] = 1.0 if r.get("passed") else 0.0
        ca1_rows[model_name] = rows
    ca1_merged = _merge_with_meta(ca1_rows, "pass_rate", meta)

    div_rows = {m: _same_model_diversity_rows(m) for m in ["qwen", "olmo", "gemini"]}
    div_merged = _merge_with_meta(div_rows, "diversity_string", meta)

    return {
        "CA@1":       (ca1_merged, "pass_rate"),
        "Edit Dist.": (div_merged, "diversity_string"),
    }


def task_optimization(meta):
    files = {
        "qwen":   OPTIMIZATION_DIR / "optimization_qwen.jsonl",
        "olmo":   OPTIMIZATION_DIR / "optimization_olmo.jsonl",
        "gemini": OPTIMIZATION_DIR / "optimization_gemini.jsonl",
    }
    rows_by_model = {}
    for name, path in files.items():
        rows = [json.loads(l) for l in open(path)] if path.exists() else []
        rows_by_model[name] = [{"summary_id": r["ID"],
                                 "pass_at_1": 1.0 if r.get("pass_rate") == 1.0 else 0.0,
                                 "mean_speedup": r.get("mean_speedup")}
                                for r in rows]
    pass1_merged = _merge_with_meta(rows_by_model, "pass_at_1", meta)
    speedup_merged = _merge_with_meta(rows_by_model, "mean_speedup", meta)

    return {
        "Pass@1":  (pass1_merged, "pass_at_1"),
        "Speedup": (speedup_merged, "mean_speedup"),
    }


def task_oracle_gen(meta):
    files = {
        "qwen":   ORACLE_GEN_DIR / "oracle_gen_qwen.jsonl",
        "olmo":   ORACLE_GEN_DIR / "oracle_gen_olmo.jsonl",
        "gemini": ORACLE_GEN_DIR / "oracle_gen_gemini.jsonl",
    }
    rows_by_model = {}
    for name, path in files.items():
        rows_by_model[name] = [json.loads(l) for l in open(path)] if path.exists() else []
    merged = _merge_with_meta(rows_by_model, "success_rate", meta)

    return {"Success Rate": (merged, "success_rate")}


def _best_per_column(table, dims):
    sig = [(dim, table[dim]) for dim in dims if dim in table and table[dim][2] < ALPHA]
    if not sig:
        return None
    return max(sig, key=lambda kv: abs(kv[1][0]))[0]


def write_marginal_csv(tables):
    best = {col: _best_per_column(tables[col], ALL_DIMS) for col in COLUMNS}
    with FULL_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Group", "Dim"] + COLUMNS)
        for group, dims in (("SONAR", SONAR_DIMS), ("Baselines", BASE_DIMS)):
            for dim in dims:
                row = [group, DIM_LABELS[dim]]
                for col in COLUMNS:
                    entry = tables[col].get(dim)
                    if entry is None:
                        row.append("--")
                        continue
                    rho, std, p = entry
                    cell = f"{rho:+.2f}(+/-{std:.2f}){sig_stars(p)}"
                    if dim == best[col]:
                        cell = f"[{cell}]"
                    row.append(cell)
                writer.writerow(row)


def write_partial_csv(tables):
    best = {col: _best_per_column(tables[col], SONAR_DIMS) for col in COLUMNS}
    with PARTIAL_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Dim"] + COLUMNS)
        for dim in SONAR_DIMS:
            row = [DIM_LABELS[dim]]
            for col in COLUMNS:
                entry = tables[col].get(dim)
                if entry is None:
                    row.append("--")
                    continue
                rho, std, p = entry
                cell = f"{rho:+.2f}{sig_stars(p)}"
                if dim == best[col]:
                    cell = f"[{cell}]"
                row.append(cell)
            writer.writerow(row)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--partial", action="store_true",
                         help="Write the partial-Spearman table instead of the marginal one.")
    args = parser.parse_args()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    meta = load_meta()

    merged_map = {}
    merged_map.update(task_retrieval())
    merged_map.update(task_translation(meta))
    merged_map.update(task_optimization(meta))
    merged_map.update(task_oracle_gen(meta))

    if args.partial:
        partial_tables = {col: partial_table(rows, value_key)
                           for col, (rows, value_key) in merged_map.items()}
        write_partial_csv(partial_tables)
    else:
        marginal_tables = {col: marginal_table(rows, value_key)
                            for col, (rows, value_key) in merged_map.items()}
        write_marginal_csv(marginal_tables)


if __name__ == "__main__":
    main()
