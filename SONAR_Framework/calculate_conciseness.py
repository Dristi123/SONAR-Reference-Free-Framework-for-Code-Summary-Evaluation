#!/usr/bin/env python3

import sys
from pathlib import Path
from typing import Any, Dict, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from diff_fuzz import run_from_template_pair

N_COMPRESSIONS = 3


def calculate_conciseness(
    summary: str,
    func_sig: str,
    code_generator,
    compressor,
    template_path: Path,
    threshold: float = 0.95,
) -> Dict[str, Any]:
    compressed_summaries = [compressor(summary) for _ in range(N_COMPRESSIONS)]
    code_a = code_generator(summary, func_sig)

    details = []
    for comp in compressed_summaries:
        ratio  = 1.0 - len(comp) / len(summary) if summary else 0.0
        code_b = code_generator(comp, func_sig)
        result = run_from_template_pair(
            template_path=template_path,
            code_a=code_a,
            code_b=code_b,
            max_cases=1000,
            timeout=60,
        )
        fuzz      = result["score"]
        preserved = fuzz is not None and fuzz >= threshold
        details.append({
            "compressed_summary": comp,
            "compression_ratio":  round(ratio, 4),
            "generated_code":     code_b,
            "fuzz_score":         round(fuzz, 4) if fuzz is not None else None,
            "fuzz_status":        result["status"],
            "behavior_preserved": preserved,
        })

    scored = [d for d in details if d["fuzz_score"] is not None]
    if not scored:
        return {
            "compressions":          details,
            "max_compression_ratio": None,
            "conciseness_score":     None,
        }

    max_ratio = max(
        (d["compression_ratio"] for d in scored if d["behavior_preserved"]),
        default=0.0,
    )
    return {
        "compressions":          details,
        "max_compression_ratio": round(max_ratio, 4),
        "conciseness_score":     round(1.0 - max_ratio, 4),
    }


def score_conciseness(
    summary: str,
    func_sig: str,
    code_generator,
    compressor,
    template_path: Path,
    threshold: float = 0.95,
) -> Optional[float]:
    result = calculate_conciseness(
        summary=summary,
        func_sig=func_sig,
        code_generator=code_generator,
        compressor=compressor,
        template_path=template_path,
        threshold=threshold,
    )
    return result["conciseness_score"]
