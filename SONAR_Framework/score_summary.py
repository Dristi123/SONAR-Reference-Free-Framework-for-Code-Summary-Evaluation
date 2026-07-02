#!/usr/bin/env python3

import ast
import sys
from pathlib import Path
from typing import Optional, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = SCRIPT_DIR / "templates"
sys.path.insert(0, str(SCRIPT_DIR))
from calculate_correctness import score_correctness
from calculate_conciseness import score_conciseness
from calculate_abstraction import score_abstraction
from calculate_fluency import score_fluency, FluencyScorer


def _template_path(task_id: str) -> Optional[Path]:
    safe_id = task_id.replace("/", "_").replace(" ", "_")
    path = TEMPLATES_DIR / f"{safe_id}.py"
    return path if path.exists() else None


def _func_sig(code: str) -> str:
    tree = ast.parse(code)
    func = next(n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)))
    sig_cls = type(func)
    sig_node = sig_cls(
        name=func.name, args=func.args, body=[ast.Pass()],
        decorator_list=[], returns=func.returns, type_comment=None,
    )
    ast.fix_missing_locations(sig_node)
    return ast.unparse(sig_node).split("\n")[0]


def score_summary(
    summary: str,
    code: str,
    task_id: str,
    code_generator,
    compressor,
    generators,
    fluency_scorer: Optional[FluencyScorer] = None,
) -> Tuple[Optional[float], Optional[float], Optional[float], float]:
    func_sig = _func_sig(code)
    template_path = _template_path(task_id)

    if template_path is not None:
        generated_code = code_generator(summary, func_sig)
        correctness = score_correctness(generated_code, template_path)
        conciseness = score_conciseness(
            summary, func_sig, code_generator, compressor, template_path
        )
    else:
        correctness = None
        conciseness = None

    abstraction = score_abstraction(summary, func_sig, generators)

    fluency = score_fluency(summary, fluency_scorer)

    return correctness, abstraction, conciseness, fluency
