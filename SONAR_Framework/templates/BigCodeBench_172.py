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


import json
from datetime import datetime

def _solve_a_impl(json_data):
    """
    Determine if the given datetime is a weekend.

    Parameters:
    - json_data (str): JSON string containing the datetime in UTC format.

    Returns:
    bool: True if the date is a weekend (Saturday or Sunday), False otherwise.

    Note:
    - The datetime to be extracted is located in the 'utc_datetime' key in the JSON data.

    Requirements:
    - json
    - datetime

    Example:
    >>> json_data = '{"utc_datetime": "2024-04-19T12:00:00"}'
    >>> _solve_a_impl(json_data)
    False
    """
    try:
        # Convert JSON string to Python dictionary
        data = json.loads(json_data)

        # Extract datetime string from dictionary
        datetime_str = data['utc_datetime']

        # Convert datetime string to datetime object
        utc_datetime = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S')

        # Check if the day of the week is Saturday (5) or Sunday (6)
        return utc_datetime.weekday() >= 5
    except Exception as e:
        raise e

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
        # Generate components for a datetime string
                year = fdp.ConsumeIntInRange(1, 9999)
                month = fdp.ConsumeIntInRange(1, 12)
                # Limiting day to 28 to avoid issues with different month lengths and leap years,
                # ensuring all generated dates are valid.
                day = fdp.ConsumeIntInRange(1, 28)
                hour = fdp.ConsumeIntInRange(0, 23)
                minute = fdp.ConsumeIntInRange(0, 59)
                second = fdp.ConsumeIntInRange(0, 59)

                # Format the datetime components into the required string format
                datetime_str = f"{year:04d}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:02d}"

                # Create a dictionary with the 'utc_datetime' key
                json_dict = {"utc_datetime": datetime_str}

                # Convert the dictionary to a JSON string
                json_data_arg = json.dumps(json_dict)

                out_a = solve_a(json_data_arg)
                out_b = solve_b(json_data_arg)
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
