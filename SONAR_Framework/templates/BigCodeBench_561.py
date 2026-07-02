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
from dateutil import parser

def _solve_a_impl(date_str, from_tz, to_tz):
    """
    Converts a date time from one timezone to another.

    Parameters:
    date_str (str): The date string in "yyyy-mm-dd hh:mm:ss" format.
    from_tz (str): The timezone of the given date string.
    to_tz (str): The timezone to which the date should be converted.

    Returns:
    str: The converted datetime string in "yyyy-mm-dd hh:mm:ss" format.

    Requirements:
    - pytz
    - dateutil.parser

    Example:
    >>> _solve_a_impl('2022-03-01 12:00:00', 'UTC', 'America/New_York')
    '2022-03-01 07:00:00'
    """
    from_tz = pytz.timezone(from_tz)
    to_tz = pytz.timezone(to_tz)
    date = parser.parse(date_str).replace(tzinfo=from_tz)
    date = date.astimezone(to_tz)

    return date.strftime('%Y-%m-%d %H:%M:%S')

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
        # Generate date_str in "yyyy-mm-dd hh:mm:ss" format
                year = fdp.ConsumeIntInRange(1, 9999)
                month = fdp.ConsumeIntInRange(1, 12)
                # Limit day to 28 to avoid complexities with varying month lengths and leap years
                day = fdp.ConsumeIntInRange(1, 28)
                hour = fdp.ConsumeIntInRange(0, 23)
                minute = fdp.ConsumeIntInRange(0, 59)
                second = fdp.ConsumeIntInRange(0, 59)
                date_str = f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"

                # Generate from_tz and to_tz from a list of valid IANA timezone names
                # A curated list of common timezones to ensure valid pytz.timezone calls
                valid_timezones = [
                    'UTC', 'America/New_York', 'America/Los_Angeles', 'Europe/London',
                    'Europe/Berlin', 'Asia/Tokyo', 'Asia/Shanghai', 'Australia/Sydney',
                    'Africa/Cairo', 'Brazil/East', 'Pacific/Honolulu', 'Indian/Maldives'
                ]
                from_tz = fdp.PickValueInList(valid_timezones)
                to_tz = fdp.PickValueInList(valid_timezones)

                # Call the function under test with the generated arguments
                out_a = solve_a(date_str, from_tz, to_tz)
                out_b = solve_b(date_str, from_tz, to_tz) # Assuming solve_a and solve_b are the same function for fuzzing
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
