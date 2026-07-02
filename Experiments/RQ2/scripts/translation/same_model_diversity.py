#!/usr/bin/env python3
import json
from itertools import combinations
from pathlib import Path

import numpy as np
from rapidfuzz.distance import Levenshtein

from run_pipeline import (
    load_multipl_e, normalized_edit_distance,
    structural_tokens, tokenize_java,
)
from prompts import build_messages, extract_body, get_java_skeleton

OUT_DIR      = Path(__file__).resolve().parent
SUMMARY_PATH = OUT_DIR / "same_model_diversity_summary.jsonl"
SRC_POOL     = OUT_DIR / "translation_sample_pool.jsonl"                                                  

MODELS       = ["qwen", "olmo", "gemini"]
UNIXCODER    = "microsoft/unixcoder-base"
MAX_LENGTH   = 512
BATCH_SIZE   = 64


def codes_path(model_name: str) -> Path:
    return OUT_DIR / f"translation_diversity_{model_name}.jsonl"


def load_sample():
    with open(SRC_POOL) as f:
        return [json.loads(line) for line in f]


                                                                                 
                                                                     
                                                                                
                                                                      
EXISTING_CODES = {
    "qwen": OUT_DIR / "translation_qwen.jsonl",
    "olmo": OUT_DIR / "translation_olmo.jsonl",
}


def _load_done(path: Path) -> set:
    done = set()
    if path.exists():
        with open(path) as f:
            for line in f:
                r = json.loads(line)
                done.add((r["task_id"], r["summary_id"], r["sample_idx"]))
    return done


def _seed_existing(model_name: str, out_path: Path, sample: list, done: set) -> set:
    src = EXISTING_CODES.get(model_name)
    if not src or not src.exists():
        return done
    existing = {}
    with open(src) as f:
        for line in f:
            r = json.loads(line)
            existing[(r["task_id"], r["summary_id"])] = r

    seeded = 0
    with open(out_path, "a") as out_f:
        for r in sample:
            key = (r["task_id"], r["summary_id"])
            if (key[0], key[1], 0) in done:
                continue
            ex = existing.get(key)
            if not ex or not ex.get("code"):
                continue
            record = {"task_id": key[0], "summary_id": key[1], "model": model_name,
                      "sample_idx": 0, "code": ex["code"]}
            out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
            done.add((key[0], key[1], 0))
            seeded += 1
    if seeded:
        print(f"[{model_name}] seeded {seeded} sample_idx=0 rows from existing {src.name} (reused, not regenerated)")
    return done


def cmd_generate(model_name: str, model_path: str, k: int, temperature: float, load_in_4bit: bool,
                  max_samples: int | None = None):
    sample = load_sample()
    multipl_e = load_multipl_e()

    out_path = codes_path(model_name)
    done = _load_done(out_path)
    done = _seed_existing(model_name, out_path, sample, done)
    todo = [
        (r, k_i)
        for r in sample
        for k_i in range(k)
        if (r["task_id"], r["summary_id"], k_i) not in done
    ]
    if max_samples is not None:
        todo = todo[:max_samples]
    print(f"[{model_name}] {len(done)} done, {len(todo)} remaining this run (rows={len(sample)}, K={k}) → {out_path}")
    if not todo:
        print("Nothing to do.")
        return

    from common.model import load_model
    model = load_model(model_path, max_new_tokens=1024, load_in_4bit=load_in_4bit)

    from run_pipeline import SUMMARIES_PATH
    desc_by_id = {}
    with open(SUMMARIES_PATH) as f:
        for line in f:
            s = json.loads(line)
            desc_by_id[s["ID"]] = s["summary"]

    with open(out_path, "a") as out_f:
        for i, (r, k_i) in enumerate(todo, 1):
            task_id, summary_id = r["task_id"], r["summary_id"]
            entry = multipl_e[task_id]
            description = desc_by_id.get(summary_id, "")
            print(f"  [{i}/{len(todo)}] {task_id} / {summary_id[:50]} / sample {k_i}", flush=True)
            try:
                msgs = build_messages(description, entry["skeleton"])
                raw = model.chat(msgs, temperature=temperature)
                body = extract_body(raw)
                record = {"task_id": task_id, "summary_id": summary_id, "model": model_name,
                          "sample_idx": k_i, "code": body}
            except Exception as e:
                record = {"task_id": task_id, "summary_id": summary_id, "model": model_name,
                          "sample_idx": k_i, "code": None, "error": str(e)}
                print(f"    ERROR: {e}", flush=True)
            out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
            out_f.flush()

    model.unload()
    print(f"\nDone → {out_path}")


