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
import pytz

# Constants
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


def _solve_a_impl(unix_timestamp, target_timezone):
    """
    Converts a Unix timestamp to a formatted date and time string in a specified timezone.

    Parameters:
    unix_timestamp (int): The Unix timestamp representing the number of seconds since the Unix Epoch (January 1, 1970, 00:00:00 UTC).
    target_timezone (str): The string identifier of the target timezone (e.g., 'America/New_York').

    Returns:
    str: A string representing the date and time in the target timezone, formatted as '%Y-%m-%d %H:%M:%S'.

    Requirements:
    - datetime.datetime
    - pytz

    Example:
    >>> unix_timestamp = 1609459200
    >>> target_timezone = 'America/New_York'
    >>> _solve_a_impl(unix_timestamp, target_timezone)
    '2020-12-31 19:00:00'
    """
    # Convert the Unix timestamp to a UTC datetime object
    datetime_utc = datetime.utcfromtimestamp(unix_timestamp).replace(tzinfo=pytz.utc)

    # Convert the UTC datetime to the target timezone
    datetime_in_target_timezone = datetime_utc.astimezone(pytz.timezone(target_timezone))

    # Format the datetime object in the target timezone to the specified string format
    formatted_datetime = datetime_in_target_timezone.strftime(DATE_FORMAT)

    return formatted_datetime

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
        # Generate unix_timestamp
                # A reasonable range for Unix timestamps (seconds since epoch) to cover a few decades around the present.
                # From 1970-01-01 00:00:00 UTC (0) up to roughly 2050 (approx 2.5 billion seconds).
                unix_timestamp = fdp.ConsumeIntInRange(0, 2_500_000_000)

                # Generate target_timezone
                # The function expects a valid timezone string. Fuzzing with arbitrary strings would
                # primarily lead to pytz.exceptions.UnknownTimeZoneError. To test the core logic of
                # date conversion, we should provide valid timezone identifiers.
                # pytz.all_timezones provides a comprehensive list of known timezones.
                # We need to ensure pytz is imported at the top level of the fuzzing script for this.
                target_timezone = fdp.PickValueInList(list(pytz.all_timezones))

                # Call the functions with the generated inputs
                out_a = solve_a(unix_timestamp, target_timezone)
                out_b = solve_b(unix_timestamp, target_timezone)
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
