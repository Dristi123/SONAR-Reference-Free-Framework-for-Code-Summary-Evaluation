#!/usr/bin/env python3
import argparse
import csv
import json
import os
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent

SCORER_CHOICES = ("claude", "gemini")

CLAUDE_MODEL = "claude-opus-4-8"

GEMINI_MODEL = "gemini-3.1-pro-preview"
GEMINI_PROJECT = os.environ.get("GEMINI_VERTEX_PROJECT", "your-gcp-project-id")
GEMINI_LOCATION = "global"

GT_PATH = SCRIPT_DIR / "groundtruth.csv"

DIMS = ["correctness", "abstraction", "conciseness"]

_DIM_EXPLAIN = {
    "correctness": "A summary is correct if it accurately describes the code's behavior.",
    "abstraction": "A summary is abstract if it avoids leaking unnecessary implementation details.",
    "conciseness": "A summary is concise if it is without redundancy or filler.",
}

_CODE_TRUNCATE = 2000


def _load_jsonl(path: Path) -> List[Dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def _load_groundtruth(path: Path) -> List[Dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_pairs_and_summaries(dims: List[str]) -> Tuple[List[Dict], Dict[str, Dict]]:
    pairs: List[Dict] = []
    summary_map: Dict[str, Dict] = {}

    for r in _load_groundtruth(GT_PATH):
        dim = r["dimension"]
        if dim not in dims:
            continue
        pairs.append({"id_a": r["id_a"], "id_b": r["id_b"], "dimension": dim})
        summary_map[r["id_a"]] = {"summary": r["summary_a"], "code": r["code"]}
        summary_map[r["id_b"]] = {"summary": r["summary_b"], "code": r["code"]}

    return pairs, summary_map


def _score_prompt(code: str, summary: str, dim: str) -> str:
    snippet = code[:_CODE_TRUNCATE] + (" ..." if len(code) > _CODE_TRUNCATE else "")
    return (
        f"You are evaluating a code summary on the dimension of **{dim}**.\n\n"
        f"{_DIM_EXPLAIN[dim]}\n\n"
        f"Code:\n```python\n{snippet}\n```\n\n"
        f"Summary:\n{summary}\n\n"
        f"Rate this summary on **{dim}** from 0.0 (worst) to 1.0 (best).\n"
        f"Respond with ONLY a floating-point number between 0.0 and 1.0. "
        f"No explanation."
    )


def _parse_score(raw: str) -> Optional[float]:
    m = re.search(r'\b(0(?:\.\d+)?|1(?:\.0+)?|\.\d+)\b', raw)
    if m:
        return round(min(max(float(m.group(1)), 0.0), 1.0), 4)
    return None


class ClaudeScorer:
    def __init__(self):
        import anthropic
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise RuntimeError("ANTHROPIC_API_KEY not set")
        self._client = anthropic.Anthropic()

    def score(self, code: str, summary: str, dim: str) -> Optional[float]:
        response = self._client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=16,
            messages=[{"role": "user", "content": _score_prompt(code, summary, dim)}],
        )
        raw = next((b.text for b in response.content if b.type == "text"), "")
        return _parse_score(raw)


class GeminiScorer:
    def __init__(self):
        import google.genai as genai
        self._client = genai.Client(
            vertexai=True, project=GEMINI_PROJECT, location=GEMINI_LOCATION,
        )

    def score(self, code: str, summary: str, dim: str) -> Optional[float]:
        prompt = _score_prompt(code, summary, dim)
        delay = 30
        for attempt in range(5):
            try:
                response = self._client.models.generate_content(
                    model=GEMINI_MODEL, contents=prompt,
                )
                return _parse_score(response.text or "")
            except Exception as e:
                if ("429" in str(e) or "RESOURCE_EXHAUSTED" in str(e)) and attempt < 4:
                    time.sleep(delay)
                    delay = min(delay * 2, 300)
                    continue
                raise


def score_all_summaries(
    pairs: List[Dict],
    summary_map: Dict[str, Dict],
    scorer,
    dims: List[str],
    out_path: Path,
    workers: int = 1,
) -> None:
    needed: set = set()
    for rec in pairs:
        dim = rec["dimension"]
        if dim not in dims:
            continue
        needed.add((rec["id_a"], dim))
        needed.add((rec["id_b"], dim))

    print(f"  Summaries to score: {len(needed)}", flush=True)

    fout = out_path.open("w", encoding="utf-8")
    write_lock = threading.Lock()
    progress = {"done": 0}
    log_every = max(1, len(needed) // 100)

    def _work(item):
        sid, dim = item
        entry = summary_map[sid]
        return sid, dim, scorer.score(entry["code"], entry["summary"], dim)

    def _on_result(sid, dim, score):
        with write_lock:
            fout.write(json.dumps({"summary_id": sid, "dim": dim, "score": score},
                                   ensure_ascii=False) + "\n")
            fout.flush()
            progress["done"] += 1
            if progress["done"] % log_every == 0:
                print(f"  [{progress['done']}/{len(needed)}] scored {sid}/{dim} -> {score}",
                      flush=True)

    if workers <= 1:
        for item in needed:
            _on_result(*_work(item))
    else:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = [pool.submit(_work, item) for item in needed]
            for fut in as_completed(futures):
                _on_result(*fut.result())

    fout.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dims", nargs="+", choices=DIMS, default=DIMS)
    parser.add_argument("--scorer", choices=SCORER_CHOICES, required=True)
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()

    out_path = SCRIPT_DIR / f"llm_scores_{args.scorer}.jsonl"

    pairs, summary_map = load_pairs_and_summaries(args.dims)
    dims_present = sorted({r["dimension"] for r in pairs})

    scorer = ClaudeScorer() if args.scorer == "claude" else GeminiScorer()

    score_all_summaries(pairs, summary_map, scorer, dims_present, out_path, workers=args.workers)
    print(f"[+] Scores -> {out_path}", flush=True)


if __name__ == "__main__":
    main()
