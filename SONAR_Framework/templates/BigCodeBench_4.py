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
import itertools

def _solve_a_impl(d):
    """
    Count the occurrence of each integer in the values of the input dictionary, where each value is a list of integers,
    and return a dictionary with these counts. The resulting dictionary's keys are the integers, and the values are 
    their respective counts across all lists in the input dictionary.

    Parameters:
    d (dict): A dictionary where each key is a string and the value is a list of integers.

    Returns:
    dict: A dictionary where each key is an integer from any of the input lists, and the value is the count of 
            how often that integer appears in all the lists combined.

    Requirements:
    - collections.Counter
    - itertools
    
    Example:
    >>> d = {'a': [1, 2, 3, 1], 'b': [3, 4, 5], 'c': [1, 2]}
    >>> count_dict = _solve_a_impl(d)
    >>> print(count_dict)
    {1: 3, 2: 2, 3: 2, 4: 1, 5: 1}
    """
    count_dict = Counter(itertools.chain.from_iterable(d.values()))
    return dict(count_dict)

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
        d = {}
        num_keys = fdp.ConsumeIntInRange(0, 5) # Number of key-value pairs in the dictionary
        for _ in range(num_keys):
            # Generate key (string)
            key_length = fdp.ConsumeIntInRange(1, 10) # Length of the key string
            key = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))

            # Generate value (list of integers)
            list_length = fdp.ConsumeIntInRange(0, 5) # Length of the integer list
            value_list = []
            for _ in range(list_length):
                integer_value = fdp.ConsumeIntInRange(-50, 50) # Integers within a reasonable range
                value_list.append(integer_value)

            d[key] = value_list

        out_a = solve_a(d)
        out_b = solve_b(d)
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
