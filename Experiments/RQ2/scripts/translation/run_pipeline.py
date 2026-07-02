#!/usr/bin/env python3

import json
import math
import re
import shutil
import subprocess
import tempfile
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from prompts import build_messages, extract_body, get_java_skeleton

SCRIPT_DIR      = Path(__file__).resolve().parent
SUMMARIES_PATH  = SCRIPT_DIR.parent / "summary_pool.jsonl"
MULTIPL_E_DIR   = SCRIPT_DIR.parent / "MultiPL-E"
JAVATUPLES_JAR  = MULTIPL_E_DIR / "javatuples-1.2.jar"
OUT_DIR         = SCRIPT_DIR

MODELS = ["qwen", "olmo", "codestral"]


_JAVA_KEYWORDS = {
    'abstract','assert','boolean','break','byte','case','catch','char','class',
    'const','continue','default','do','double','else','enum','extends','final',
    'finally','float','for','goto','if','implements','import','instanceof','int',
    'interface','long','native','new','package','private','protected','public',
    'return','short','static','strictfp','super','switch','synchronized','this',
    'throw','throws','transient','try','void','volatile','while','true','false','null',
}

_STRUCTURAL_TOKENS = {
    'if','else','for','while','do','switch','case','default','break','continue',
    'return','try','catch','finally','throw','new',
    '{','}','(',')','[',']',';',
    '==','!=','<=','>=','<','>','&&','||','!',
    '+','-','*','/','%','?',':',
} | _JAVA_KEYWORDS

_TOKEN_RE = re.compile(
    r'//[^\n]*'
    r'|/\*.*?\*/'
    r'|"(?:[^"\\]|\\.)*"'
    r"|'(?:[^'\\]|\\.)*'"
    r'|[a-zA-Z_]\w*'
    r'|[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?[fFdDlL]?'
    r'|[-+*/=<>!&|^~%]{1,3}|[(){}\[\];,.]',
    re.DOTALL,
)


def tokenize_java(code: str) -> List[str]:
    tokens = []
    for m in _TOKEN_RE.finditer(code):
        tok = m.group(0)
        if tok.startswith("//") or tok.startswith("/*"):
            continue
        tokens.append(tok)
    return tokens


def structural_tokens(code: str) -> List[str]:
    return [t for t in tokenize_java(code) if t in _STRUCTURAL_TOKENS]


def normalized_edit_distance(seq1: List[str], seq2: List[str]) -> float:
    if not seq1 and not seq2:
        return 0.0
    if not seq1 or not seq2:
        return 1.0
    n, m = len(seq1), len(seq2)
    prev = list(range(m + 1))
    for i in range(1, n + 1):
        curr = [i] + [0] * m
        for j in range(1, m + 1):
            cost = 0 if seq1[i - 1] == seq2[j - 1] else 1
            curr[j] = min(curr[j - 1] + 1, prev[j] + 1, prev[j - 1] + cost)
        prev = curr
    return prev[m] / max(n, m)


def pairwise_diversity(codes: List[str], token_fn) -> float:
    seqs = [token_fn(c) for c in codes if c]
    if len(seqs) < 2:
        return float("nan")
    dists = [
        normalized_edit_distance(a, b)
        for a, b in combinations(seqs, 2)
    ]
    return sum(dists) / len(dists)


def load_multipl_e() -> Dict:
    data = {}
    for line in open(MULTIPL_E_DIR / "humaneval_java.jsonl"):
        e = json.loads(line)
        m = re.match(r"(HumanEval_\d+)_", e["name"])
        if not m:
            continue
        tid = m.group(1)
        data[tid] = {
            "prompt":   e["prompt"],
            "tests":    e["tests"],
            "skeleton": get_java_skeleton(e["prompt"]),
        }
    for line in open(MULTIPL_E_DIR / "mbpp_java.jsonl"):
        e = json.loads(line)
        m = re.match(r"mbpp_(\d+)_", e["name"])
        if not m:
            continue
        tid = f"MBPP_{m.group(1)}"
        data[tid] = {
            "prompt":   e["prompt"],
            "tests":    e["tests"],
            "skeleton": get_java_skeleton(e["prompt"]),
        }
    return data


def load_summaries(valid_tids: set) -> Dict:
    by_task = defaultdict(list)
    with open(SUMMARIES_PATH) as f:
        for line in f:
            r = json.loads(line)
            if r["task_id"] in valid_tids:
                by_task[r["task_id"]].append(r)
    return dict(by_task)


