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
from collections import Counter

def _solve_a_impl(values, weights, n_samples):
    """
    Sample random numbers based on a given weighted distribution and return a histogram of the samples.

    Parameters:
    - values (list): List of values to be sampled from.
    - weights (list): List of weights corresponding to the values.
    - n_samples (int): Number of samples to be drawn.

    Returns:
    - histogram (dict): A histogram as a dictionary with the values as keys and counts as values.

    Requirements:
    - collections.Counter
    - random

    Example:
    >>> random.seed(42)
    >>> _solve_a_impl([1, 2, 3], [3, 2, 1], 1000)
    {2: 342, 1: 480, 3: 178}
    """
    import random
    samples = random.choices(values, weights=weights, k=n_samples)
    histogram = dict(Counter(samples))

    return histogram

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
        list_length = fdp.ConsumeIntInRange(1, 10)

        values = []
        for _ in range(list_length):
            values.append(fdp.ConsumeIntInRange(-100, 100)) # Example uses integers

        weights = []
        for _ in range(list_length):
            weights.append(fdp.ConsumeIntInRange(0, 100)) # Weights should be non-negative

        n_samples = fdp.ConsumeIntInRange(1, 1000) # Number of samples should be positive

        random.seed(42)
        out_a = solve_a(values, weights, n_samples)
        random.seed(42)
        out_b = solve_b(values, weights, n_samples)
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
