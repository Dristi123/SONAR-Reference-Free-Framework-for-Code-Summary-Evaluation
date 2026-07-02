#!/usr/bin/env python3

import argparse
import json
import os
import re
from pathlib import Path

SCRIPT_DIR     = Path(__file__).resolve().parent
SUMMARIES_PATH = SCRIPT_DIR.parent / "summary_pool.jsonl"
HE_FUZZ_READY  = SCRIPT_DIR.parent / "dataset" / "HE.jsonl"
COFFE_STRESS   = SCRIPT_DIR / "stressful_testcases.json"
OUT_DIR        = SCRIPT_DIR
DEFAULT_MODEL  = Path(os.environ.get("OPT_MODEL_PATH", "qwen2_5_coder_32b"))

from prompts import build_messages
from common.executor import run_test_suite, extract_code
from common.coffe_executor import compare_efficiency


def load_he_fuzz_ready() -> dict:
    entries = {}
    with open(HE_FUZZ_READY) as f:
        for line in f:
            r = json.loads(line)
            entries[r["task_id"]] = r
    return entries


def load_stress_tests() -> dict:
    with open(COFFE_STRESS) as f:
        raw = json.load(f)
    result = {}
    for prompt_key, tests in raw.items():
        m = re.search(r"def\s+(\w+)\s*\(", prompt_key)
        if m:
            ep = m.group(1)
            result[ep] = [t["input"] for t in tests if t.get("input")]
    return result


def load_summaries(task_ids: set | None, summaries_path: Path = SUMMARIES_PATH) -> list[dict]:
    rows = []
    with open(summaries_path) as f:
        for line in f:
            r = json.loads(line)
            if r.get("dataset") != "HumanEval":
                continue
            tid_num = int(r["task_id"].split("_")[1])
            if task_ids and tid_num not in task_ids:
                continue
            rows.append(r)
    return rows


def load_done(out_path: Path) -> set:
    done = set()
    if out_path.exists():
        with open(out_path) as f:
            for line in f:
                r = json.loads(line)
                done.add(r["ID"])
    return done


def append_result(out_path: Path, record: dict):
    with open(out_path, "a") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def _get_func_sig(entry: dict) -> str:
    for line in entry["prompt"].splitlines():
        if line.strip().startswith("def "):
            return line.strip()
    return f"def {entry['entry_point']}(...):"


