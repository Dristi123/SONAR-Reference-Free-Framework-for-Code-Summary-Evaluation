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
import math

def _solve_a_impl(f):
    """
    Analyzes a given function 'f' and returns a dictionary containing its name, the square root of
    the number of arguments, and the count of lambda functions present in its default values.
    This function demonstrates introspection of Python functions and the use of mathematical
    operations on the introspected data.

    Parameters:
    f (function): The function to inspect.

    Returns:
    dict: A dictionary containing the function's name, the square root of the number of arguments,
          and the count of lambda functions in default values.

    Requirements:
    - inspect
    - types
    - math

    Examples:
    >>> def sample_function(x, y=2): return x + y
    >>> result = _solve_a_impl(sample_function)
    >>> 'sample_function' == result['function_name'] and result['sqrt_args'] == math.sqrt(2)
    True
    >>> lambda_func = lambda x: x * 2
    >>> _solve_a_impl(lambda_func)['lambda_in_defaults'] == 0
    True
    """
    spec = inspect.getfullargspec(f)

    info = {
        'function_name': f.__name__,
        'sqrt_args': math.sqrt(len(spec.args)),
    }

    if spec.defaults:
        info['lambda_in_defaults'] = sum(1 for d in spec.defaults if isinstance(d, types.LambdaType))
    else:
        info['lambda_in_defaults'] = 0

    return info

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
        # Define a set of functions to be used as input for task_func
        # These functions cover different argument structures and default value types
        def fuzzed_func_no_args():
            return 0

        def fuzzed_func_pos_args(a, b, c):
            return a + b + c

        def fuzzed_func_defaults(x, y=10, z="hello"):
            return x + y

        def fuzzed_func_defaults_with_lambda(p, q=lambda val: val * 2, r=lambda val: val + 1):
            # The return value is irrelevant for task_func's analysis
            return p + q(1) + r(2)

        def fuzzed_func_mixed_args(arg1, arg2=5, *args, kwarg1=True, kwarg2=lambda x: x*x, **kwargs):
            return arg1 + arg2

        # A simple lambda function itself (will have no defaults)
        fuzzed_lambda_func = lambda x: x + 1

        # Functions containing only *args and **kwargs
        def fuzzed_func_varargs_only(*args):
            return len(args)

        def fuzzed_func_varkwargs_only(**kwargs):
            return len(kwargs)

        def fuzzed_func_all_kinds(a, b=1, *args, k=2, l=lambda z: z/2, **kwargs):
            return a + b + k

        # List of functions to choose from
        function_choices = [
            fuzzed_func_no_args,
            fuzzed_func_pos_args,
            fuzzed_func_defaults,
            fuzzed_func_defaults_with_lambda,
            fuzzed_func_mixed_args,
            fuzzed_lambda_func,
            fuzzed_func_varargs_only,
            fuzzed_func_varkwargs_only,
            fuzzed_func_all_kinds,
        ]

        # Pick a function from the predefined choices
        f = fdp.PickValueInList(function_choices)

        # Call both implementations with the same fuzzed input
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
