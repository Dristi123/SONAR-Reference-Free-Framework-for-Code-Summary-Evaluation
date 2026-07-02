#!/usr/bin/env python3


import ast
import re
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path
from typing import List, Optional


_PREAMBLE = """\
import atheris
import sys
import random
from typing import List, Tuple, Dict, Optional, Any, Set
from collections import defaultdict, Counter, OrderedDict
from itertools import combinations, permutations, product
from functools import reduce
import math, re, hashlib, copy, string
"""


_TEMPLATE = """\
{future_imports}{preamble}
total = 0
matches = 0
_discarded = 0
MAX_CASES = {max_cases}
_attempts = 0
MAX_ATTEMPTS = MAX_CASES * 5

{context}
{solve_a_impl}

{solve_b_impl}


def solve_a(*args, **kwargs):
    try:
        return (True, _solve_a_impl(*args, **kwargs))
    except Exception:
        return (False, None)


def solve_b(*args, **kwargs):
    try:
        return (True, _solve_b_impl(*args, **kwargs))
    except Exception:
        return (False, None)


def _eq(a, b, tol=1e-9):
    \"\"\"Equality with float tolerance and NaN handling.\"\"\"
    if isinstance(a, float) and isinstance(b, float):
        if a != a and b != b:   # both NaN
            return True
        if a != a or b != b:    # one NaN
            return False
        if abs(a) == float("inf") or abs(b) == float("inf"):
            return a == b
        return abs(a - b) <= tol * max(abs(a), abs(b), 1.0)
    return a == b


def TestOneInput(data):
    global total, matches, _discarded, _attempts
    _attempts += 1

    if total >= MAX_CASES or _attempts >= MAX_ATTEMPTS:
        raise SystemExit(0)

    fdp = atheris.FuzzedDataProvider(data)

    try:
{binding_code}
    except Exception:
        return  # input generation failed — fdp exhausted or type error in binding

    a_ok, a_val = out_a
    b_ok, b_val = out_b

    if not a_ok and not b_ok:
        # Case 1: both raised — both agree input is invalid
        total += 1
        matches += 1
    elif a_ok and not b_ok:
        # Case 2: reference succeeded, generated raised — mismatch
        total += 1
        print(f"Mismatch: A returned {{a_val!r}}, B raised")
    elif not a_ok and b_ok:
        # Case 3: reference raised, generated succeeded — discard (no ground truth)
        _discarded += 1
    else:
        # Case 4: both succeeded — compare outputs
        total += 1
        if _eq(a_val, b_val):
            matches += 1
        else:
            print(f"Mismatch: A={{a_val!r}}, B={{b_val!r}}")


def main():
    atheris.Setup(sys.argv, TestOneInput)
    try:
        atheris.Fuzz()
    except (SystemExit, Exception):
        pass
    finally:
        print("\\n=== Fuzzing Summary ===")
        print(f"Total test cases: {{total}}")
        print(f"Matches (semantically equivalent): {{matches}}")
        print(f"Discarded inputs: {{_discarded}}")
        if total > 0:
            print(f"Semantic agreement score: {{matches / total:.2%}}")
        else:
            print("No valid inputs tested.")


if __name__ == "__main__":
    main()
"""


