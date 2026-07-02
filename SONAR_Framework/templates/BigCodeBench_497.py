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


from datetime import datetime, timedelta
import pytz
import calendar


def _solve_a_impl(days_in_past=7):
    """
    Get the weekday of the date 'days_in_past' days ago from today.

    This function computes the date that is 'days_in_past' number of days ago from the current
    system time's date in UTC. It then determines the weekday of this target date using calendar
    and returns its name as a string.

    Parameters:
    days_in_past (int): The number of days to go back from the current date to find the weekday.
                        Defaults to 7 (one week ago). Must be a non-negative integer.

    Returns:
    weekday (str)     : The name of the weekday (e.g., 'Monday', 'Tuesday') for the computed date.

    Raises:
    ValueError: If 'days_in_past' is negative.
    
    Requirements:
    - datetime.datetime
    - datetime.timedelta
    - pytz
    - calendar

    Example:
    >>> _solve_a_impl()
    'Monday'
    >>> _solve_a_impl(3)
    'Friday'
    """
    if days_in_past < 0:
        raise ValueError("Days in the past cannot be negative")

    date = datetime.now(pytz.UTC) - timedelta(days=days_in_past)
    weekday = calendar.day_name[date.weekday()]

    return weekday

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
        days_in_past = fdp.ConsumeIntInRange(0, 365 * 10) # Non-negative integer, up to 10 years
        out_a = solve_a(days_in_past)
        out_b = solve_b(days_in_past)
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
