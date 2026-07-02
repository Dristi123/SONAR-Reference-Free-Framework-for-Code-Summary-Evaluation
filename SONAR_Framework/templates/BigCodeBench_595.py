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
import bisect
from array import array


def _solve_a_impl(n=10, total=100):
    """
    Generates 'n' random integer numbers such that their sum equals 'total', sorts these numbers,
    and determines the position where a new random number can be inserted to maintain the sorted order.
    The function uses a retry mechanism to ensure the generated numbers sum up to 'total'.

    Parameters:
    n (int): The number of random numbers to generate. Default is 10.
    total (int): The total sum of the generated numbers. Default is 100.

    Returns:
    tuple: A tuple containing the sorted numbers as an array and the insertion position for a new number.

    Requirements:
    - random
    - bisect
    - array.array

    Examples:
    >>> sorted_nums, pos = _solve_a_impl(5, 50)
    >>> len(sorted_nums) == 5
    True
    >>> sum(sorted_nums) == 50
    True
    """
    nums = []
    while sum(nums) != total:
        nums = [random.randint(0, total) for _ in range(n)]

    nums.sort()
    nums = array('i', nums)

    new_num = random.randint(0, total)
    pos = bisect.bisect(nums, new_num)

    return (nums, pos)

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
      
            seed = fdp.ConsumeIntInRange(0, 1000000) # Seed for random number generation
            # n: The number of random numbers to generate. Default 10.
            # Must be >= 1 to avoid infinite loop when total > 0.
            n = fdp.ConsumeIntInRange(1, 50) 
            # total: The total sum of the generated numbers. Default 100.
            # Must be >= 0 because random.randint(0, total) expects total >= 0.
            total = fdp.ConsumeIntInRange(0, 200)

            random.seed(seed)
            out_a = solve_a(n, total)
            random.seed(seed)
            out_b = solve_b(n, total)
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
