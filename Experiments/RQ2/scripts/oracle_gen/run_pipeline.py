#!/usr/bin/env python3

import json
import re
import signal
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional

SCRIPT_DIR      = Path(__file__).resolve().parent
SUMMARIES_PATH  = SCRIPT_DIR.parent / "summary_pool.jsonl"
HE_FUZZ_READY   = SCRIPT_DIR.parent / "dataset" / "HE.jsonl"
MBPP_FUZZ_READY = SCRIPT_DIR.parent / "dataset" / "MBPP.jsonl"

N_ASSERTS = 10                                   

SYSTEM = (
    "You are a software testing expert. "
    "Write Python assert statements to test a function based solely on its description. "
    "Do not use any knowledge beyond what is stated in the description."
)

USER = """\
Write {n} Python assert statements that test the following function.

## Function description
{summary}

## Function signature
{func_sig}

## Requirements
- Output ONLY assert statements, one per line, no explanation or imports
- Each assert must call `{entry_point}(...)` with concrete literal inputs
- The expected value must be a concrete literal (not a variable or expression)
- Cover typical inputs and at least one edge case

## Output
"""


def build_messages(summary: str, func_sig: str, entry_point: str, n: int = N_ASSERTS) -> list:
    return [
        {"role": "system", "content": SYSTEM},
        {"role": "user",   "content": USER.format(
            summary=summary, func_sig=func_sig,
            entry_point=entry_point, n=n,
        )},
    ]


def parse_asserts(raw: str) -> List[str]:
    asserts = []
    for line in raw.splitlines():
        s = line.strip()
        s = re.sub(r"^```[a-zA-Z]*", "", s).strip()
        if s.startswith("assert "):
            asserts.append(s)
    return asserts


class _Timeout(Exception):
    pass

def _alarm(signum, frame):
    raise _Timeout()

def run_assert(stmt: str, func_code: str, timeout: int = 5) -> str:
    script = func_code + "\n" + stmt
    ns: Dict = {}
    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(timeout)
    try:
        exec(compile(script, "<assert>", "exec"), ns)
        return "pass"
    except AssertionError:
        return "fail"
    except _Timeout:
        return "timeout"
    except Exception as e:
        return f"error:{type(e).__name__}"
    finally:
        signal.alarm(0)


def load_sample_task_ids() -> set:
    tids = set()
    with open(SUMMARIES_PATH) as f:
        for line in f:
            r = json.loads(line)
            if r["dataset"] in ("HumanEval", "MBPP"):
                tids.add(r["task_id"])
    return tids


def load_entries(valid_tids: set) -> Dict[str, Dict]:
    entries = {}

               
    with open(HE_FUZZ_READY) as f:
        for line in f:
            e = json.loads(line)
            tid = e["task_id"]                
            if tid in valid_tids:
                canonical = e["prompt"] + e["canonical_solution"]
                sig = next(
                    (l.strip() for l in e["prompt"].splitlines() if l.strip().startswith("def ")),
                    f"def {e['entry_point']}(...):"
                )
                imports = "\n".join(
                    l for l in e["prompt"].splitlines()
                    if l.strip() and not l.strip().startswith("def ")
                )
                entries[tid] = {
                    "entry_point": e["entry_point"],
                    "func_sig":    sig,
                    "imports":     imports,
                    "canonical":   canonical,
                    "tests":       e["test_case_list"],
                }

                                                            
    with open(MBPP_FUZZ_READY) as f:
        for line in f:
            e = json.loads(line)
            tid = f"MBPP_{e['task_id']}"
            if tid in valid_tids:
                code = e.get("code", "")
                setup = e.get("test_setup_code", "")
                canonical = (setup + "\n" + code).strip() if setup else code
                ep = e.get("entry_point", "")
                sig = next(
                    (l.strip() for l in code.splitlines() if l.strip().startswith("def ")),
                    f"def {ep}(...):"
                )
                entries[tid] = {
                    "entry_point": ep,
                    "func_sig":    sig,
                    "imports":     setup,
                    "canonical":   canonical,
                    "tests":       e.get("test_list", []),
                }

    return entries


def load_summaries(valid_tids: set) -> Dict[str, List[Dict]]:
    by_task = defaultdict(list)
    with open(SUMMARIES_PATH) as f:
        for line in f:
            r = json.loads(line)
            if r["task_id"] in valid_tids:
                by_task[r["task_id"]].append(r)
    return dict(by_task)


