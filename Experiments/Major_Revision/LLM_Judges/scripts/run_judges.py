import argparse
import csv
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
EXPERIMENTS = SCRIPT_DIR.parents[2]
SUMMARIES = EXPERIMENTS / "RQ2" / "scripts" / "summary_pool.jsonl"
PROMPTS = json.loads((SCRIPT_DIR / "judge_prompts.json").read_text())
OUT = SCRIPT_DIR / "judge_scores.csv"

sys.path.insert(0, str(EXPERIMENTS / "RQ1" / "scripts"))
from rq1_llm_only_baseline import CLAUDE_MODEL, _parse_score, _score_prompt

GPT_MODEL = "gpt-4o-2024-08-06"
DIMS = {"crupi": ["content_adequacy", "conciseness", "fluency"],
        "coderpe": ["coherence", "consistency", "fluency", "relevance"],
        "claude": ["correctness", "abstraction", "conciseness"]}
CRUPI_FIELDS = {"content_adequacy": r"content\s*adequacy", "conciseness": r"conciseness",
                "fluency": r"fluency(?:\s*&\s*understandability)?"}


def crupi(client, code, summary):
    p = PROMPTS["crupi"]
    prompt = p["template"].replace("<LANGUAGE>", "Python").replace("<FUNCTION>", code).replace("<COMMENT>", summary)
    text = client.chat.completions.create(
        model=GPT_MODEL, temperature=0.2, seed=123,
        messages=[{"role": "system", "content": p["system"]}, {"role": "user", "content": prompt + "#"}],
    ).choices[0].message.content
    out = {}
    for name, pattern in CRUPI_FIELDS.items():
        m = re.search(pattern + r"[^0-9]{0,40}?([1-5])", text, re.I)
        out[name] = int(m.group(1)) if m else None
    return out


def coderpe(client, code, summary):
    p = PROMPTS["coderpe"]
    out = {}
    for d in p["dimensions"]:
        prompt = p["template"].format(role_description=p["role"], role_dimension=d["role"], criterion_name=d["name"],
                                      criterion_task=d["criterion"], example_data=d["example"],
                                      code_to_display=code, generated=summary)
        text = client.chat.completions.create(
            model=GPT_MODEL, messages=[{"role": "user", "content": prompt}], response_format={"type": "text"},
            temperature=1, max_completion_tokens=1000, top_p=1, frequency_penalty=0, presence_penalty=0, store=False,
        ).choices[0].message.content.strip()
        labelled = re.search(re.escape(d["name"]) + r"[^0-9\n]{0,30}?([0-4])\b", text, re.I)
        if labelled:
            out[d["name"].lower()] = int(labelled.group(1))
            continue
        numbers = re.findall(r"\d+", " ".join(text.split()))
        value = int(numbers[-1]) if numbers else None
        out[d["name"].lower()] = value if value is not None and value <= 4 and len(text) <= 30 else None
    return out


def claude(client, code, summary):
    out = {}
    for dim in DIMS["claude"]:
        response = client.messages.create(model=CLAUDE_MODEL, max_tokens=16,
                                          messages=[{"role": "user", "content": _score_prompt(code, summary, dim)}])
        out[dim] = _parse_score(next((b.text for b in response.content if b.type == "text"), ""))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()
    if not os.environ.get("OPENAI_API_KEY") or not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("OPENAI_API_KEY and ANTHROPIC_API_KEY must be set")
    import anthropic
    import openai
    clients = {"crupi": openai.OpenAI(), "coderpe": openai.OpenAI(), "claude": anthropic.Anthropic()}
    judges = {"crupi": crupi, "coderpe": coderpe, "claude": claude}

    code = {}
    with open(SCRIPT_DIR / "function_code.jsonl") as f:
        for line in f:
            r = json.loads(line)
            code[r["task_id"]] = r["code"]
    with open(SUMMARIES) as f:
        items = [json.loads(line) for line in f]

    def score(item):
        row = {"summary_id": item["ID"]}
        for judge, fn in judges.items():
            for dim, value in fn(clients[judge], code[item["task_id"]], item["summary"]).items():
                row[f"{judge}_{dim}"] = value
        return row

    with ThreadPoolExecutor(args.workers) as ex:
        rows = list(ex.map(score, items))
    fields = ["summary_id"] + [f"{j}_{d}" for j in judges for d in DIMS[j]]
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fields)
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
