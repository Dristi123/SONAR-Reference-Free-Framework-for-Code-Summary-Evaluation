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
from itertools import zip_longest
from random import choices

def _solve_a_impl(l1, l2, K=10):
    """
    Combine two lists by alternating their elements, even if they are of different lengths. 
    Elements from the longer list without a counterpart in the shorter one will be included on their own.
    Then, create a random sample of size K from the combined list, and calculate the frequency of 
    each element in the sample.

    Parameters:
    l1 (list): The first list containing any hashable types.
    l2 (list): The second list containing any hashable types.
    K (int): the size of the random sample from the combined list. Default to 10.

    Returns:
    collections.Counter: An object that counts the frequency of each element in the sample.

    Requirements:
    - collections
    - itertools.zip_longest
    - random.choices

    Example:
    >>> import random
    >>> random.seed(32)
    >>> l1 = list(range(10))
    >>> l2 = list(range(10, 20))
    >>> freq = _solve_a_impl(l1, l2)
    >>> print(freq)
    Counter({5: 2, 10: 1, 2: 1, 3: 1, 9: 1, 14: 1, 7: 1, 1: 1, 8: 1})
    """
    combined = [val for pair in zip_longest(l1, l2) for val in pair if val is not None]
    sample = choices(combined, k=K)
    freq = collections.Counter(sample)
    return freq

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
       
            list_len_1 = fdp.ConsumeIntInRange(0, 10)
            l1 = [fdp.ConsumeIntInRange(-100, 100) for _ in range(list_len_1)]

            list_len_2 = fdp.ConsumeIntInRange(0, 10)
            l2 = [fdp.ConsumeIntInRange(-100, 100) for _ in range(list_len_2)]

            K = fdp.ConsumeIntInRange(0, 20) # K can be 0, and also potentially larger than combined list length

            random.seed(42)
            out_a = solve_a(l1, l2, K)
            random.seed(42)
            out_b = solve_b(l1, l2, K)
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
