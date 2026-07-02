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
from dateutil.parser import parse
import datetime


def _solve_a_impl(date_str, from_tz, to_tz):
    """
    Convert a date string from one time zone to another and return the time difference in seconds to the current time
    in the destination time zone.

    Parameters:
    date_str (str): The date string in "yyyy-mm-dd hh:mm:ss" format.
    from_tz (str): The timezone of the given date string.
    to_tz (str): The timezone to which the date string should be converted.

    Returns:
    int: The time difference in seconds.

    Requirements:
    - pytz
    - dateutil.parser
    Example:
    >>> type(_solve_a_impl('2022-10-22 11:59:59', 'UTC', 'America/Chicago'))
    <class 'int'>
    """
    # Get timezone objects for the source and destination timezones
    from_tz_obj = pytz.timezone(from_tz)
    to_tz_obj = pytz.timezone(to_tz)

    # Parse the given date string and localize it to the source timezone
    given_date_naive = parse(date_str)
    given_date = from_tz_obj.localize(given_date_naive)

    # Convert the given date to the destination timezone
    given_date_in_to_tz = given_date.astimezone(to_tz_obj)

    # Get the current time in the destination timezone
    current_date_in_to_tz = datetime.now(pytz.utc).astimezone(to_tz_obj)

    # Calculate the time difference in seconds
    time_difference = current_date_in_to_tz - given_date_in_to_tz

    return int(time_difference.total_seconds())

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
        year = fdp.ConsumeIntInRange(1900, 2100)
        month = fdp.ConsumeIntInRange(1, 12)
        day = fdp.ConsumeIntInRange(1, 28) # Limiting day to 28 to avoid complexities with variable month lengths and leap years
        hour = fdp.ConsumeIntInRange(0, 23)
        minute = fdp.ConsumeIntInRange(0, 59)
        second = fdp.ConsumeIntInRange(0, 59)

        date_str = f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"

        # A representative list of common timezones that pytz recognizes
        tz_list = [
            'UTC',
            'America/New_York',
            'Europe/London',
            'Asia/Tokyo',
            'America/Chicago',
            'Australia/Sydney',
            'Pacific/Honolulu',
            'Indian/Chagos',
            'Atlantic/Canary',
            'Africa/Cairo',
            'Europe/Berlin',
            'Asia/Shanghai',
            'America/Los_Angeles'
        ]

        from_tz = fdp.PickValueInList(tz_list)
        to_tz = fdp.PickValueInList(tz_list)

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
