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


import pytz
import numpy as np
from dateutil.parser import parse
import math


SOLAR_CYCLE_YEARS = np.array([1986, 1996, 2008, 2019])

def _solve_a_impl(date_str, from_tz, to_tz):
    """
    Calculate solar activity based on the date and time, taking into account the solar cycle of 11 years.

    Parameters:
    date_str (str): The date string in "yyyy-mm-dd hh:mm:ss" format.
    from_tz (str): The timezone of the given date string.
    to_tz (str): The timezone to which the given date and time should be converted.

    Returns:
    float: The solar activity between 0 and 1. The value represents the solar activity 
           calculated using a cosine function based on the years since the closest solar cycle year.

    Requirements:
    - pytz
    - numpy
    - dateutil.parser
    - math

    Example:
    >>> _solve_a_impl('1970-01-01 00:00:00', 'UTC', 'America/New_York')
    0.14231483827328487
    >>> _solve_a_impl('1990-01-01 00:00:00', 'UTC', 'America/New_York')
    0.6548607339452851
    """
    from_tz = pytz.timezone(from_tz)
    to_tz = pytz.timezone(to_tz)
    given_date = parse(date_str).replace(tzinfo=from_tz)
    converted_date = given_date.astimezone(to_tz)

    solar_cycle_year = SOLAR_CYCLE_YEARS[np.argmin(np.abs(SOLAR_CYCLE_YEARS - converted_date.year))]
    years_since_solar_cycle_year = abs(converted_date.year - solar_cycle_year)

    solar_activity = math.cos(math.pi * years_since_solar_cycle_year / 11)

    return solar_activity

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
        TIMEZONE_LIST = [
            'UTC',
            'America/New_York',
            'America/Los_Angeles',
            'Europe/London',
            'Europe/Berlin',
            'Asia/Tokyo',
            'Australia/Sydney',
            'Africa/Cairo',
            'America/Chicago',
            'Asia/Shanghai',
            'Indian/Maldives',
            'Atlantic/Azores'
        ]

        year = fdp.ConsumeIntInRange(1900, 2100)
        month = fdp.ConsumeIntInRange(1, 12)
        # Limiting day to 1-28 to avoid issues with varying days in months (e.g., Feb, Apr, Jun)
        day = fdp.ConsumeIntInRange(1, 28)
        hour = fdp.ConsumeIntInRange(0, 23)
        minute = fdp.ConsumeIntInRange(0, 59)
        second = fdp.ConsumeIntInRange(0, 59)

        date_str = f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"

        from_tz = fdp.PickValueInList(TIMEZONE_LIST)
        to_tz = fdp.PickValueInList(TIMEZONE_LIST)

        out_a = solve_a(date_str, from_tz, to_tz)
        out_b = solve_b(date_str, from_tz, to_tz)
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
