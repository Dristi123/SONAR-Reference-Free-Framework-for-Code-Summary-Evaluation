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
from scipy.stats import norm


def _solve_a_impl(data: np.ndarray, threshold: float = 2.0) -> list:
    """
    Determine the outlier indices in a 1D numpy array based on the Z score.

    First a normal distribution is fitted to the data, the mean and standard
    deviation is used to calculate the z scores of each datapoint. 
    If the absolute z score of a datapoint is larger than threshold it is
    considered an outlier and its index is recorded.

    If the standard deviation is 0, an empty list is returned as outliers. 
    
    Parameters:
    data (numpy.ndarray): The 1D numpy array to check for outliers.
    threshold (float): The outlier threshold. Defaults to 2.

    Returns:
    list: The indices of outliers in the data where Z score > threshold. Empty if standard deviation is 0
    float: The mean of the fitted normal distribution.
    float: The variance of the fitted normal distribution.

    Requirements:
    - numpy 
    - scipy.stats.norm

    Example:
    >>> data = np.array([1, 2, 3, 4, 5, 6, 100])
    >>> _solve_a_impl(data)
    ([6], 17.285714285714285, 1142.7755102040817)
    
    >>> data = np.array([-10, 3, 5, 5, 5, 5, 5, 7, 20])
    >>> outliers, mean, var = _solve_a_impl(data, threshold=4)
    >>> print(outliers)
    []
    >>> print(mean)
    5.0
    >>> print(var)
    50.888888888888886

      
    """
    # Calculate the z-scores
    mean, std_dev = norm.fit(data)
    if std_dev == 0:
        return [], mean, std_dev**2
    z_scores = (data - mean) / std_dev
    outliers = np.where(np.abs(z_scores) > threshold)

    return list(outliers[0]), mean, std_dev**2

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
        # Generate input for 'data' (1D numpy array)
            data_length = fdp.ConsumeIntInRange(1, 100)  # Array length from 1 to 100
            # The examples use integer data, so we generate a list of integers
            data_list = [fdp.ConsumeIntInRange(-1000, 1000) for _ in range(data_length)]
            data_np = np.array(data_list)

            # Generate input for 'threshold' (float)
            # Threshold should be non-negative. We generate a float between 0.0 and 100.0
            threshold_val = fdp.ConsumeIntInRange(0, 10000) / 100.0

            # Call the function under test with the generated inputs
            out_a = solve_a(data_np, threshold_val)
            out_b = solve_b(data_np, threshold_val)
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
