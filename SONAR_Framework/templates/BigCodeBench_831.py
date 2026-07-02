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


import random
import math


def _solve_a_impl(range_start=1, range_end=100, pairs_count=10, random_seed=None):
    """
    Create a generator object that generates a sequence of tuples.
    Each tuple contains two random numbers and the square root of their
    absolute difference.

    A random seed is used to have reproducability in the outputs.

    Parameters:
    - range_start (int): The start of the range for random numbers. Default is 1.
    - range_end (int): The end of the range for random numbers. Default is 100.
    - pairs_count (int): The number of pairs to generate. Default is 10.
    - random_seed (int): Seed used for rng. Default is None.
    
    Returns:
    generator: A generator object that produces tuples in the format
               (num1, num2, square root of absolute difference).

    Requirements:
    - random
    - math

    Example:
    >>> pairs = _solve_a_impl(random_seed=1)
    >>> print(next(pairs))
    (18, 73, 7.416198487095663)
    
    >>> pairs = _solve_a_impl(1, 3, pairs_count=25, random_seed=14)
    >>> print(next(pairs))
    (1, 3, 1.4142135623730951)
    """
    random.seed(random_seed)
    pairs = [(random.randint(range_start, range_end), random.randint(range_start, range_end)) for _ in range(pairs_count)]
    return ((x, y, math.sqrt(abs(x - y))) for x, y in pairs)

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
        range_start_raw = fdp.ConsumeIntInRange(1, 200)
        range_end_raw = fdp.ConsumeIntInRange(1, 200)

        range_start = min(range_start_raw, range_end_raw)
        range_end = max(range_start_raw, range_end_raw)

        pairs_count = fdp.ConsumeIntInRange(1, 100)

        # Decide if a seed should be provided or be None
        use_seed = fdp.ConsumeBool()
        random_seed = fdp.ConsumeIntInRange(0, 1000) if use_seed else None

        out_a_gen = solve_a(range_start=range_start, range_end=range_end, pairs_count=pairs_count, random_seed=random_seed)
        out_a = list(out_a_gen)

        out_b_gen = solve_b(range_start=range_start, range_end=range_end, pairs_count=pairs_count, random_seed=random_seed)
        out_b = list(out_b_gen)
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
