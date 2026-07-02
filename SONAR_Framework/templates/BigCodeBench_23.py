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
from itertools import zip_longest

def _solve_a_impl(l1, l2,THRESHOLD = 0.5):
    """
    Alternates elements from two numeric lists, calculates the absolute difference of each 
    element from a predefined threshold, and returns the element closest to this threshold.
    
    Parameters:
    l1 (list): The first input list containing numeric values.
    l2 (list): The second input list containing numeric values.
    THRESHOLD (float): The predefined constant representing a numeric value used as a reference point for comparison. Default to 0.5. 
    
    Returns:
    float: The element from the combined list that is closest to the threshold of 0.5.
    
    Requirements:
    - numpy
    - itertools.zip_longest

    Notes:
    - If l1 and l2 are of different lengths, elements from the longer list without a corresponding 
      pair in the shorter list will not be paired with 'None'. Only existing numeric elements are considered.
    - The threshold is fixed at 0.5. Adjustments to the threshold require changes to the THRESHOLD constant.
    
    Example:
    >>> l1 = [0.3, 1, 2, 3]
    >>> l2 = [0.7, 11, 12, 13]
    >>> closest = _solve_a_impl(l1, l2)
    >>> print(closest)
    0.7
    """
    combined = [val for pair in zip_longest(l1, l2) for val in pair if val is not None]
    differences = np.abs(np.array(combined) - THRESHOLD)
    closest_index = np.argmin(differences)
    return combined[closest_index]

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
      
            l1_len = fdp.ConsumeIntInRange(0, 10)
            l1 = []
            for _ in range(l1_len):
                l1.append(fdp.ConsumeIntInRange(-10000, 10000) / 100.0)

            l2_len = fdp.ConsumeIntInRange(0, 10)
            l2 = []
            for _ in range(l2_len):
                l2.append(fdp.ConsumeIntInRange(-10000, 10000) / 100.0)

            # The description specifies the threshold is fixed at 0.5
            THRESHOLD_VAL = 0.5

            out_a = solve_a(l1, l2, THRESHOLD_VAL)
            out_b = solve_b(l1, l2, THRESHOLD_VAL)
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
