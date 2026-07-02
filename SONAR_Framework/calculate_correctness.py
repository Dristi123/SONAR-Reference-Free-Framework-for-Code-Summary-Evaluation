#!/usr/bin/env python3

import ast
import sys
from pathlib import Path
from typing import Optional, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from diff_fuzz import run_from_template


def _is_stub(code: str) -> Tuple[bool, str]:
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return True, f"syntax_error:{e}"

    funcs = [n for n in tree.body if isinstance(n, ast.FunctionDef)]
    if not funcs:
        return True, "no_function_defined"

    body = funcs[0].body


    def _is_str_node(node):
        return (isinstance(node, ast.Constant) and isinstance(node.value, str)
                or isinstance(node, ast.Str))

    if body and isinstance(body[0], ast.Expr) and _is_str_node(body[0].value):
        body = body[1:]

    if not body:
        return True, "empty_body"

    if len(body) == 1:
        stmt = body[0]
        if isinstance(stmt, ast.Pass):
            return True, "pass_only"
        if isinstance(stmt, ast.Raise):
            return True, "raise_only"
        if isinstance(stmt, ast.Return):
            if stmt.value is None:
                return True, "bare_return"
            if isinstance(stmt.value, ast.Constant) and stmt.value.value is None:
                return True, "return_none"

    return False, ""


def score_correctness(
    generated_code: str,
    template_path: Path,
    n_runs: int = 3,
    timeout: int = 60,
    max_cases: int = 1000,
) -> Optional[float]:
    stub, _ = _is_stub(generated_code)
    if stub:
        return 0.0

    result = run_from_template(
        template_path=template_path,
        generated_code=generated_code,
        n_runs=n_runs,
        timeout=timeout,
        max_cases=max_cases,
    )
    return result["score"]
