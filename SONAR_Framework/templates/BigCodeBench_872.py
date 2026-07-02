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

def _solve_a_impl(data_list):
    """
    Unzips a list of tuples and calculates the mean of the numeric values for 
    each position.

    The function accepts a list of tuples, where each tuple consists of 
    alphanumeric values. It unzips the tuples, and calculates the mean of 
    numeric values at each position using numpy, where non numeric values are
    ignores. If all values at a position are non numeric, the mean at this
    position is set to be np.nan.
    If the provided tuples have different number of entries, missing values are 
    treated as zeros.

    Parameters:
    - data_list (list of tuples): The data to process, structured as a list of tuples. Each tuple can contain alphanumeric values.

    Returns:
    - list: A list of mean values for each numeric position across the tuples. Non-numeric positions are ignored.
            An empty list is returned if the input list (data_list) is empty.

    Requirements:
    - numpy
    - itertools

    Example:
    >>> _solve_a_impl([('a', 1, 2), ('b', 2, 3), ('c', 3, 4), ('d', 4, 5), ('e', 5, 6)])
    [nan, 3.0, 4.0]
    >>> _solve_a_impl([(1, 'a', 2), ('a', 3, 5), ('c', 1, -2)])
    [1.0, 2.0, 1.6666666666666667]
    """
    # Unzip the data while handling uneven tuple lengths by filling missing values with NaN
    unzipped_data = list(itertools.zip_longest(*data_list, fillvalue=np.nan))

    # Calculate the mean of numeric values, ignoring non-numeric ones
    mean_values = [np.nanmean([val for val in column if isinstance(val, (int, float))]) for column in unzipped_data]

    return mean_values

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
        list_len = fdp.ConsumeIntInRange(0, 10)
        data_list = []
        for _ in range(list_len):
            tuple_len = fdp.ConsumeIntInRange(0, 10)
            current_tuple_elements = []
            for _ in range(tuple_len):
                # Choose between an integer, a float, or a string
                element_type_choice = fdp.ConsumeIntInRange(0, 2)
                if element_type_choice == 0:
                    # Integer
                    current_tuple_elements.append(fdp.ConsumeIntInRange(-1000, 1000))
                elif element_type_choice == 1:
                    # Float
                    current_tuple_elements.append(fdp.ConsumeIntInRange(-10000, 10000) / 100.0)
                else:
                    # String (alphanumeric implies characters, but UnicodeNoSurrogates covers it)
                    current_tuple_elements.append(''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10))))
            data_list.append(tuple(current_tuple_elements))

        out_a = solve_a(data_list)
        out_b = solve_b(data_list)
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
