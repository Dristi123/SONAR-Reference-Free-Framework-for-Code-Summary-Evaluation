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


def _solve_a_impl(column, data):
    """
    Analyzes a list of stock data and calculates the sum, mean, minimum, and maximum
    values for a specified column.

    Parameters:
    - column (str): The name of the column to analyze. Valid options are 'Date', 'Open', 'High',
                    'Low', 'Close', and 'Volume'.
    - data (list of lists): A list where each element is a list representing stock data for a single day.
                            Each inner list should contain values in the following order:
                            'Date', 'Open', 'High', 'Low', 'Close', 'Volume'.
    Returns:
    - dict: A dictionary containing the calculated 'sum', 'mean', 'min' (minimum), and 'max' (maximum)
            for the specified column. If the input data is empty, 'sum' will be 0, and 'mean', 'min', and
            'max' will be NaN.

    Requirements:
    - pandas
    - numpy

    Raises:
    - ValueError: If the specified column name is not valid.
    
    Example:
    >>> data = [[datetime(2022, 1, 1), 100, 105, 95, 102, 10000]]
    >>> results = _solve_a_impl('Open', data)
    >>> results
    {'sum': 100, 'mean': 100.0, 'min': 100, 'max': 100}
    >>> type(results)
    <class 'dict'>
    """
    valid_columns = ["Date", "Open", "High", "Low", "Close", "Volume"]
    if column not in valid_columns:
        raise ValueError(f"Invalid column name.")
    if not isinstance(data, list) or (
        len(data) > 0
        and not all(
            isinstance(row, list) and len(row) == len(valid_columns) for row in data
        )
    ):
        raise ValueError(
            "Data must be a list of lists, with each inner list matching the length of the column names."
        )

    df = pd.DataFrame(data, columns=valid_columns)
    column_data = df[column]

    result = {
        "sum": np.sum(column_data) if not column_data.empty else 0,
        "mean": np.mean(column_data) if not column_data.empty else float("nan"),
        "min": np.min(column_data) if not column_data.empty else float("nan"),
        "max": np.max(column_data) if not column_data.empty else float("nan"),
    }

    return result

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
        valid_columns = ["Date", "Open", "High", "Low", "Close", "Volume"]
        column = fdp.PickValueInList(valid_columns)

        num_rows = fdp.ConsumeIntInRange(0, 10) # Generate up to 10 rows of stock data, including 0 for empty data case
        data = []
        for _ in range(num_rows):
            row = []
            # Generate values for each of the 6 columns
            # 'Date' can be represented numerically for fuzzing as the function uses np.sum/mean/min/max
            row.append(fdp.ConsumeIntInRange(0, 100000000) / 100.0) # Date as a float timestamp/value
            # 'Open', 'High', 'Low', 'Close', 'Volume' are typically numerical (floats)
            for _ in range(5):
                row.append(fdp.ConsumeIntInRange(-10000, 10000) / 100.0)
            data.append(row)

        out_a = solve_a(column, data)
        out_b = solve_b(column, data)
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
