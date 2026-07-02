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
import random
from scipy import stats


def _solve_a_impl(list_of_lists, size=5, seed=0):
    """
    Calculate the mean, median, and mode of values in a list of lists.
    If a list is empty, fill it with SIZE (default: 5) random integers between 0 and 100, 
    and then calculate the statistics.
    
    Parameters:
    list_of_lists (list): The list of lists.
    size (int, Optional): The number of random integers to generate. Default is 5.
    seed (int, Optional): Seed value for random number generation. Default is 0.
    
    Returns:
    dict: A dictionary with the mean, median, and mode of the values.
    
    Requirements:
    - numpy
    - random
    - scipy.stats
    
    Example:
    >>> _solve_a_impl([[1, 2, 3], [], [4, 5, 6]])
    {'mean': 23.454545454545453, 'median': 5.0, 'mode': array([5])}
    """
    random.seed(seed)
    data = []
    for list_ in list_of_lists:
        if list_:
            data += list_
        else:
            data += [random.randint(0, 100) for _ in range(size)]
    
    return {
        'mean': np.mean(data),
        'median': np.median(data),
        'mode': stats.mode(data)[0]
    }

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
        # Generate list_of_lists
                num_outer_lists = fdp.ConsumeIntInRange(0, 10)
                list_of_lists_arg = []
                for _ in range(num_outer_lists):
                    num_inner_elements = fdp.ConsumeIntInRange(0, 10)
                    inner_list = []
                    for _ in range(num_inner_elements):
                        inner_list.append(fdp.ConsumeIntInRange(-100, 100)) # Values for non-empty lists
                    list_of_lists_arg.append(inner_list)

                # Generate size
                size_arg = fdp.ConsumeIntInRange(1, 20) # size is used for number of random integers

                # Generate seed
                seed_arg = fdp.ConsumeIntInRange(0, 1000) # Seed for random number generation

                out_a = solve_a(list_of_lists_arg, size_arg, seed_arg)
                out_b = solve_b(list_of_lists_arg, size_arg, seed_arg)
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
