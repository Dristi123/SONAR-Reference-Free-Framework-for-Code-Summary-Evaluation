#!/usr/bin/env python3
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_PATH = SCRIPT_DIR / "rq1_data.jsonl"
OUT_PATH = SCRIPT_DIR / "sonar_scores.jsonl"


def main():
    score_by_id_dim = {}
    with DATA_PATH.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            score_by_id_dim[(r["id_a"], r["dimension"])] = r["sonar_score_a"]
            score_by_id_dim[(r["id_b"], r["dimension"])] = r["sonar_score_b"]

    with OUT_PATH.open("w", encoding="utf-8") as f:
        for (summary_id, dim), score in score_by_id_dim.items():
            f.write(json.dumps({"summary_id": summary_id, "dim": dim, "score": score},
                                ensure_ascii=False) + "\n")

    print(f"[+] {len(score_by_id_dim)} scores -> {OUT_PATH}")


if __name__ == "__main__":
    main()
