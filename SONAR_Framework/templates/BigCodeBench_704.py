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
from itertools import combinations

# Constants
MIN_PERCENTAGE = 0.75

def _solve_a_impl(data, cols, percentage):
    """
    Find all combinations of columns from a given DataFrame so that the absolute correlation between them is greater than a certain threshold.

    Parameters:
    - data (list): List of lists with the data, where the length of the inner list equals the number of columns
    - cols (list): List of column names
    - percentage (float): The threshold for the absolute correlation.

    Returns:
    - corr_combinations (list): A list of tuples where each tuple contains two column names.

    Requirements:
    - pandas
    - itertools

    Example:
    >>> result = _solve_a_impl([[5.1, 5.0, 1.4], [4.9, 4.8, 1.4], [4.7, 4.6, 2.0]], ['x', 'y', 'z'], 0.9)
    >>> print(result)
    [('x', 'y')]
    """
    if not 0 <= percentage <= 1:
        raise ValueError('Percentage must be between 0 and 1')
    df = pd.DataFrame(data, columns=cols)
    corr_matrix = df.corr().abs()
    columns = corr_matrix.columns
    corr_combinations = []

    for col1, col2 in combinations(columns, 2):
        if corr_matrix.loc[col1, col2] > percentage:
            corr_combinations.append((col1, col2))

    return corr_combinations

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
        # Generate number of columns
                num_cols = fdp.ConsumeIntInRange(2, 5) # At least 2 columns required for combinations(..., 2)

                # Generate column names (list of strings)
                cols = []
                for i in range(num_cols):
                    # Generate unique enough names. Pandas handles duplicate names by renaming.
                    cols.append(''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10))))

                # Generate number of rows
                num_rows = fdp.ConsumeIntInRange(1, 10) # Correlation can be computed with >=1 row, will be NaN for 1 row.

                # Generate data (list of lists of floats)
                data = []
                for _ in range(num_rows):
                    row = []
                    for _ in range(num_cols):
                        # Data points are floats based on the example and problem context
                        row.append(fdp.ConsumeIntInRange(-10000, 10000) / 100.0)
                    data.append(row)

                # Generate percentage (float between 0 and 1)
                percentage = fdp.ConsumeIntInRange(0, 100) / 100.0

                out_a = solve_a(data, cols, percentage)
                out_b = solve_b(data, cols, percentage)
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
