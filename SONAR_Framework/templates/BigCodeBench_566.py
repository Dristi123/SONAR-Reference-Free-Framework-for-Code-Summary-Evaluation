import atheris
import sys
import random
from typing import List, Tuple, Dict, Optional, Any, Set
from collections import defaultdict, Counter, OrderedDict
from itertools import combinations, permutations, product
from functools import reduce
import math, re, hashlib, copy, string
total = 0
matches = 0
_discarded = 0
MAX_CASES = 1000
_attempts = 0
MAX_ATTEMPTS = MAX_CASES * 5


import inspect
import types

def _solve_a_impl(f):
    """
    Inspects a given function 'f' and returns its specifications, including the function's name,
    whether it is a lambda function, its arguments, defaults, and annotations. This method
    utilizes the inspect and types modules to introspect function properties.

    Parameters:
    f (function): The function to inspect.

    Returns:
    dict: A dictionary containing details about the function, such as its name, if it's a lambda function,
          arguments, default values, and annotations.

    Requirements:
    - inspect
    - types

    Examples:
    >>> def sample_function(x, y=5): return x + y
    >>> result = _solve_a_impl(sample_function)
    >>> 'sample_function' == result['function_name'] and len(result['args']) == 2
    True
    >>> lambda_func = lambda x: x * 2
    >>> _solve_a_impl(lambda_func)['is_lambda']
    True
    """
    spec = inspect.getfullargspec(f)

    return {
        'function_name': f.__name__,
        'is_lambda': isinstance(f, types.LambdaType),
        'args': spec.args,
        'defaults': spec.defaults,
        'annotations': spec.annotations
    }

def _solve_b_impl(*args, **kwargs):
    raise NotImplementedError


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
    """Equality with float tolerance and NaN handling."""
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
        _ATHERIS_FUZZ_FUNCS = [
            lambda: None,  # No arguments
            lambda x: x,  # One positional argument
            lambda a, b: a + b,  # Two positional arguments
            lambda x, y=10: x * y,  # Positional with default
            lambda p: p * 2,  # Simple lambda
            lambda a, b, c=None: (a, b, c), # Multiple args with one default
            lambda p: p, # Another simple lambda
            lambda *args: sum(args),  # Var-positional arguments
            lambda **kwargs: kwargs,  # Var-keyword arguments
            lambda a, *args, b, c=20, **kwargs: (a, args, b, c, kwargs), # Complex signature
            lambda x: x, # Simple identity lambda
            lambda a: a if isinstance(a, int) else None, # Type check inside lambda
        ]

        def _atheris_fuzz_def_func_with_annotations(arg1: int, arg2: str = "hello") -> bool:
            """A standard function with annotations and defaults."""
            return len(arg2) > arg1

        _ATHERIS_FUZZ_FUNCS.append(_atheris_fuzz_def_func_with_annotations)

        # Pick a function from the predefined list for fuzzing
        f = fdp.PickValueInList(_ATHERIS_FUZZ_FUNCS)

        out_a = solve_a(f)
        out_b = solve_b(f)
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
        print(f"Mismatch: A returned {a_val!r}, B raised")
    elif not a_ok and b_ok:
        # Case 3: reference raised, generated succeeded — discard (no ground truth)
        _discarded += 1
    else:
        # Case 4: both succeeded — compare outputs
        total += 1
        if _eq(a_val, b_val):
            matches += 1
        else:
            print(f"Mismatch: A={a_val!r}, B={b_val!r}")


def main():
    atheris.Setup(sys.argv, TestOneInput)
    try:
        atheris.Fuzz()
    except (SystemExit, Exception):
        pass
    finally:
        print("\n=== Fuzzing Summary ===")
        print(f"Total test cases: {total}")
        print(f"Matches (semantically equivalent): {matches}")
        print(f"Discarded inputs: {_discarded}")
        if total > 0:
            print(f"Semantic agreement score: {matches / total:.2%}")
        else:
            print("No valid inputs tested.")


if __name__ == "__main__":
    main()