def run_java(prompt: str, body: str, tests: str) -> Tuple[bool, str]:
    full_java = prompt + "\n" + body + "\n" + tests
    tmp = tempfile.mkdtemp(prefix="task3m_java_")
    try:
        java_file = Path(tmp) / "Problem.java"
        java_file.write_text(full_java)
        cp = subprocess.run(
            ["javac", "-cp", str(JAVATUPLES_JAR), "Problem.java"],
            cwd=tmp, capture_output=True, text=True, timeout=30,
        )
        if cp.returncode != 0:
            return False, f"compile_error: {cp.stderr[:300]}"
        rp = subprocess.run(
            ["java", "-ea", "-cp", f".:{JAVATUPLES_JAR}", "Problem"],
            cwd=tmp, capture_output=True, text=True, timeout=15,
        )
        if rp.returncode == 0:
            return True, ""
        return False, f"runtime_error: {rp.stderr[:200]}"
    except subprocess.TimeoutExpired:
        return False, "timeout"
    except Exception as e:
        return False, str(e)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def build_completion_prompt(description: str, skeleton: str) -> str:
    return (
        f"// Task description: {description}\n"
        f"// Implement the method body below.\n"
        f"{skeleton} {{\n"
    )


def load_local_model(model_path: Path, load_in_4bit: bool = False):
    from common.model import load_model
    return load_model(model_path, max_new_tokens=1024, load_in_4bit=load_in_4bit)


def codes_path(model_name: str) -> Path:
    return OUT_DIR / f"translation_{model_name}.jsonl"

def bodies_path(model_name: str) -> Path:
    return OUT_DIR / f"translation_bodies_{model_name}.jsonl"


def _load_done(path: Path) -> set:
    done = set()
    if path.exists():
        with open(path) as f:
            for line in f:
                r = json.loads(line)
                done.add((r["task_id"], r["summary_id"]))
    return done


def _append(path: Path, record: dict):
    with open(path, "a") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def phase_generate(args, multipl_e, summaries_by_task):
    model_name = args.model_name
    out_path   = bodies_path(model_name)

                                                               
    done = _load_done(out_path) | _load_done(codes_path(model_name))
    todo = [
        (tid, s)
        for tid, slist in summaries_by_task.items()
        for s in slist
        if (tid, s["ID"]) not in done
    ]
    print(f"[generate] {len(done)} done, {len(todo)} remaining → {out_path}")

    if not todo:
        print("All bodies already generated.")
        return

    print(f"Loading model: {model_name} …")
    model = load_local_model(Path(args.model), load_in_4bit=args.load_in_4bit)

    is_completion = hasattr(model, "complete") and not hasattr(model, "chat")

    for i, (task_id, s) in enumerate(todo, 1):
        summary_id  = s["ID"]
        description = s["summary"]
        entry       = multipl_e[task_id]
        print(f"  [{i}/{len(todo)}] {task_id} / {summary_id[:60]}", flush=True)
        try:
            if is_completion:
                raw = model.complete(build_completion_prompt(description, entry["skeleton"]), max_new_tokens=1024)
            else:
                raw = model.chat(build_messages(description, entry["skeleton"]))
            body   = extract_body(raw)
            record = {"task_id": task_id, "summary_id": summary_id,
                      "model": model_name, "code": body}
        except Exception as e:
            record = {"task_id": task_id, "summary_id": summary_id,
                      "model": model_name, "code": None, "error": str(e)}
            print(f"    ERROR: {e}", flush=True)
        _append(out_path, record)

    model.unload()
    print(f"\nGeneration done → {out_path}")


def _compile_one(work):
    task_id, summary_id, model_name, code, prompt, tests = work
    if not code:
        return {"task_id": task_id, "summary_id": summary_id, "model": model_name,
                "code": code, "passed": False, "pass_rate": 0.0, "error": "no_body"}
    passed, err = run_java(prompt, code, tests)
    return {"task_id": task_id, "summary_id": summary_id, "model": model_name,
            "code": code, "passed": passed,
            "pass_rate": 1.0 if passed else 0.0,
            "error": err if err else None}


def phase_compile(args, multipl_e):
    from concurrent.futures import ThreadPoolExecutor, as_completed

    model_name = args.model_name
    bp         = bodies_path(model_name)
    cp         = codes_path(model_name)

    if not bp.exists():
        print(f"ERROR: {bp.name} not found — run --generate-only first.")
        return

    bodies = []
    with open(bp) as f:
        for line in f:
            bodies.append(json.loads(line))

    done = _load_done(cp)
    todo = [b for b in bodies if (b["task_id"], b["summary_id"]) not in done]
    print(f"[compile] {len(done)} done, {len(todo)} remaining  jobs={args.jobs}")

    if not todo:
        print("All compiled.")
        return

    work = [
        (b["task_id"], b["summary_id"], b["model"], b.get("code"),
         multipl_e[b["task_id"]]["prompt"], multipl_e[b["task_id"]]["tests"])
        for b in todo if b["task_id"] in multipl_e
    ]

    n = 0
    with open(cp, "a") as out_f:
        with ThreadPoolExecutor(max_workers=args.jobs) as pool:
            futures = {pool.submit(_compile_one, w): w for w in work}
            for fut in as_completed(futures):
                record = fut.result()
                out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
                out_f.flush()
                n += 1
                status = "PASS" if record.get("passed") else "FAIL"
                print(f"  [{n}/{len(work)}] {record['task_id']} / "
                      f"{record['summary_id'][:50]}  {status}", flush=True)

    print(f"\nCompile done → {cp}")


