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
from collections import Counter


def _solve_a_impl(list_of_tuples):
    """
    Computes the sum of numeric values and counts the occurrences of categories in a list of tuples.

    Each tuple in the input list contains a numeric value and a category. This function calculates
    the sum of all the numeric values and also counts how many times each category appears in the list.

    Parameters:
    - list_of_tuples (list of tuple): A list where each tuple contains a numeric value and a category.

    Returns:
    - tuple: A 2-element tuple where the first element is the sum of the numeric values, and the
             second element is a dictionary with categories as keys and their counts as values.

    Requirements:
    - numpy
    - collections.Counter

    Example:
    >>> list_of_tuples = [(5, 'Fruits'), (9, 'Vegetables'), (-1, 'Dairy'), (-2, 'Bakery'), (4, 'Meat')]
    >>> sum_of_values, category_counts = _solve_a_impl(list_of_tuples)
    >>> print(sum_of_values)
    15
    >>> print(category_counts)
    {'Fruits': 1, 'Vegetables': 1, 'Dairy': 1, 'Bakery': 1, 'Meat': 1}
    """

    numeric_values = [pair[0] for pair in list_of_tuples]
    categories = [pair[1] for pair in list_of_tuples]

    total_sum = np.sum(numeric_values)
    category_counts = Counter(categories)

    return total_sum, dict(category_counts)

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
        list_of_tuples_length = fdp.ConsumeIntInRange(0, 10)
        list_of_tuples = []
        for _ in range(list_of_tuples_length):
            numeric_value = fdp.ConsumeIntInRange(-10000, 10000)
            category = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))
            list_of_tuples.append((numeric_value, category))

        out_a = solve_a(list_of_tuples)
        out_b = solve_b(list_of_tuples)
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
