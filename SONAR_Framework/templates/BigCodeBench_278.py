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


import numpy as np
from sympy import symbols, solve


def _solve_a_impl(precision=2, seed=0):
    """
    Solve a quadratic equation in the form of ax ^ 2 + bx + c = 0, where a, b, and c randomly generated numbers are between -10 and 10. The solutions are complex numbers rounded to the specified accuracy.

    Parameters:
    precision (int): The number of decimal places to which to round the solutions.
    seed (int, Optional): The seed for the random number generator.

    Returns:
    tuple: A tuple of two solutions formatted as complex numbers (rounded to the specified precision).

    Requirements:
    - numpy
    - math
    - sympy

    Example:
    >>> result = _solve_a_impl()
    >>> len(result)
    2
    >>> result
    ((-3.86+0j), (-0.54+0j))
    """
    np.random.seed(seed)
    a = np.random.uniform(-10, 10)
    b = np.random.uniform(-10, 10)
    c = np.random.uniform(-10, 10)

    x = symbols('x')
    equation = a * x**2 + b * x + c

    solutions = solve(equation, x)
    solutions = [complex(round(complex(solution).real, precision), round(complex(solution).imag, precision)) for solution in solutions]

    return tuple(solutions)

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
     
            precision_val = fdp.ConsumeIntInRange(0, 5)
            seed_val = fdp.ConsumeIntInRange(0, 1000)

            out_a = solve_a(precision=precision_val, seed=seed_val)
            out_b = solve_b(precision=precision_val, seed=seed_val)
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
