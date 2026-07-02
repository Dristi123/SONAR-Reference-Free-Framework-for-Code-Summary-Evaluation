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


import collections
import random

# Constants
LETTERS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']

def _solve_a_impl(n_keys, n_values):
    """
    Create a Python dictionary with a specified number of keys and values. 

    Parameters:
    n_keys (int): The number of keys to generate.
    n_values (int): The number of values for each key (consecutive integers starting from 1).

    Returns:
    dict: A Python dictionary with keys as strings and values as lists of integers.

    Note: 
    - Keys are randomly selected from a predefined list of letters, and values are consecutive integers starting from 1.
    - Due to the randomness in key selection, the actual keys in the dictionary may vary in each execution.

    Requirements:
    - collections
    - random

    Example:
    >>> random.seed(0)
    >>> _solve_a_impl(3, 5)
    {'g': [1, 2, 3, 4, 5], 'a': [1, 2, 3, 4, 5]}
    >>> result = _solve_a_impl(1, 5)
    >>> list(result)[0] in LETTERS
    True
    """

    keys = [random.choice(LETTERS) for _ in range(n_keys)]
    values = list(range(1, n_values + 1))
    return dict(collections.OrderedDict((k, values) for k in keys))

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
       
            n_keys = fdp.ConsumeIntInRange(0, 20)
            n_values = fdp.ConsumeIntInRange(0, 100)

            random.seed(42)
            out_a = solve_a(n_keys, n_values)
            random.seed(42)
            out_b = solve_b(n_keys, n_values)
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