_BINDING_PROMPT = """\
You are completing the input binding logic inside a Python Atheris fuzzing script.

The function under test is:

```python
{reference_code}
```

Natural language description:
{description}
{seed_section}
Your task: write ONLY the code that goes inside the `try:` block of `TestOneInput`.
The surrounding structure looks like this:

```python
def TestOneInput(data):
    global total, matches
    if total >= MAX_CASES:
        raise Exception
    fdp = atheris.FuzzedDataProvider(data)
    try:
        # YOUR CODE HERE

        total += 1
        if out_a == out_b:
            matches += 1
    except Exception:
        pass
```

Rules:
- Use `fdp.Consume*` methods to generate inputs that match the expected argument types.
  IMPORTANT: derive the input domain from BOTH the description AND the reference code.
  Only test inputs that the description says the function accepts — do not test edge cases
  (e.g. non-paren characters, empty strings, negatives) that the description does not mention.
- Call `out_a = solve_a(...)` and `out_b = solve_b(...)` with identical arguments.
- End your code just before `total += 1` — do NOT include that line.
- For integers:  `fdp.ConsumeIntInRange(min, max)`
- For strings: use `fdp.ConsumeUnicodeNoSurrogates(fdp.ConsumeIntInRange(1, 100))`.
  CRITICAL EXCEPTION: if the description says the string consists of specific characters
  (e.g. "string of parentheses", "string of digits", "binary string") OR if the function
  body only checks specific characters (e.g. `if c == '(':`) then you MUST restrict to
  those characters using ONLY this exact one-liner pattern (no for loops, no other form):
  `''.join(fdp.PickValueInList(['(', ')']) for _ in range(fdp.ConsumeIntInRange(1, 50)))`
  Replace `['(', ')']` with the actual character set from the description.
- For floats:    `fdp.ConsumeIntInRange(-10000, 10000) / 100.0`
- For booleans:  `fdp.ConsumeBool()`
- For lists:     use `ConsumeIntInRange(1, 10)` for length, then generate elements in a loop
- If a parameter represents the length of another input (e.g. `n` in `func(arr, n)`),
  derive `n` from `len(arr)` — do NOT consume it independently.
- If the function uses `random` or `numpy.random` internally, set a fixed seed immediately
  before EACH call so both implementations experience the same random sequence:
      random.seed(42)
      if _HAS_NUMPY: _fuzz_np.random.seed(42)
      out_a = solve_a(...)
      random.seed(42)
      if _HAS_NUMPY: _fuzz_np.random.seed(42)
      out_b = solve_b(...)
- Output ONLY the binding code — no imports, no function definitions, no try/except wrapper.
"""

_SEED_SECTION = """
Here is an example call to the function (use it to confirm your understanding of the input types):
{seed_example}
"""

_FUZZ_PYTHON = sys.executable

_SCORE_PAT    = re.compile(r"Semantic agreement score:\s*([\d.]+)%")
_TOTAL_PAT    = re.compile(r"Total test cases:\s*(\d+)")
_MATCHES_PAT  = re.compile(r"Matches \(semantically equivalent\):\s*(\d+)")
_DISCARD_PAT  = re.compile(r"Discarded inputs:\s*(\d+)")


STATUS_ALL_MATCH      = "all_match"
STATUS_PARTIAL_MATCH  = "partial_match"
STATUS_NO_MATCH       = "no_match"
STATUS_ALL_DISCARDED  = "all_discarded"
STATUS_NO_INPUTS      = "no_valid_inputs"
STATUS_EXEC_ERROR     = "exec_error"
STATUS_TIMEOUT        = "timeout"

_CRASH_PREFIXES = ("crash-", "slow-", "oom-", "leak-", "timeout-")


def _delete_crash_files() -> None:
    for fname in Path.cwd().iterdir():
        if any(fname.name.startswith(p) for p in _CRASH_PREFIXES):
            fname.unlink(missing_ok=True)


def _run_script(script_path: str, n_runs: int, timeout: int) -> dict:
    scores:   List[float] = []
    statuses: List[str]   = []
    total_cases   = 0
    total_matches = 0

    for run in range(n_runs):
        run_status = STATUS_EXEC_ERROR
        _delete_crash_files()
        try:
            result    = subprocess.run(
                [_FUZZ_PYTHON, script_path],
                capture_output=True, text=True, timeout=timeout,
            )
            combined  = result.stdout + result.stderr
            score_m   = _SCORE_PAT.search(combined)
            total_m   = _TOTAL_PAT.search(combined)
            matches_m = _MATCHES_PAT.search(combined)
            discard_m = _DISCARD_PAT.search(combined)

            if score_m:
                s  = float(score_m.group(1)) / 100.0
                t  = int(total_m.group(1))   if total_m   else 0
                mc = int(matches_m.group(1)) if matches_m else 0
                scores.append(s)
                total_cases   += t
                total_matches += mc
                run_status = (STATUS_ALL_MATCH    if s == 1.0
                              else STATUS_PARTIAL_MATCH if s > 0.0
                              else STATUS_NO_MATCH)
            else:
                t  = int(total_m.group(1))   if total_m   else 0
                dc = int(discard_m.group(1)) if discard_m else 0
                run_status = (STATUS_ALL_DISCARDED if t == 0 and dc > 0
                              else STATUS_NO_INPUTS if t == 0
                              else STATUS_EXEC_ERROR)

        except subprocess.TimeoutExpired:
            run_status = STATUS_TIMEOUT
        finally:
            statuses.append(run_status)

    avg_score = sum(scores) / len(scores) if scores else 0.0

    if scores:
        agg_status = (STATUS_ALL_MATCH    if avg_score == 1.0
                      else STATUS_PARTIAL_MATCH if avg_score > 0.0
                      else STATUS_NO_MATCH)
    elif all(s == STATUS_TIMEOUT        for s in statuses): agg_status = STATUS_TIMEOUT
    elif all(s == STATUS_ALL_DISCARDED  for s in statuses): agg_status = STATUS_ALL_DISCARDED
    elif all(s == STATUS_NO_INPUTS      for s in statuses): agg_status = STATUS_NO_INPUTS
    else:                                                   agg_status = STATUS_EXEC_ERROR

    return {
        "score":   avg_score,
        "status":  agg_status,
        "total":   total_cases,
        "matches": total_matches,
        "n_valid": len(scores),
    }


