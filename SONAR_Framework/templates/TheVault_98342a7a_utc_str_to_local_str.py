import atheris
import sys
import random
from typing import List, Tuple, Dict, Optional, Any, Set
from collections import defaultdict, Counter, OrderedDict
from itertools import combinations, permutations, product
from functools import reduce
import math, re, hashlib, copy, string
import datetime
total = 0
matches = 0
_discarded = 0
MAX_CASES = 1000
_attempts = 0
MAX_ATTEMPTS = MAX_CASES * 5


def _solve_a_impl(utc_str: str, utc_format: str, local_format: str):
    temp1 = datetime.datetime.strptime(utc_str, utc_format)
    temp2 = temp1.replace(tzinfo=datetime.timezone.utc)
    local_time = temp2.astimezone()
    return local_time.strftime(local_format)

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
        import datetime

        # Generate components for a datetime object
        year = fdp.ConsumeIntInRange(1, 9999)
        month = fdp.ConsumeIntInRange(1, 12)
        # Limiting day to 28 avoids issues with month lengths and leap years, simplifying valid date generation.
        day = fdp.ConsumeIntInRange(1, 28)
        hour = fdp.ConsumeIntInRange(0, 23)
        minute = fdp.ConsumeIntInRange(0, 59)
        second = fdp.ConsumeIntInRange(0, 59)
        microsecond = fdp.ConsumeIntInRange(0, 999999)

        # Generate a timezone offset for the initial datetime object.
        # This ensures that timezone-related format specifiers like %z and %Z can be used successfully.
        tz_offset_hours = fdp.ConsumeIntInRange(-12, 14) # Common range for UTC offsets
        # Generate minute offsets, which can be 0, 15, 30, 45, etc.
        tz_offset_minutes_val = fdp.PickValueInList([0, 15, 30, 45])
        tz_offset_minutes = tz_offset_minutes_val * (1 if fdp.ConsumeBool() else -1) # Random positive/negative minute offset

        tz_delta = datetime.timedelta(hours=tz_offset_hours, minutes=tz_offset_minutes)
        tz = datetime.timezone(tz_delta)

        # Create a timezone-aware datetime object
        dt_obj = datetime.datetime(year, month, day, hour, minute, second, microsecond, tzinfo=tz)

        # Define a set of common strftime/strptime format components (specifiers and delimiters).
        # These are "specific characters" for format strings, so we pick from this list.
        format_components = [
            '%Y', '%m', '%d', '%H', '%M', '%S', '%f', '%y',  # Date/Time numeric components
            '%z', '%Z',  # Timezone components (will work as dt_obj is tz-aware)
            '-', '/', ' ', ':', '.',  # Common delimiters
            '%a', '%A', '%b', '%B',  # Locale-specific abbreviated/full weekday/month names
            '%j', '%w',  # Day of year, weekday number
            '%%',  # Literal percent sign
        ]

        # Generate utc_format by picking from the format_components list.
        # The length of the format string is also fuzzed.
        utc_format_len = fdp.ConsumeIntInRange(1, 25)  # Max length for generated format string
        utc_format = "".join(fdp.PickValueInList(format_components) for _ in range(utc_format_len))

        # Generate local_format similarly, to provide varied output formatting.
        local_format_len = fdp.ConsumeIntInRange(1, 25)
        local_format = "".join(fdp.PickValueInList(format_components) for _ in range(local_format_len))

        # Generate utc_str by formatting the datetime object using the generated utc_format.
        # This guarantees that utc_str is always parseable by strptime with utc_format,
        # which is crucial for the function to proceed beyond the initial parsing step.
        utc_str = dt_obj.strftime(utc_format)

        # Call the function under test (solve_a) and the reference implementation (solve_b)
        out_a = solve_a(utc_str, utc_format, local_format)
        out_b = solve_b(utc_str, utc_format, local_format)
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
