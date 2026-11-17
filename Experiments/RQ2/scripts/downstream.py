import csv
import json
from collections import defaultdict
from itertools import combinations
from pathlib import Path

from rapidfuzz.distance import Levenshtein

SCRIPT_DIR = Path(__file__).resolve().parent
SUMMARY_POOL = SCRIPT_DIR / "summary_pool.jsonl"
MRR_SCORES = SCRIPT_DIR / "retrieval" / "mrr_scores_rerun.csv"
TRANSLATION_DIR = SCRIPT_DIR / "translation"
OPTIMIZATION_DIR = SCRIPT_DIR / "optimization"
ORACLE_GEN_DIR = SCRIPT_DIR / "oracle_gen"
METRICS = ["MRR", "CA@1", "Edit Dist.", "Pass@1", "Speedup", "Success Rate"]
LLMS = ["qwen", "olmo", "gemini"]


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def load_meta():
    return {r["ID"]: r for r in read_jsonl(SUMMARY_POOL)}


def edit_distance_rows(llm):
    codes = defaultdict(dict)
    for r in read_jsonl(TRANSLATION_DIR / f"translation_diversity_{llm}.jsonl"):
        codes[r["task_id"], r["summary_id"]][r["sample_idx"]] = r.get("code")
    rows = []
    for (_, summary_id), by_idx in codes.items():
        found = [c for c in by_idx.values() if c]
        if len(found) >= 2:
            dists = [Levenshtein.normalized_distance(a, b) for a, b in combinations(found, 2)]
            rows.append((summary_id, sum(dists) / len(dists)))
    return rows


def outcomes():
    out = {m: [] for m in METRICS}
    with open(MRR_SCORES, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["MRR"] != "":
                out["MRR"].append((r["summary_id"], r["retriever"], float(r["MRR"])))
    for llm in LLMS:
        for r in read_jsonl(TRANSLATION_DIR / f"translation_{llm}.jsonl"):
            out["CA@1"].append((r["summary_id"], llm, 1.0 if r.get("passed") else 0.0))
        out["Edit Dist."] += [(sid, llm, value) for sid, value in edit_distance_rows(llm)]
        for r in read_jsonl(OPTIMIZATION_DIR / f"optimization_{llm}.jsonl"):
            out["Pass@1"].append((r["ID"], llm, 1.0 if r.get("pass_rate") == 1.0 else 0.0))
            out["Speedup"].append((r["ID"], llm, r.get("mean_speedup")))
        for r in read_jsonl(ORACLE_GEN_DIR / f"oracle_gen_{llm}.jsonl"):
            out["Success Rate"].append((r["summary_id"], llm, r.get("success_rate")))
    return out
