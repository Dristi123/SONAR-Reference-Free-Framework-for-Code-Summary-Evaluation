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


def _solve_a_impl(func):
    func._web_method = True
    return func

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
        # Generate a name for the dummy function that will be decorated.
                # This name serves as the "identical argument" for solve_a and solve_b.
                func_name_len = fdp.ConsumeIntInRange(1, 100)
                func_name = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))

                # Call solve_a and solve_b with the generated function name.
                # It's assumed that solve_a and solve_b are defined elsewhere
                # and internally create a fresh dummy function object (with the given name)
                # for each call before applying the 'web_method' decorator.
                # They should return a tuple of properties that define the post-decoration state
                # for comparison, e.g., (function_name, _web_method_attribute_value).
                # Example conceptual definitions for solve_a/solve_b (NOT part of the output):
                #
                # def create_dummy_func(name):
                #     def dummy_func_for_test(*args, **kwargs):
                #         pass
                #     dummy_func_for_test.__name__ = name
                #     # Ensure it's clean for attribute assignment, though a new function
                #     # object should not have _web_method initially.
                #     if hasattr(dummy_func_for_test, '_web_method'):
                #         del dummy_func_for_test._web_method
                #     return dummy_func_for_test
                #
                # def solve_a(name_param):
                #     func_to_decorate = create_dummy_func(name_param)
                #     decorated_func = web_method(func_to_decorate)
                #     # Return relevant properties for comparison.
                #     # The function's name and the presence/value of the _web_method attribute.
                #     return (decorated_func.__name__, getattr(decorated_func, '_web_method', False))
                #
                # def solve_b(name_param):
                #     func_to_decorate = create_dummy_func(name_param)
                #     decorated_func = web_method(func_to_decorate)
                #     return (decorated_func.__name__, getattr(decorated_func, '_web_method', False))

                out_a = solve_a(func_name)
                out_b = solve_b(func_name)
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
