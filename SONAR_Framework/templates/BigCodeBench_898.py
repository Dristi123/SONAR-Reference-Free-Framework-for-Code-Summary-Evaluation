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


from collections import Counter
import random

LETTERS = ['a', 'b', 'c', 'd', 'e']

def _solve_a_impl(count, seed=0):
    """
    Generate a specific number of random letter pairs, each from a predefined list, and analyze the frequency of each pair.

    Parameters:
    - count (int): The number of letter pairs to generate.
    - seed (int, optional): Seed for the random number generator to ensure reproducibility. Defaults to None.

    Returns:
    - Counter: A Counter object representing the frequency of each generated letter pair.

    Requirements:
    - collections.Counter
    - random

    Examples:
    >>> _solve_a_impl(5, seed=42)
    Counter({('d', 'a'): 1, ('b', 'b'): 1, ('d', 'd'): 1, ('e', 'a'): 1, ('c', 'a'): 1})
    >>> _solve_a_impl(0, seed=42)
    Counter()
    """
    random.seed(seed)

    pairs = [tuple(random.choices(LETTERS, k=2)) for _ in range(count)]
    pair_frequency = Counter(pairs)

    return pair_frequency

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
        count = fdp.ConsumeIntInRange(0, 100)
        seed = fdp.ConsumeIntInRange(0, 10000)

        random.seed(42) # Fixed seed for solve_a to ensure deterministic random behavior
        out_a = solve_a(count, seed)

        random.seed(42) # Fixed seed for solve_b to ensure deterministic random behavior
        out_b = solve_b(count, seed)
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
