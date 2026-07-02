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
from scipy.stats import mode
from scipy.stats import entropy


def _solve_a_impl(numbers):
    """
    Creates and returns a dictionary with the mode and entropy of a numpy array constructed from a given list.
    The function first converts the list into a numpy array, then calculates the mode and the entropy (base 2) of this array,
    and finally adds them to the initial dictionary with the keys 'mode' and 'entropy'.

    Parameters:
        numbers (list): A non-empty list of numbers from which a numpy array is created to calculate mode and entropy.

    Returns:
        dict: A dictionary containing the 'mode' and 'entropy' of the array with their respective calculated values.

    Raises:
        ValueError if the input list `numbers` is empty

    Requirements:
        - numpy
        - scipy.stats.mode
        - scipy.stats.entropy

    Examples:
        >>> result = _solve_a_impl([1, 2, 2, 3, 3, 3])
        >>> 'mode' in result and result['mode'] == 3 and 'entropy' in result
        True
    """
    if len(numbers) == 0:
        raise ValueError
    my_dict = {'array': np.array(numbers)}
    mode_value = mode(my_dict['array']).mode[0]
    ent = entropy(my_dict['array'], base=2)
    my_dict['mode'] = mode_value
    my_dict['entropy'] = ent
    return my_dict

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
        list_len = fdp.ConsumeIntInRange(1, 100) # List must be non-empty as per description and ValueError
        numbers = []
        for _ in range(list_len):
            # The example uses integers, and entropy calculation typically works well with counts/frequencies,
            # which are usually non-negative integers. Limiting to non-negative integers for simplicity.
            numbers.append(fdp.ConsumeIntInRange(0, 100))

        out_a = solve_a(numbers)
        # For fuzzing, solve_b would be a reference implementation or the same function
        # to test for determinism or against a different implementation.
        # In this context, we'll call task_func for both.
        out_b = solve_b(numbers)
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