def _entry_point(code: str) -> str:

    m = re.search(r'^def\s+(\w+)\s*\(', code, re.MULTILINE)
    if m:
        return m.group(1)

    m = re.search(r'^\s*def\s+(\w+)\s*\(', code, re.MULTILINE)
    return m.group(1) if m else "solve"


def _rename_all(code: str, old: str, new: str) -> str:

    class _FunctionRenamer(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            if node.name == old:
                node.name = new
            self.generic_visit(node)
            return node

        def visit_AsyncFunctionDef(self, node):
            if node.name == old:
                node.name = new
            self.generic_visit(node)
            return node

        def visit_Call(self, node):
            self.generic_visit(node)
            if isinstance(node.func, ast.Name) and node.func.id == old:
                node.func.id = new
            return node

    try:
        tree = ast.parse(code)
    except SyntaxError:
        return re.sub(r"\bdef\s+" + re.escape(old) + r"\s*\(", f"def {new}(", code)

    tree = _FunctionRenamer().visit(tree)
    ast.fix_missing_locations(tree)
    return ast.unparse(tree)

def _extract_seed(test_cases: List[str], entry_point: str) -> Optional[str]:
    for tc in (test_cases or []):
        marker = f"{entry_point}("
        start = tc.find(marker)
        if start == -1:
            continue
        start += len(marker)
        depth, end = 1, start
        while end < len(tc) and depth > 0:
            if tc[end] == "(":
                depth += 1
            elif tc[end] == ")":
                depth -= 1
            if depth > 0:
                end += 1
        if depth == 0:
            return tc[start:end].strip()
    return None


def _normalize_to_zero(code: str) -> str:
    lines = code.splitlines()
    indents = [len(l) - len(l.lstrip()) for l in lines if l.strip()]
    if not indents:
        return code
    min_indent = min(indents)
    if min_indent > 0:

        return textwrap.dedent(code)


    non_zero = [i for i in indents if i > 0]
    if not non_zero:
        return code
    base = min(non_zero)
    result = []
    for line in lines:
        if line.strip():
            stripped = len(line) - len(line.lstrip())
            result.append(line[min(base, stripped):])
        else:
            result.append(line)
    return "\n".join(result)


def _fix_block_indentation(code: str) -> str:
    _OPENER = re.compile(
        r'^(\s*)(for|if|elif|else|while|with|try|except|finally|def|class)\b.*:\s*$'
    )
    _CONTINUATION = re.compile(r'^\s*(elif|else|except|finally)\b')
    lines  = code.splitlines()
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = _OPENER.match(line)
        if m:
            block_indent = len(m.group(1))

            j = i + 1
            while j < len(lines) and (
                not lines[j].strip() or lines[j].lstrip().startswith('#')
            ):
                j += 1
            if j < len(lines):
                next_indent = len(lines[j]) - len(lines[j].lstrip())
                if next_indent == block_indent:

                    result.append(line)
                    i += 1
                    while i < len(lines):
                        curr = lines[i]
                        curr_stripped = curr.lstrip()
                        curr_indent   = len(curr) - len(curr_stripped) if curr_stripped else 0
                        if curr_stripped and curr_indent < block_indent:
                            break

                        if (curr_stripped and curr_indent == block_indent
                                and _CONTINUATION.match(curr)):
                            break


                        if block_indent > 0 and not curr_stripped:
                            k = i + 1
                            while k < len(lines) and not lines[k].strip():
                                k += 1
                            if k < len(lines):
                                peek_indent = len(lines[k]) - len(lines[k].lstrip())
                                if peek_indent <= block_indent:
                                    result.append(curr)
                                    i += 1
                                    break
                        if curr_stripped and curr_indent == block_indent:
                            result.append(' ' * (block_indent + 4) + curr_stripped)
                        else:
                            result.append(curr)
                        i += 1
                    continue
        result.append(line)
        i += 1
    return '\n'.join(result)


def _indent(code: str, spaces: int = 8) -> str:
    code = _fix_block_indentation(code)
    code = textwrap.dedent(code)
    pad  = " " * spaces
    return "\n".join(pad + line if line.strip() else line
                     for line in code.splitlines())


def _strip_fences(text: str) -> str:
    text = re.sub(r"^```(?:python)?\s*\n?", "", text.strip(), flags=re.MULTILINE)
    text = re.sub(r"\n?```\s*$", "", text, flags=re.MULTILINE)
    return text.strip()


def _fix_empty_blocks(code: str) -> str:
    lines = code.splitlines()
    result = []
    i = 0
    _BLOCK_RE = re.compile(r'^\s*(for|if|elif|else|while|with|try|except|finally|def|class)\b.*:\s*$')
    while i < len(lines):
        line = lines[i]
        if _BLOCK_RE.match(line):
            current_indent = len(line) - len(line.lstrip())

            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            next_indent = len(lines[j]) - len(lines[j].lstrip()) if j < len(lines) else 0
            if next_indent <= current_indent:
                result.append(line)
                result.append(' ' * (current_indent + 4) + 'pass')
                i += 1
                continue
        result.append(line)
        i += 1
    return '\n'.join(result)


def _fix_binding_names(binding_code: str, ep: str) -> str:
    if ep in ("solve_a", "solve_b", "solve"):
        return binding_code
    pat = re.compile(r'\b' + re.escape(ep) + r'\b')
    lines = binding_code.splitlines()
    result = []
    for line in lines:
        if re.search(r'\bout_a\s*=', line):
            line = pat.sub('solve_a', line)
        elif re.search(r'\bout_b\s*=', line):
            line = pat.sub('solve_b', line)
        result.append(line)
    return '\n'.join(result)


def generate_binding_code(
    reference_code: str,
    description: str,
    llm_client,
    seed_example: Optional[str] = None,
) -> str:
    seed_section = (
        _SEED_SECTION.format(seed_example=seed_example)
        if seed_example else ""
    )
    prompt = _BINDING_PROMPT.format(
        reference_code=reference_code,
        description=description,
        seed_section=seed_section,
    )
    raw = llm_client(prompt)
    return _strip_fences(raw)


def _split_future_imports(context: str):
    future_lines = []
    other_lines  = []
    for line in context.splitlines():
        if re.match(r'\s*from\s+__future__\s+import', line):
            future_lines.append(line.strip())
        else:
            other_lines.append(line)
    return future_lines, "\n".join(other_lines)


def _assemble_script(
    reference_code: str,
    generated_code: str,
    binding_code: str,
    max_cases: int,
    context: str = "",
) -> str:
    ep = _entry_point(reference_code)
    solve_a_impl = _rename_all(reference_code, ep, "_solve_a_impl")
    solve_b_impl = _rename_all(generated_code,  ep, "_solve_b_impl")
    binding_code = _fix_binding_names(binding_code, ep)


    future_lines, clean_context = _split_future_imports(context)
    future_block = "\n".join(future_lines) + "\n" if future_lines else ""

    return _TEMPLATE.format(
        future_imports=future_block,
        preamble=_PREAMBLE.strip(),
        context=clean_context.strip() + "\n" if clean_context.strip() else "",
        solve_a_impl=solve_a_impl.strip(),
        solve_b_impl=solve_b_impl.strip(),
        binding_code=_indent(binding_code, 8),
        max_cases=max_cases,
    )


def run_differential_fuzz(
    generated_code: str,
    reference_code: str,
    binding_code: str,
    n_runs: int = 3,
    timeout: int = 60,
    max_cases: int = 2000,
    context: str = "",
) -> float:
    script = _assemble_script(reference_code, generated_code, binding_code, max_cases, context)

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", prefix="diff_fuzz_",
        delete=False, encoding="utf-8"
    ) as f:
        f.write(script)
        script_path = f.name

    try:
        return _run_script(script_path, n_runs, timeout)
    finally:
        Path(script_path).unlink(missing_ok=True)
        _delete_crash_files()