def process(summary_rec: Dict, entry: Dict, model, model_name: str,
            n_asserts: int = N_ASSERTS) -> Dict:
    task_id    = summary_rec["task_id"]
    summary_id = summary_rec["ID"]
    summary    = summary_rec["summary"]
    ep         = entry["entry_point"]
    func_sig   = entry["func_sig"]
    canonical  = entry["canonical"]

                      
    msgs = build_messages(summary, func_sig, ep, n=n_asserts)
    raw  = model(msgs)
    asserts = parse_asserts(raw)

                                
    results = [run_assert(a, canonical) for a in asserts]
    passing = [a for a, r in zip(asserts, results) if r == "pass"]

    n_total   = len(asserts)
    n_passing = len(passing)
    success_rate = n_passing / n_total if n_total else 0.0

    return {
        "task_id":          task_id,
        "summary_id":       summary_id,
        "model":            model_name,
        "generated_asserts": asserts,
        "assert_results":   results,
        "n_asserts":        n_total,
        "n_pass_canonical": n_passing,
        "success_rate":     success_rate,
        "error":            None,
    }


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


def _write_passrate(raw_path: Path, out_path: Path):
    by_id = {}
    with open(raw_path) as f:
        for line in f:
            r = json.loads(line)
            if "success_rate" not in r:
                continue
            by_id[r["summary_id"]] = {
                "ID":           r["summary_id"],
                "success_rate": r["success_rate"],
            }
    with open(out_path, "w") as f:
        for sid, rec in sorted(by_id.items()):
            f.write(json.dumps(rec) + "\n")
    print(f"Pass-rate file → {out_path}  ({len(by_id)} summaries)")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Task 5 – Test Oracle Generation")
    parser.add_argument("--model",        type=str, default=None,
                        help="Path to local HF model, or 'gemini'.")
    parser.add_argument("--model-name",   type=str, default=None)
    parser.add_argument("--load-in-4bit", action="store_true")
    parser.add_argument("--out-dir",      type=Path, default=SCRIPT_DIR)
    parser.add_argument("--n-asserts",    type=int, default=N_ASSERTS)
    parser.add_argument("--dry-run",      action="store_true")
    args = parser.parse_args()

    print("[1/4] Loading sample task IDs …")
    valid_tids = load_sample_task_ids()
    print(f"      {len(valid_tids)} tasks (HumanEval + MBPP)")

    print("[2/4] Loading entries …")
    entries = load_entries(valid_tids)
    print(f"      {len(entries)} entries")

    print("[3/4] Loading summaries …")
    summaries_by_task = load_summaries(set(entries.keys()))
    total = sum(len(v) for v in summaries_by_task.values())
    print(f"      {len(summaries_by_task)} tasks, {total} summaries")

    if args.dry_run:
        print("[dry-run] data OK — exiting before model load.")
        return

    args.out_dir.mkdir(parents=True, exist_ok=True)
    raw_path  = args.out_dir / f"oracle_gen_{args.model_name}.jsonl"
    rate_path = args.out_dir / f"oracle_gen_passrate_{args.model_name}.jsonl"

    done = _load_done(raw_path)
    todo = [
        (tid, s)
        for tid, slist in summaries_by_task.items()
        for s in slist
        if (tid, s["ID"]) not in done
    ]
    print(f"      {len(done)} done, {len(todo)} remaining → {raw_path}")

    if not todo:
        _write_passrate(raw_path, rate_path)
        return

    print(f"[4/4] Loading model: {args.model_name} …")
    from common.model import load_model
    _model = load_model(Path(args.model), max_new_tokens=512, load_in_4bit=args.load_in_4bit)
    def model_fn(msgs):
        return _model.chat(msgs)

    for i, (task_id, s) in enumerate(todo, 1):
        print(f"  [{i}/{len(todo)}] {task_id} / {s['ID'][:60]}", flush=True)
        try:
            record = process(s, entries[task_id], model_fn, args.model_name,
                              n_asserts=args.n_asserts)
        except Exception as e:
            print(f"    ERROR: {e}", flush=True)
            record = {
                "task_id": task_id, "summary_id": s["ID"],
                "model": args.model_name, "error": str(e),
            }
        _append(raw_path, record)
        rate_str = f"{record['success_rate']:.3f}" if record.get("success_rate") is not None else "N/A"
        print(f"    success_rate={rate_str}", flush=True)

    _model.unload()

    _write_passrate(raw_path, rate_path)
    print(f"\nDone.")


if __name__ == "__main__":
    main()
