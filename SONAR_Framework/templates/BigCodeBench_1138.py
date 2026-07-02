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
import itertools

def _solve_a_impl(matrix):
    """
    Sorts a numeric 2D numpy array in ascending order and finds all unique combinations of two elements from the sorted array.
    
    Parameters:
    - matrix (numpy.array): A 2D numpy array of any shape (m, n), where m and n are non-negative integers.
    
    Returns:
    - tuple: A tuple containing two elements:
        1. numpy.array: A 1D array with all elements of the input array sorted in ascending order.
        2. list: A list of tuples, each containing a pair of elements from the sorted array, representing all unique combinations taken two at a time.

    Requirements:
    - numpy
    - itertools
    
    Example:
    >>> _solve_a_impl(np.array([[1, 3], [2, 4]]))
    (array([1, 2, 3, 4]), [(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)])
    """
    sorted_array = np.sort(matrix, axis=None)
    
    combinations = list(itertools.combinations(sorted_array, 2))
    
    return sorted_array, combinations

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
        # Determine matrix dimensions
                rows = fdp.ConsumeIntInRange(0, 5)  # Max 5 rows to keep input size manageable
                cols = fdp.ConsumeIntInRange(0, 5)  # Max 5 columns to keep input size manageable

                matrix_elements = []
                for _ in range(rows * cols):
                    # Generate numeric elements (floats are used to cover integers and decimals)
                    matrix_elements.append(fdp.ConsumeIntInRange(-10000, 10000) / 100.0)

                # Create the numpy array. np.array([]).reshape(r, c) handles zero dimensions correctly.
                matrix_input = np.array(matrix_elements).reshape(rows, cols)

                # Call the functions with the generated input
                out_a = solve_a(matrix_input)
                out_b = solve_b(matrix_input)
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
