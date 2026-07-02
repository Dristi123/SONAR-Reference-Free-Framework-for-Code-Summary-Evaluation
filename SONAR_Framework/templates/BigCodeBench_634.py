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


import itertools
from typing import Any
from scipy import stats
import numpy as np


def _solve_a_impl(input_list: list, repetitions: int) -> Any:
    """
    Calculate the mode of a list of elements with multiple repetitions of the original list.
    
    Functionality: 
    - Takes a list and a repetition count as input.
    - Flattens the list with multiple repetitions.
    - Calculates the mode of the flattened list.
    
    Parameters:
    - input_list (list): A list containing elements (can be of any hashable type).
    - repetitions (int): The number of times the original list should be repeated.

    Requirements:
    - typing
    - itertools
    - scipy

    Returns:
    - scipy.stats.ModeResult: An object containing the mode(s) and count(s) of the most frequently occurring element(s) in the flattened list.
    
    Examples:
    >>> _solve_a_impl(['A', 'B', 'C'], 10)
    ModeResult(mode=array(['A'], dtype='<U1'), count=array([10]))
    
    >>> _solve_a_impl([1, 2, 3], 5)
    ModeResult(mode=array([1]), count=array([5]))
    """
    # Flattening the list with multiple repetitions
    flattened_list = np.array(list(itertools.chain(*[input_list for _ in range(repetitions)])))
    
    # Calculating the mode
    mode = stats.mode(flattened_list)
    
    return mode

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
        # Generate repetitions parameter
                repetitions = fdp.ConsumeIntInRange(1, 100)

                # Generate input_list parameter
                list_len = fdp.ConsumeIntInRange(1, 10)
                input_list = []
                for _ in range(list_len):
                    # Choose between generating an integer or a string element
                    element_type_choice = fdp.PickValueInList([0, 1]) # 0 for int, 1 for string
                    if element_type_choice == 0:
                        input_list.append(fdp.ConsumeIntInRange(-1000, 1000))
                    else:
                        input_list.append(''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10))))

                out_a = solve_a(input_list, repetitions)
                out_b = solve_b(input_list, repetitions)
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
