#!/usr/bin/env python3
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

SCRIPT_DIR      = Path(__file__).resolve().parent
TRANSLATION_DIR = SCRIPT_DIR.parent / "translation"
DS_SUMMARIES    = SCRIPT_DIR.parent / "summary_pool.jsonl"
QUERY_IDS       = SCRIPT_DIR / "retrieval_query_ids.jsonl"
CACHE_DIR       = SCRIPT_DIR / "retrieval_cache"

AFC_DIMS  = ["correctness", "abstraction", "conciseness", "fluency"]
BASE_DIMS = ["bleu4", "rouge_l", "meteor", "bleurt", "bertscore_f1"]
ALL_DIMS  = AFC_DIMS + BASE_DIMS

                                                                     
MODELS = {
    "unixcoder":     "unixcoder",
    "codet5p":       "codet5p",
    "graphcodebert": "graphcodebert",
}


def get_overlap():
    java_he, java_mbpp = set(), set()
    for m in ["codestral", "kimi", "olmo", "qwen"]:
        p = TRANSLATION_DIR / f"translation_{m}.jsonl"
        if not p.exists():
            continue
        with open(p) as f:
            for line in f:
                r = json.loads(line)
                if r["pass_rate"] != 1.0:
                    continue
                if r["task_id"].startswith("HumanEval"):
                    java_he.add(r["task_id"])
                elif r["task_id"].startswith("MBPP"):
                    java_mbpp.add(r["task_id"])

    he_q, mbpp_q = set(), set()
    with open(QUERY_IDS) as f:
        for line in f:
            tid = json.loads(line)["task_id"]
            if tid.startswith("HumanEval"):
                he_q.add(tid)
            elif tid.startswith("MBPP"):
                mbpp_q.add(tid)

    return java_he & he_q, java_mbpp & mbpp_q


def load_positives(overlap_tids):
    ja_per = defaultdict(set)
    for m in ["codestral", "kimi", "olmo", "qwen"]:
        p = TRANSLATION_DIR / f"translation_{m}.jsonl"
        if not p.exists():
            continue
        with open(p) as f:
            for line in f:
                r = json.loads(line)
                if r["task_id"] in overlap_tids and r["pass_rate"] == 1.0:
                    ja_per[r["task_id"]].add(r["code"])

    return [t for t in sorted(ja_per) for _ in ja_per[t]]


def load_queries(he_overlap, mbpp_overlap):
    ds_by_id = {}
    with open(DS_SUMMARIES) as f:
        for line in f:
            r = json.loads(line)
            ds_by_id[r["ID"]] = r

    overlap_tids = he_overlap | mbpp_overlap
    queries = []
    with open(QUERY_IDS) as f:
        for line in f:
            row = json.loads(line)
            if row["task_id"] not in overlap_tids:
                continue
            ds = ds_by_id.get(row["summary_id"])
            if ds is None:
                continue
            queries.append({"task_id": row["task_id"],
                            **{d: float(ds[d]) if ds.get(d) is not None else None for d in AFC_DIMS},
                            **{d: ds.get(d) for d in BASE_DIMS}})
    return queries


def compute_metrics(scores, pos_map, queries):
    rows = []
    for q, row_s in zip(queries, scores):
        pos = pos_map.get(q["task_id"], set())
        if not pos:
            continue
        ranked = np.argsort(-row_s)
        mrr = next((1 / r for r, idx in enumerate(ranked, 1) if idx in pos), 0.0)
        rows.append({**{d: q.get(d) for d in ALL_DIMS}, "MRR": mrr})
    return rows
