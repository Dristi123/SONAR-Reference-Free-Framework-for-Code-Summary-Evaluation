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

# Constants
TIME_FORMAT = "%d/%m/%y %H:%M:%S.%f"


def _solve_a_impl(time_string, from_tz, to_tz):
    """
    Converts a time string from one timezone to another, considering various cases such as daylight saving time.

    Parameters:
    - time_string (str): A time string in the format 'dd/mm/yy HH:MM:SS.fff'. This string should represent a valid date and time.
    - from_tz (str): The timezone of the given time string. The timezone should be a valid IANA timezone name (e.g., 'UTC', 'America/New_York').
    - to_tz (str): The target timezone to which the time string should be converted. This should also be a valid IANA timezone name (e.g., 'Asia/Tokyo').

    Returns:
    - str: The converted time string in the format 'dd/mm/yy HH:MM:SS.fff'. The conversion takes into account any differences in daylight saving rules between the source and target timezones.

    Requirements:
    - pytz
    - dateutil

    Example:
    >>> _solve_a_impl('30/03/09 16:31:32.123', 'UTC', 'America/New_York')
    '30/03/09 12:31:32.123000'

    Note: The example assumes no daylight saving time shift between the given timezones at the specified date and time.
    """
    from_zone = pytz.timezone(from_tz)
    to_zone = pytz.timezone(to_tz)
    dt = parse(time_string, dayfirst=True)
    dt = from_zone.localize(dt)
    dt = dt.astimezone(to_zone)

    return dt.strftime(TIME_FORMAT)

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
        # To ensure a valid list of timezones is available for fdp.PickValueInList,
        # we define a representative subset here. In a full fuzzing script,
        # this list would typically be generated once globally from pytz.all_timezones.
        _TIMEZONE_NAMES = [
            'UTC', 'America/New_York', 'Europe/London', 'Asia/Tokyo',
            'America/Los_Angeles', 'Europe/Berlin', 'Australia/Sydney',
            'Pacific/Honolulu', 'Africa/Cairo', 'America/Sao_Paulo'
        ]

        # Generate components for the time_string in 'dd/mm/yy HH:MM:SS.fff' format
        day = fdp.ConsumeIntInRange(1, 31)
        month = fdp.ConsumeIntInRange(1, 12)
        year = fdp.ConsumeIntInRange(0, 99) # Represents 'yy' part, e.g., 00-99
        hour = fdp.ConsumeIntInRange(0, 23)
        minute = fdp.ConsumeIntInRange(0, 59)
        second = fdp.ConsumeIntInRange(0, 59)
        millisecond = fdp.ConsumeIntInRange(0, 999) # For '.fff' part

        # Format the components into the required time_string format
        time_string = "{:02d}/{:02d}/{:02d} {:02d}:{:02d}:{:02d}.{:03d}".format(
            day, month, year, hour, minute, second, millisecond
        )

        # Pick valid IANA timezone names from our predefined list
        from_tz = fdp.PickValueInList(_TIMEZONE_NAMES)
        to_tz = fdp.PickValueInList(_TIMEZONE_NAMES)

        # Call the function under test with the fuzzed inputs
        out_a = solve_a(time_string, from_tz, to_tz)
        out_b = solve_b(time_string, from_tz, to_tz)
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
