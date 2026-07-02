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
from statsmodels.tsa.seasonal import seasonal_decompose

def _solve_a_impl(start_date='2016-01-01', periods=24, freq='M', model='additive'):
    """
    Generate a sales time-series and decompose it into trend, seasonal, and residual components.
    
    Parameters:
    - start_date (str): The start date of the time-series in the format 'YYYY-MM-DD'. Default is '2016-01-01'.
    - periods (int): The number of periods to generate for the time-series. Default is 24.
    - freq (str): The frequency of the time-series data. Default is 'M' (Monthly End).
    - model (str): The type of seasonal decomposition ('additive' or 'multiplicative'). Default is 'additive'.

    Returns:
    - A dictionary containing 'trend', 'seasonal', and 'residual' components as Pandas Series.
    
    Requirements:
    - numpy
    - pandas
    - statsmodels
    
    Examples:
    >>> result = _solve_a_impl('2016-01-01', 24, 'M')
    >>> all(key in result for key in ['trend', 'seasonal', 'residual'])
    True

    >>> result = _solve_a_impl('2020-01-01', 24, 'M', 'multiplicative')
    >>> len(result['seasonal'])
    24
    """
    date_range = pd.date_range(start=start_date, periods=periods, freq=freq)
    sales_data = np.random.randint(low=100, high=500, size=periods)
    sales_series = pd.Series(sales_data, index=date_range)
    try:
        decomposition = seasonal_decompose(sales_series, model=model, period=12 if freq == 'M' else 4)
    except ValueError as e:
        return {'error': str(e)}
    
    return {
        'trend': decomposition.trend,
        'seasonal': decomposition.seasonal,
        'residual': decomposition.resid
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
        # Generate start_date components and format them
        year = fdp.ConsumeIntInRange(1900, 2100) # A reasonable range for years
        month = fdp.ConsumeIntInRange(1, 12)
        # Using 1-28 for day to avoid complexities with variable month lengths and leap years
        day = fdp.ConsumeIntInRange(1, 28) 
        start_date = f"{year:04d}-{month:02d}-{day:02d}"

        # Generate periods (number of data points)
        periods = fdp.ConsumeIntInRange(1, 100) # Keep the number of periods relatively small for performance

        # Generate frequency for the time-series
        # Based on common pandas frequencies and the function's internal logic for `period`
        freq = fdp.PickValueInList(['D', 'W', 'M', 'Q', 'Y'])

        # Generate the model type for seasonal decomposition
        model = fdp.PickValueInList(['additive', 'multiplicative'])

        # The function uses np.random.randint internally, so we need to seed numpy's random
        # to ensure consistent results between the two calls.
        np.random.seed(42)
        out_a = solve_a(start_date=start_date, periods=periods, freq=freq, model=model)

        # Reset the seed for the second call
        np.random.seed(42)
        out_b = solve_b(start_date=start_date, periods=periods, freq=freq, model=model)
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
