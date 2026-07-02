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


import heapq
import random

def _solve_a_impl(k, list_length = 5, min_value = 0, max_value = 100):
    """
    Find the k smallest numbers in a randomly generated list using heapq.

    Parameters:
    k (int): The number of smallest elements to find.
    list_length (int): The length of the randomly generated list of integers.
    min_value (int): The minimum value for randomly generated integers.
    max_value (int): The maximum value for randomly generated integers.

    Returns:
    tuple: A tuple containing two lists: 
        - list[int]: The randomly generated list of integers with the specified length.
        - list[int]: The k smallest numbers found using heapq.

    Requirements:
    - heapq
    - random

    Example:
    >>> random.seed(0)
    >>> rand_list, least_k = _solve_a_impl(3)
    >>> least_k[0] in rand_list
    True
    >>> rand_list, least_k = _solve_a_impl(3,5,100,100)
    >>> print(least_k)
    [100, 100, 100]
    """

    numbers = [random.randint(min_value, max_value) for _ in range(list_length)]
    heapq.heapify(numbers)
    smallest_numbers = heapq.nsmallest(k, numbers)
   
    return numbers, smallest_numbers

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
     
            list_length = fdp.ConsumeIntInRange(0, 100) # list_length can be 0 or up to 100 for reasonable fuzzing
            k = fdp.ConsumeIntInRange(0, list_length) # k must be non-negative and less than or equal to list_length
            min_value = fdp.ConsumeIntInRange(-1000, 1000) # min_value can be positive or negative
            # max_value must be greater than or equal to min_value.
            # We cap the upper bound for max_value to keep values within a reasonable range.
            max_value = fdp.ConsumeIntInRange(min_value, 1000) 

            random.seed(42)
            out_a = solve_a(k, list_length, min_value, max_value)
            random.seed(42)
            out_b = solve_b(k, list_length, min_value, max_value)
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