def run_model(args, multipl_e, summaries_by_task):
    phase_generate(args, multipl_e, summaries_by_task)
    if not args.generate_only:
        print("\nRunning sequential compile (use --compile-only --jobs N for faster) …")
        args.jobs = 1
        phase_compile(args, multipl_e)


def run_merge():
    print("[merge] Loading per-model code files …")

                                                         
    by_pair: Dict[Tuple, Dict] = defaultdict(dict)
    for model_name in MODELS:
        path = codes_path(model_name)
        if not path.exists():
            print(f"  WARNING: {path.name} not found — skipping {model_name}")
            continue
        n = 0
        with open(path) as f:
            for line in f:
                r = json.loads(line)
                key = (r["task_id"], r["summary_id"])
                by_pair[key][model_name] = {
                    "code":   r.get("code"),
                    "passed": r.get("passed", False),
                }
                n += 1
        print(f"  {model_name}: {n} records")

                                 
    summaries = {}
    with open(SUMMARIES_PATH) as f:
        for line in f:
            r = json.loads(line)
            summaries[r["ID"]] = r

    print(f"\n[merge] Computing diversity for {len(by_pair)} (task_id, summary_id) pairs …")

    div_out  = OUT_DIR / "translation_sample_pool.jsonl"
    rate_out = OUT_DIR / "translation_passrate.jsonl"

    with open(div_out, "w") as df, open(rate_out, "w") as rf:
        for (task_id, summary_id), model_results in sorted(by_pair.items()):

            codes = [model_results[m]["code"] or "" for m in MODELS if m in model_results]
            passed_flags = {m: model_results[m]["passed"] for m in MODELS if m in model_results}

                                                        
            n_models = len(passed_flags)
            pass_rate = sum(passed_flags.values()) / n_models if n_models else 0.0

                                                                  
            div_token  = pairwise_diversity(codes, tokenize_java)
            div_struct = pairwise_diversity(codes, structural_tokens)

                              
            meta = summaries.get(summary_id, {})

            record = {
                "task_id":        task_id,
                "summary_id":     summary_id,
                "correctness":    meta.get("correctness"),
                "abstraction":    meta.get("abstraction"),
                "conciseness":    meta.get("conciseness"),
                "fluency":        meta.get("fluency"),
                "pass_rate":      pass_rate,
                "n_models":       n_models,
                "diversity_token":  div_token  if not math.isnan(div_token)  else None,
                "diversity_struct": div_struct if not math.isnan(div_struct) else None,
            }
                                            
            for m in MODELS:
                if m in model_results:
                    record[f"{m}_code"]   = model_results[m]["code"]
                    record[f"{m}_passed"] = model_results[m]["passed"]

            df.write(json.dumps(record, ensure_ascii=False) + "\n")

                                                                                         
            rf.write(json.dumps({
                "ID":               summary_id,
                "pass_rate":        pass_rate,
                "diversity_token":  record["diversity_token"],
                "diversity_struct": record["diversity_struct"],
                "correctness":      meta.get("correctness"),
                "abstraction":      meta.get("abstraction"),
            }) + "\n")

    print(f"\nWritten:")
    print(f"  {div_out}")
    print(f"  {rate_out}")
    print(f"\nTo run correlation analysis:")
    print(f"  python conditional_expectation_analysis.py --passrate {rate_out}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Task 3 – Multi-Model Translation + Diversity")
    parser.add_argument("--model",         type=str,  default=None,
                        help="Path to local HF model.")
    parser.add_argument("--model-name",    type=str,  default=None,
                        help=f"Label for output files. One of: {MODELS}")
    parser.add_argument("--load-in-4bit",  action="store_true")
    parser.add_argument("--generate-only", action="store_true",
                        help="Phase 1: inference only, store java bodies. No compilation.")
    parser.add_argument("--compile-only",  action="store_true",
                        help="Phase 2: compile stored bodies in parallel. No model needed.")
    parser.add_argument("--jobs",          type=int, default=8,
                        help="Parallel workers for --compile-only (default: 8).")
    parser.add_argument("--merge",         action="store_true",
                        help="Merge all 4 model code files and compute diversity.")
    parser.add_argument("--dry-run",       action="store_true")
    args = parser.parse_args()

    if args.merge:
        run_merge()
        return

    if args.compile_only:
        if not args.model_name:
            parser.error("--compile-only requires --model-name")
        print("[1/2] Loading MultiPL-E Java data …")
        multipl_e = load_multipl_e()
        print(f"      {len(multipl_e)} tasks")
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        phase_compile(args, multipl_e)
        return

    if args.model and args.model_name:
        print("[1/2] Loading MultiPL-E Java data …")
        multipl_e = load_multipl_e()
        print(f"      {len(multipl_e)} tasks")
        print("[2/2] Loading summaries …")
        summaries_by_task = load_summaries(set(multipl_e.keys()))
        total = sum(len(v) for v in summaries_by_task.values())
        print(f"      {len(summaries_by_task)} tasks, {total} summaries")
        if args.dry_run:
            print("[dry-run] data OK — exiting before model load.")
            return
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        run_model(args, multipl_e, summaries_by_task)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
