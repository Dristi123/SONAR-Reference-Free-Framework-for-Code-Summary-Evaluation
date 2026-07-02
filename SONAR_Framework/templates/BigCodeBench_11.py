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
import random


def _solve_a_impl(T1, max_value=100):
    """
    Converts elements in 'T1', a tuple of tuples containing string representations 
    of integers, to integers and creates a list of random integers. The size of the 
    list equals the sum of these integers. Returns the 25th, 50th, and 75th percentiles 
    of this list.

    Parameters:
    T1 (tuple of tuple of str): A tuple of tuples, each containing string representations of integers.
    max_value (int): The upper bound for random number generation, exclusive. Default is 100.
    
    Returns:
    tuple: A tuple (p25, p50, p75) representing the 25th, 50th, and 75th percentiles of the list.

    Requirements:
    - numpy
    - itertools
    - random
    
    Example:
    >>> import random
    >>> random.seed(42)
    >>> T1 = (('13', '17', '18', '21', '32'), ('07', '11', '13', '14', '28'), ('01', '05', '06', '08', '15', '16'))
    >>> percentiles = _solve_a_impl(T1)
    >>> print(percentiles)
    (24.0, 48.0, 77.0)
    """
    int_list = [list(map(int, x)) for x in T1]
    flattened_list = list(itertools.chain(*int_list))
    total_nums = sum(flattened_list)

    random_nums = [random.randint(0, max_value) for _ in range(total_nums)]

    p25 = np.percentile(random_nums, 25)
    p50 = np.percentile(random_nums, 50)
    p75 = np.percentile(random_nums, 75)

    return p25, p50, p75

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
        # Generate max_value
        # max_value is an integer, upper bound for random number generation (exclusive).
        # The default is 100. Let's allow it to vary in a reasonable range.
        max_value = fdp.ConsumeIntInRange(0, 200)

        # Generate T1: a tuple of tuples of string representations of integers.
        # First, determine the number of inner tuples.
        num_outer_tuples = fdp.ConsumeIntInRange(1, 5) # Number of inner tuples (at least 1 to avoid empty T1)
        T1_list = []
        for _ in range(num_outer_tuples):
            # Determine the number of strings in each inner tuple.
            num_inner_strings = fdp.ConsumeIntInRange(1, 5) # Number of strings (at least 1 to avoid empty inner tuples)
            inner_tuple_list = []
            for _ in range(num_inner_strings):
                # Generate an integer value, then convert it to a string.
                # To ensure that `total_nums` (sum of integers) is generally > 0,
                # and to prevent excessively large lists which could lead to performance issues
                # or out-of-memory errors during fuzzing, limit the integer value.
                # The example has values up to 32, so let's allow a similar range.
                int_val = fdp.ConsumeIntInRange(1, 30) # Ensure integers are positive to guarantee total_nums > 0
                inner_tuple_list.append(str(int_val))
            T1_list.append(tuple(inner_tuple_list))
        T1 = tuple(T1_list)

        # Call task_func for solve_a
        # Seed the random number generator so both calls produce identical results.
        random.seed(42)
        out_a = solve_a(T1, max_value)

        # Call task_func for solve_b
        # Seed the random number generator again for the second call.
        random.seed(42)
        out_b = solve_b(T1, max_value)
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
