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
import random
from scipy import stats

def _solve_a_impl(n_data_points=5000, min_value=0.0, max_value=10.0):
    """
    Generate a random dataset of floating-point numbers within a specified range, 
    truncate each value to 3 decimal places, and calculate statistical measures (mean, median, mode) of the data.
    
    Parameters:
    n_data_points (int): Number of data points to generate. Default is 5000.
    min_value (float): Minimum value range for data points. Default is 0.0.
    max_value (float): Maximum value range for data points. Default is 10.0.

    Returns:
    dict: A dictionary with keys 'mean', 'median', 'mode' and their corresponding calculated values.
    
    Requirements:
    - pandas
    - random
    - scipy.stats

    Example:
    >>> random.seed(0)
    >>> stats = _solve_a_impl(1000, 5.0, 5.0)
    >>> print(stats)
    {'mean': 5.0, 'median': 5.0, 'mode': 5.0}
    """

    data = [round(random.uniform(min_value, max_value), 3) for _ in range(n_data_points)]
    data_df = pd.DataFrame(data, columns=['Value'])

    mean = data_df['Value'].mean()
    median = data_df['Value'].median()
    mode = stats.mode(data_df['Value'].values)[0][0]

    return {'mean': mean, 'median': median, 'mode': mode}

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
      
            n_data_points = fdp.ConsumeIntInRange(1, 1000) # Limit data points to avoid excessive execution time

                # Generate two float values and then assign them to min_value and max_value
                # ensuring that min_value <= max_value for valid range.
            raw_val1 = fdp.ConsumeIntInRange(-10000, 10000) / 100.0
            raw_val2 = fdp.ConsumeIntInRange(-10000, 10000) / 100.0

            min_value = min(raw_val1, raw_val2)
            max_value = max(raw_val1, raw_val2)

            random.seed(42)
            out_a = solve_a(n_data_points=n_data_points, min_value=min_value, max_value=max_value)
            random.seed(42)
            out_b = solve_b(n_data_points=n_data_points, min_value=min_value, max_value=max_value)
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