def score_with_fuzzing(
    generated_code: str,
    reference_code: str,
    description: str,
    llm_client,
    test_cases: Optional[List[str]] = None,
    binding_code: Optional[str] = None,
    context: str = "",
    n_runs: int = 3,
    timeout: int = 60,
    max_cases: int = 2000,
) -> dict:
    if binding_code is None:
        ep   = _entry_point(reference_code)
        seed = _extract_seed(test_cases, ep)
        for attempt in range(3):
            binding_code = generate_binding_code(
                reference_code, description, llm_client, seed_example=seed
            )

            test_script = _assemble_script(reference_code, reference_code, binding_code, max_cases, context)
            try:
                compile(test_script, "<binding>", "exec")
                break
            except SyntaxError:
                if attempt < 2:
                    binding_code = None
    result = run_differential_fuzz(
        generated_code, reference_code, binding_code,
        n_runs=n_runs, timeout=timeout, max_cases=max_cases, context=context,
    )
    score = result["score"] if result["n_valid"] > 0 else None
    return {
        "score":   score,
        "status":  result["status"],
        "total":   result["total"],
        "matches": result["matches"],
    }


_SOLVE_B_RE = re.compile(
    r'def _solve_b_impl\(\*args,\s*\*\*kwargs\):\s*\n[ \t]+raise NotImplementedError[^\n]*\n?'
)


