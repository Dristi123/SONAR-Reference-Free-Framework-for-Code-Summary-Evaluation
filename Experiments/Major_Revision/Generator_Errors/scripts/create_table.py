import csv
from collections import defaultdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
RESULTS_DIR = SCRIPT_DIR.parent / "results"
GENERATORS = ["gemini", "qwen", "olmo"]
CORRECT, WRONG = 0.95, 0.5


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def number(value):
    return None if value == "" else float(value)


def pct(part, whole):
    return f"{100 * part / whole:.1f}% ({part}/{whole})"


def correctness_errors(data):
    rows = []
    scored = [r for r in data if all(r[g] is not None for g in GENERATORS)]
    for g in GENERATORS:
        others = [o for o in GENERATORS if o != g]
        adequate = [r for r in scored if any(r[o] >= CORRECT for o in others)]
        rows.append((g, "wrong code on summaries another generator implemented correctly",
                     pct(sum(r[g] < WRONG for r in adequate), len(adequate))))
    return [("Same summary, different generators", *r) for r in rows]


def same_generator(data):
    rows = []
    for g in ["gemini"]:
        by_function = defaultdict(list)
        for r in data:
            if r[g] is not None:
                by_function[r["task_id"]].append(r[g])
        zero = [(t, v) for t, values in by_function.items() for v in values if v == 0]
        solved = {t for t, values in by_function.items() if any(v >= CORRECT for v in values)}
        functions = {t for t, _ in zero}
        rows += [(g, "zero-scored summaries whose function has a correctly implemented summary",
                  pct(sum(t in solved for t, _ in zero), len(zero))),
                 (g, "functions with a zero-scored summary that also have a correctly implemented summary",
                  pct(len(functions & solved), len(functions)))]
    return [("Same generator, different summaries", *r) for r in rows]


def main():
    data = [{"task_id": r["task_id"], **{g: number(r[g]) for g in GENERATORS}}
            for r in read_csv(SCRIPT_DIR / "correctness_by_generator.csv")]
    rows = correctness_errors(data) + same_generator(data)
    RESULTS_DIR.mkdir(exist_ok=True)
    with open(RESULTS_DIR / "generator_errors.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["analysis", "generator", "measure", "value"])
        w.writerows(rows)


if __name__ == "__main__":
    main()
