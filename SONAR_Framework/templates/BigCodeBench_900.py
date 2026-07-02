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


import pandas as pd
import numpy as np

def _solve_a_impl(d):
    """
    Calculate mean, sum, max, min and standard deviation for the keys "x," "y" and "z" from a list of dictionaries "d."
    
    Parameters:
    d (list): A list of dictionaries.

    Returns:
    dict: A dictionary with keys as 'x', 'y', and 'z' and values as dictionaries of statistics.

    Raises:
    - ValueError: If input is not a list of dictionaries.

    Requirements:
    - pandas
    - numpy

    Examples:
    >>> data = [{'x': 1, 'y': 10, 'z': 5}, {'x': 3, 'y': 15, 'z': 6}, {'x': 2, 'y': 1, 'z': 7}]
    >>> _solve_a_impl(data)
    {'x': {'mean': 2.0, 'sum': 6, 'max': 3, 'min': 1, 'std': 0.816496580927726}, 'y': {'mean': 8.666666666666666, 'sum': 26, 'max': 15, 'min': 1, 'std': 5.792715732327589}, 'z': {'mean': 6.0, 'sum': 18, 'max': 7, 'min': 5, 'std': 0.816496580927726}}
    >>> _solve_a_impl([])
    {'x': None, 'y': None, 'z': None}
    >>> _solve_a_impl([{'a': 1}])
    {'x': None, 'y': None, 'z': None}
    """
    if not isinstance(d, list) or any(not isinstance(item, dict) for item in d):
        raise ValueError("Input must be a list of dictionaries.")
    
    if not d:
        return {key: None for key in ['x', 'y', 'z']}

    df = pd.DataFrame(d).fillna(0)  # Replace missing values with 0 to allow computations
    stats = {}

    for key in ['x', 'y', 'z']:
        if key in df.columns:
            stats[key] = {
                'mean': np.mean(df[key]),
                'sum': np.sum(df[key]),
                'max': np.max(df[key]),
                'min': np.min(df[key]),
                'std': np.std(df[key], ddof=0)  # Population standard deviation
            }
        else:
            stats[key] = None

    return stats

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
        d = []
        for _ in range(list_len):
            current_dict = {}
            # Randomly decide to include 'x', 'y', 'z' keys and their values
            if fdp.ConsumeBool():
                current_dict['x'] = fdp.ConsumeIntInRange(-10000, 10000) / 100.0
            if fdp.ConsumeBool():
                current_dict['y'] = fdp.ConsumeIntInRange(-10000, 10000) / 100.0
            if fdp.ConsumeBool():
                current_dict['z'] = fdp.ConsumeIntInRange(-10000, 10000) / 100.0
            # Add some other random keys to ensure robustness, but not required by problem description to be tested specifically
            # if fdp.ConsumeBool():
            #    current_dict[''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))] = fdp.ConsumeIntInRange(-10000, 10000) / 100.0
            d.append(current_dict)

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
