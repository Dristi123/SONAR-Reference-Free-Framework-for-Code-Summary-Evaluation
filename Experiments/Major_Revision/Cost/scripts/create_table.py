import csv
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, median

SCRIPT_DIR = Path(__file__).resolve().parent
RESULTS_DIR = SCRIPT_DIR.parent / "results"
NO_VALID_RESULT = {"timeout", "all_discarded", "no_valid_inputs", "exec_error", "harness_error"}
USD_PER_M_INPUT, USD_PER_M_OUTPUT = 0.30, 2.50
FUNCTIONS_PER_SUMMARY = 9
CALLS = {"Correctness": {"gemini": 1}, "Conciseness": {"gemini": 7},
         "Abstraction": {"gemini": 3, "olmo": 3, "qwen": 3}}


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def stats(values):
    return f"{mean(values):.2f}", f"{median(values):.2f}"


def pct(part, whole):
    return f"{100 * part / whole:.1f}% ({part}/{whole})"


def totals(gemini, local, fuzz, joern):
    def avg(rows, col):
        return mean(float(r[col]) for r in rows)

    group = {"Correctness": "correctness+conciseness", "Conciseness": "correctness+conciseness",
             "Abstraction": "abstraction"}
    fuzz_seconds = {dim: defaultdict(float) for dim in ("correctness", "conciseness")}
    for r in fuzz:
        fuzz_seconds[r["dimension"]][r["summary_id"]] += float(r["seconds"])
    out = []
    for dim, calls in CALLS.items():
        g = gemini[group[dim]]
        n = calls["gemini"]
        generated = n * (avg(g, "output_tokens") + avg(g, "thinking_tokens"))
        seconds = n * avg(g, "seconds")
        usd = n * (avg(g, "input_tokens") * USD_PER_M_INPUT
                   + (avg(g, "output_tokens") + avg(g, "thinking_tokens")) * USD_PER_M_OUTPUT) / 1e6
        gpu = 0.0
        for model in ("olmo", "qwen"):
            if model in calls:
                rows = [c for c in local if c["model"] == model]
                generated += calls[model] * avg(rows, "output_tokens")
                gpu += calls[model] * avg(rows, "seconds")
        if dim == "Abstraction":
            other = avg(joern, "joern_seconds") + avg(joern, "similarity_seconds")
        else:
            other = mean(fuzz_seconds[dim.lower()].values())
        out.append((dim, f"{generated:.0f}", f"{seconds + gpu + other:.1f}", f"{gpu:.1f}",
                    f"{usd:.4f}"))
    tokens = f"{sum(float(r[1]) for r in out):.0f}"
    gpu, usd = f"{sum(float(r[3]) for r in out):.1f}", f"{sum(float(r[4]) for r in out):.4f}"
    out.append(("Total (dimensions in parallel)", tokens, f"{max(float(r[2]) for r in out):.1f}", gpu, usd))
    return out


def main():
    rows = []
    gemini = defaultdict(list)
    for r in read_csv(SCRIPT_DIR / "gemini_calls.csv"):
        gemini[r["dimensions"]].append(r)
    for dims, calls in gemini.items():
        name = f"Gemini 2.5 Flash ({dims})"
        for col, measure in (("input_tokens", "input tokens per call"), ("output_tokens", "output tokens per call"),
                             ("thinking_tokens", "thinking tokens per call"), ("seconds", "seconds per call")):
            rows.append(("Gemini calls", name, measure, *stats([float(c[col]) for c in calls])))

    local = read_csv(SCRIPT_DIR / "local_calls.csv")
    per_summary = defaultdict(float)
    for model in ("olmo", "qwen"):
        calls = [c for c in local if c["model"] == model]
        name = {"olmo": "OLMo-3.1-32B-Instruct", "qwen": "Qwen2.5-Coder-32B"}[model]
        for col, measure in (("input_tokens", "input tokens per call"), ("output_tokens", "output tokens per call"),
                             ("seconds", "seconds per call")):
            rows.append(("Abstraction", name, measure, *stats([float(c[col]) for c in calls])))
        for c in calls:
            per_summary[c["summary_id"]] += float(c["seconds"])
    rows.append(("Abstraction", "OLMo + Qwen (6 calls)", "seconds per summary", *stats(list(per_summary.values()))))

    joern = read_csv(SCRIPT_DIR / "joern_runs.csv")
    rows.append(("Abstraction", "Joern (9 functions)", "seconds per summary",
                 *stats([float(r["joern_seconds"]) for r in joern])))
    rows.append(("Abstraction", "Pairwise similarity (36 pairs)", "seconds per summary",
                 *stats([float(r["similarity_seconds"]) for r in joern])))

    fuzz = [r for r in read_csv(SCRIPT_DIR / "fuzzing_runs.csv") if int(r["comparison"]) < 3]
    for dim in ("correctness", "conciseness"):
        runs = [r for r in fuzz if r["dimension"] == dim]
        fuzzed = [float(r["seconds"]) for r in runs if r["status"] != "stub"]
        total = defaultdict(float)
        for r in runs:
            total[r["summary_id"]] += float(r["seconds"])
        rows.append((dim.capitalize(), "Differential fuzzing", "seconds per comparison (3 runs)", *stats(fuzzed)))
        rows.append((dim.capitalize(), "Differential fuzzing", "seconds per summary", *stats(list(total.values()))))

    failures = []
    for dim in ("correctness", "conciseness"):
        status = Counter(r["status"] for r in fuzz if r["dimension"] == dim)
        n = sum(status.values())
        failures.append((dim.capitalize(), "Stub code (scored 0 without fuzzing)", pct(status["stub"], n)))
        failures.append((dim.capitalize(), "Fuzzing comparison without a valid result (left unscored)",
                         pct(sum(v for k, v in status.items() if k in NO_VALID_RESULT), n)))
    functions = FUNCTIONS_PER_SUMMARY * len(joern)
    no_graph = functions - sum(int(r["functions_with_graph"]) for r in joern)
    failures.append(("Abstraction", "Function without a Joern graph (AST fallback)", pct(no_graph, functions)))
    capped = sum(int(c["output_tokens"]) >= 512 for c in local)
    failures.append(("Abstraction", "Local generation cut at the 512-token limit", pct(capped, len(local))))

    RESULTS_DIR.mkdir(exist_ok=True)
    with open(RESULTS_DIR / "cost_per_summary.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["dimension", "generated_tokens", "seconds", "gpu_seconds", "usd"])
        w.writerows(totals(gemini, local, fuzz, joern))
    with open(RESULTS_DIR / "cost_table.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["dimension", "component", "measure", "mean", "median"])
        w.writerows(rows)
    with open(RESULTS_DIR / "execution_failures.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["dimension", "failure", "share"])
        w.writerows(failures)


if __name__ == "__main__":
    main()