def pairwise_avg(seqs, dist_fn):
    if len(seqs) < 2:
        return None
    dists = [dist_fn(a, b) for a, b in combinations(seqs, 2)]
    return sum(dists) / len(dists)


def embed_all(texts, tokenizer, encoder, device):
    import torch
    import torch.nn.functional as F
    from tqdm import tqdm
    vecs = []
    with torch.no_grad():
        for i in tqdm(range(0, len(texts), BATCH_SIZE), desc="embedding"):
            batch = texts[i : i + BATCH_SIZE]
            enc = tokenizer(batch, padding=True, truncation=True,
                             max_length=MAX_LENGTH, return_tensors="pt").to(device)
            out = encoder(**enc)
            mask = enc["attention_mask"].unsqueeze(-1).float()
            v = (out.last_hidden_state * mask).sum(1) / mask.sum(1).clamp(min=1)
            v = F.normalize(v, dim=-1)
            vecs.append(v.cpu().numpy())
    return np.concatenate(vecs, axis=0)


def cmd_merge():
    import torch
    from transformers import AutoModel, AutoTokenizer

    sample = load_sample()
    meta_by_key = {(r["task_id"], r["summary_id"]): r for r in sample}

    all_records = []
    for model_name in MODELS:
        p = codes_path(model_name)
        if not p.exists():
            print(f"WARNING: {p.name} not found — skipping {model_name}")
            continue
        with open(p) as f:
            for line in f:
                all_records.append(json.loads(line))

    print(f"Loaded {len(all_records)} (row, model, sample) records")

    unique_codes = sorted({r["code"] for r in all_records if r.get("code")})
    print(f"Embedding {len(unique_codes)} unique code snippets with {UNIXCODER} …")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tokenizer = AutoTokenizer.from_pretrained(UNIXCODER, trust_remote_code=True)
    encoder = AutoModel.from_pretrained(UNIXCODER, trust_remote_code=True).to(device).eval()
    vecs = embed_all(unique_codes, tokenizer, encoder, device)
    vec_by_code = {c: v for c, v in zip(unique_codes, vecs)}

    from collections import defaultdict
    grouped = defaultdict(list)
    for r in all_records:
        grouped[(r["task_id"], r["summary_id"], r["model"])].append(r)

    def metrics_for(codes):
        if len(codes) < 2:
            return {"diversity_token": None, "diversity_struct": None,
                    "diversity_string": None, "diversity_embed": None}
        embs = [vec_by_code[c] for c in codes]
        edist = [1.0 - float(np.dot(a, b)) for a, b in combinations(embs, 2)]
        return {
            "diversity_token":  pairwise_avg([tokenize_java(c) for c in codes], normalized_edit_distance),
            "diversity_struct": pairwise_avg([structural_tokens(c) for c in codes], normalized_edit_distance),
            "diversity_string": pairwise_avg(codes, Levenshtein.normalized_distance),
            "diversity_embed":  sum(edist) / len(edist),
        }

    out_rows = []
    for (task_id, summary_id, model_name), samples in sorted(grouped.items()):
        codes_all = [s["code"] for s in samples if s.get("code")]
        meta = meta_by_key.get((task_id, summary_id), {})

        out_rows.append({
            "task_id": task_id, "summary_id": summary_id, "model": model_name,
            "k": len(samples),
            "correctness": meta.get("correctness"), "abstraction": meta.get("abstraction"),
            **metrics_for(codes_all),
        })

    with open(SUMMARY_PATH, "w") as f:
        for r in out_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"\nWritten {len(out_rows)} rows → {SUMMARY_PATH}")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-name", type=str, choices=MODELS)
    parser.add_argument("--model", type=str, help="Model path, or 'gemini'")
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--temperature", type=float, default=0.8)
    parser.add_argument("--load-in-4bit", action="store_true")
    parser.add_argument("--max-samples", type=int, default=None,
                        help="Cap the number of new (row, sample_idx) generations this run.")
    parser.add_argument("--merge", action="store_true")
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if args.merge:
        cmd_merge()
        return
    if args.model_name and args.model:
        cmd_generate(args.model_name, args.model, args.k, args.temperature, args.load_in_4bit,
                     args.max_samples)
        return
    parser.print_help()


if __name__ == "__main__":
    main()
