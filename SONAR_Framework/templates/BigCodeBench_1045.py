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


from datetime import datetime
import numpy as np
from dateutil.parser import parse

LEAP_SECONDS = np.array(
    [
        1972,
        1973,
        1974,
        1975,
        1976,
        1977,
        1978,
        1979,
        1980,
        1981,
        1982,
        1983,
        1985,
        1988,
        1990,
        1993,
        1994,
        1997,
        1999,
        2006,
        2009,
        2012,
        2015,
        2016,
        2020,
    ]
)


def _solve_a_impl(date_str):
    """
    Calculate the total number of seconds elapsed from a given date until the current time,
    including any leap seconds that occurred in this period.

    Parameters:
    date_str (str): The date and time from which to calculate, in "yyyy-mm-dd hh:mm:ss" format.

    Returns:
    int: The total number of elapsed seconds, including leap seconds, since the given date.

    Requirements:
    - datetime.datetime
    - numpy
    - dateutil.parser.parse
    
    Note:
    This function uses the datetime, numpy, and dateutil.parser modules.
    The LEAP_SECONDS array should contain years when leap seconds were added.

    Example:
    >>> total_seconds = _solve_a_impl('1970-01-01 00:00:00')
    >>> print(total_seconds)
    1702597276
    """
    given_date = parse(date_str)
    current_date = datetime.now()

    total_seconds = (current_date - given_date).total_seconds()

    # Count leap seconds that occurred between the two dates
    leap_seconds = np.sum(LEAP_SECONDS >= given_date.year)

    total_seconds += leap_seconds

    return int(total_seconds)

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
        # Generate year within a reasonable range for date parsing and leap second calculations
        year = fdp.ConsumeIntInRange(1900, 2030)

        # Generate month (1-12)
        month = fdp.ConsumeIntInRange(1, 12)

        # Generate day (1-28 to ensure validity for all months and simplify fuzzing)
        day = fdp.ConsumeIntInRange(1, 28)

        # Generate hour (0-23)
        hour = fdp.ConsumeIntInRange(0, 23)

        # Generate minute (0-59)
        minute = fdp.ConsumeIntInRange(0, 59)

        # Generate second (0-59)
        second = fdp.ConsumeIntInRange(0, 59)

        # Construct the date string in the specified "yyyy-mm-dd hh:mm:ss" format
        date_str = f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"

        # Call the function under test with the generated input
        out_a = solve_a(date_str)
        out_b = solve_b(date_str)
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