def _get_imports(entry: dict) -> str:
    lines = []
    for line in entry["prompt"].splitlines():
        if line.strip().startswith("def "):
            break
        if line.strip().startswith("import") or line.strip().startswith("from"):
            lines.append(line)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model",    type=str, default=str(DEFAULT_MODEL),
                        help="Model path, or 'gemini'")
    parser.add_argument("--out",      type=Path,
                        help="Output JSONL path (default: results/<model_name>.jsonl)")
    parser.add_argument("--summaries", type=Path, default=SUMMARIES_PATH,
                        help="Summaries JSONL to read (default: summary_pool.jsonl)")
    parser.add_argument("--task-ids", type=str, default=None,
                        help="Comma-separated HE task IDs to run, e.g. 0,12,107")
    parser.add_argument("--max-rows", type=int, default=None,
                        help="Stop after the first N rows of --summaries (e.g. 1085 to match an earlier dataset boundary)")
    parser.add_argument("--dry-run",  action="store_true")
    args = parser.parse_args()

    task_ids = (
        {int(x) for x in args.task_ids.split(",")}
        if args.task_ids else None
    )
    model_name = Path(args.model).name if args.model != "gemini" else args.model

    out_path = args.out or OUT_DIR / f"{model_name}.jsonl"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print("Loading data …")
    he_entries = load_he_fuzz_ready()
    stress_by_ep = load_stress_tests()
    summaries = load_summaries(task_ids, args.summaries)

                                                 
    summaries = [s for s in summaries if s["task_id"] in he_entries]

    if args.max_rows is not None:
        summaries = summaries[:args.max_rows]

    print(f"  {len(summaries)} summary rows")
    print(f"  {sum(1 for s in summaries if he_entries[s['task_id']]['entry_point'] in stress_by_ep)} "
          f"have COFFE stress tests")

    if args.dry_run:
        s = summaries[0]
        entry = he_entries[s["task_id"]]
        msgs = build_messages(s["summary"], _get_func_sig(entry))
        print("\n=== DRY RUN — sample prompt ===")
        print("SYSTEM:", msgs[0]["content"])
        print("USER:", msgs[1]["content"])
        return

    done = load_done(out_path)
    todo = [s for s in summaries if s["ID"] not in done]
    print(f"  {len(done)} done, {len(todo)} remaining → {out_path}\n")

    if not todo:
        print("Nothing to do.")
        return

    from common.model import load_model
    model = load_model(args.model, max_new_tokens=512)

    print(f"{'#':>4}  {'task_id':<16}  {'corr':>5}  {'abs':>5}  {'pass':>5}  {'speedup':>8}  ID")
    print("-" * 90)

    for i, summ in enumerate(todo, 1):
        sid      = summ["ID"]
        tid      = summ["task_id"]
        corr     = summ.get("correctness")
        abst     = summ.get("abstraction")
        conc     = summ.get("conciseness")
        flu      = summ.get("fluency")
        entry    = he_entries[tid]
        ep       = entry["entry_point"]
        func_sig = _get_func_sig(entry)
        imports  = _get_imports(entry)
        canonical = entry["code"]
        he_tests  = entry["test_case_list"]
        stress_inputs = stress_by_ep.get(ep, [])

        try:
            msgs    = build_messages(summ["summary"], func_sig)
            raw_gen = model.chat(msgs, temperature=None)
            gen_code = extract_code(raw_gen, func_sig)
            runnable = (imports + "\n" + gen_code).strip() if imports else gen_code
        except Exception as e:
            record = {"ID": sid, "task_id": tid, "error_gen": str(e)}
            append_result(out_path, record)
            print(f"{i:>4}  {tid:<16}  ERROR generating: {e}", flush=True)
            continue


        impl = run_test_suite(he_tests, runnable, timeout=10)
        pass_rate = impl["pass_rate"]

   
        speedup = None
        speedup_note = ""
        if pass_rate == 1.0 and stress_inputs:
            try:
                eff = compare_efficiency(canonical, runnable, ep, stress_inputs, timeout=10)
                speedup = eff["mean_speedup"]
            except Exception as e:
                speedup_note = f"error:{e}"
        elif pass_rate < 1.0:
            speedup_note = "correctness_failed"
        else:
            speedup_note = "no_stress_inputs"

        record = {
            "ID":               sid,
            "task_id":          tid,
            "model":            model_name,
            "correctness":      corr,
            "abstraction":      abst,
            "conciseness":      conc,
            "fluency":          flu,
            "summary":          summ["summary"],
            "func_sig":         func_sig,
            "generated_code":   gen_code,
            "pass_rate":        pass_rate,
            "passed":           impl["passed"],
            "total_tests":      impl["total"],
            "mean_speedup":     speedup,
            "speedup_note":     speedup_note,
            "n_stress_inputs":  len(stress_inputs),
        }
        append_result(out_path, record)

        corr_str    = f"{corr:.3f}" if corr is not None else "  N/A"
        abst_str    = f"{abst:.3f}" if abst is not None else "  N/A"
        pass_str    = f"{pass_rate:.2f}"
        speedup_str = f"{speedup:.3f}x" if speedup is not None else speedup_note or "N/A"
        print(
            f"{i:>4}  {tid:<16}  {corr_str:>5}  {abst_str:>5}  "
            f"{pass_str:>5}  {speedup_str:>8}  {sid}",
            flush=True,
        )

    model.unload()
    print(f"\nDone → {out_path}")


if __name__ == "__main__":
    main()
