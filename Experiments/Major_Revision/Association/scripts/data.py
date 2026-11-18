import sys
from pathlib import Path

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
RESULTS_DIR = SCRIPT_DIR.parent / "results"
JUDGE_SCORES = SCRIPT_DIR.parents[1] / "LLM_Judges" / "scripts" / "judge_scores.csv"

sys.path.insert(0, str(SCRIPT_DIR.parents[2] / "RQ2" / "scripts"))
from downstream import METRICS, load_meta, outcomes

FAMILIES = {"sonar": ["correctness", "abstraction", "conciseness", "fluency"],
            "crupi": ["content_adequacy", "conciseness", "fluency"],
            "coderpe": ["coherence", "consistency", "fluency", "relevance"],
            "claude": ["correctness", "abstraction", "conciseness"],
            "reference": ["bleu4", "rouge_l", "meteor", "bleurt", "bertscore_f1"]}
JUDGES = ["sonar", "crupi", "coderpe", "claude"]
CONCISENESS_ROWS = {"sonar:conciseness", "crupi:conciseness", "claude:conciseness", "coderpe:relevance"}


def judge_scores():
    scores = pd.read_csv(JUDGE_SCORES).set_index("summary_id")
    scores.columns = [c.replace("_", ":", 1) for c in scores.columns]
    return scores.dropna()


def frames():
    meta = load_meta()
    judges = judge_scores()
    out = {}
    for metric, rows in outcomes().items():
        recs = []
        for sid, model, y in rows:
            if y is None or sid not in judges.index or sid not in meta:
                continue
            m = meta[sid]
            recs.append({"id": sid, "y": y, "llm": model, "task": m["task_id"], "len": len(m["summary"].split()),
                         **{f"{f}:{d}": m[d] for f in ("sonar", "reference") for d in FAMILIES[f]},
                         **judges.loc[sid].to_dict()})
        out[metric] = pd.DataFrame(recs)
    return out