def run_from_template(
    template_path,
    generated_code: str,
    n_runs: int = 3,
    timeout: int = 60,
    max_cases: int = 1000,
) -> dict:
    template = Path(template_path).read_text(encoding="utf-8")

    ep           = _entry_point(generated_code)
    solve_b_impl = _rename_all(generated_code, ep, "_solve_b_impl").strip()

    script, n_replacements = _SOLVE_B_RE.subn(solve_b_impl + "\n\n", template, count=1)
    if n_replacements != 1:
        raise ValueError(f"Expected exactly one _solve_b_impl placeholder in {template_path}, found {n_replacements}")
    if max_cases != 1000:
        script = re.sub(r'^MAX_CASES\s*=\s*\d+', f'MAX_CASES = {max_cases}',
                        script, flags=re.MULTILINE)

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", prefix="tmpl_fuzz_",
        delete=False, encoding="utf-8"
    ) as f:
        f.write(script)
        script_path = f.name

    try:
        result = _run_script(script_path, n_runs, timeout)
    finally:
        Path(script_path).unlink(missing_ok=True)
        _delete_crash_files()

    return _finish(result)


def _replace_impl_function(source: str, func_name: str, new_code: str) -> str:
    tree = ast.parse(source)
    target = next((n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == func_name), None)
    if target is None:
        raise ValueError(f"{func_name} not found in template")
    new_func = _rename_all(new_code, _entry_point(new_code), func_name).strip()
    lines = source.splitlines(keepends=True)
    return "".join(lines[:target.lineno - 1] + [new_func + "\n\n"] + lines[target.end_lineno:])


def run_from_template_pair(
    template_path,
    code_a: str,
    code_b: str,
    n_runs: int = 3,
    timeout: int = 60,
    max_cases: int = 1000,
) -> dict:
    template = Path(template_path).read_text(encoding="utf-8")

    script = _replace_impl_function(template, "_solve_a_impl", code_a)
    script = _replace_impl_function(script, "_solve_b_impl", code_b)
    if max_cases != 1000:
        script = re.sub(r'^MAX_CASES\s*=\s*\d+', f'MAX_CASES = {max_cases}',
                        script, flags=re.MULTILINE)

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", prefix="tmpl_fuzz_",
        delete=False, encoding="utf-8"
    ) as f:
        f.write(script)
        script_path = f.name

    try:
        result = _run_script(script_path, n_runs, timeout)
    finally:
        Path(script_path).unlink(missing_ok=True)
        _delete_crash_files()

    return _finish(result)


def _finish(result: dict) -> dict:
    return {
        "score":   result["score"] if result["n_valid"] > 0 else None,
        "status":  result["status"],
        "total":   result["total"],
        "matches": result["matches"],
    }
