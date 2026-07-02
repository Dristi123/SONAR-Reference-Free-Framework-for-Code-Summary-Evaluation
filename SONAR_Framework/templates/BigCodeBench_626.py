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


from random import choice
import pytz
from dateutil.parser import parse

# Constants
TIMEZONES = ['America/New_York', 'Europe/London', 'Asia/Shanghai', 'Asia/Tokyo', 'Australia/Sydney']


def _solve_a_impl(date_str, from_tz):
    """
    Converts a datetime string from a given timezone to a datetime string in a randomly chosen timezone.

    Parameters:
    - date_str (str): The datetime string in "yyyy-mm-dd hh:mm:ss" format.
    - from_tz (str): The timezone of the given datetime string.

    Returns:
    - tuple: A tuple containing the converted datetime string and the randomly chosen timezone.
    
    Requirements:
    - pytz
    - dateutil.parser
    - random

    Example:
    >>> date_str, from_tz = '2023-06-15 12:00:00', 'UTC'
    >>> converted_date, to_tz = _solve_a_impl(date_str, from_tz)
    >>> to_tz in TIMEZONES
    True
    """
    from_tz = pytz.timezone(from_tz)
    to_tz = pytz.timezone(choice(TIMEZONES))
    given_date = parse(date_str).replace(tzinfo=from_tz)
    converted_date = given_date.astimezone(to_tz)

    return converted_date.strftime('%Y-%m-%d %H:%M:%S'), to_tz.zone

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
                year = str(fdp.ConsumeIntInRange(1900, 2100)).zfill(4)
                month = str(fdp.ConsumeIntInRange(1, 12)).zfill(2)
                # Limiting day to 28 to avoid issues with month-specific day counts (e.g., Feb 30)
                day = str(fdp.ConsumeIntInRange(1, 28)).zfill(2)
                hour = str(fdp.ConsumeIntInRange(0, 23)).zfill(2)
                minute = str(fdp.ConsumeIntInRange(0, 59)).zfill(2)
                second = str(fdp.ConsumeIntInRange(0, 59)).zfill(2)
                date_str = f"{year}-{month}-{day} {hour}:{minute}:{second}"

                # Generate from_tz by picking from a list of valid timezones
                # Combine TIMEZONES from the constants with other common pytz-compatible timezones
                all_possible_from_timezones = TIMEZONES + ['UTC', 'GMT', 'Europe/Paris', 'Asia/Kolkata', 'US/Eastern', 'Etc/GMT+1']
                from_tz = fdp.PickValueInList(all_possible_from_timezones)

                # Set random seed before calling the function to ensure reproducible random choices
                # within the function (specifically random.choice(TIMEZONES))
                random.seed(42)
                out_a = solve_a(date_str, from_tz)

                # Set random seed again for the second call to ensure identical random choices
                random.seed(42)
                out_b = solve_b(date_str, from_tz)
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
