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
import math


def _solve_a_impl(decimal_value, precision=2):
    """
    Calculate the square root of the given decimal value to a certain precision and then encode the result as a JSON string.
    
    Parameters:
    utc_datetime (datetime): The datetime in UTC.
    precision (int, Optional): The number of decimal places to round the square root to. Defaults to 2.
    
    Returns:
    str: The square root of the decimal value encoded as a JSON string.
    
    Requirements:
    - json
    - math
    
    Example:
    >>> from decimal import Decimal
    >>> decimal_value = Decimal('3.9')
    >>> json_str = _solve_a_impl(decimal_value, decimal_value)
    >>> print(json_str)
    "1.97"
    """
    # Calculate the square root of the decimal value
    square_root = round(math.sqrt(decimal_value), 2)
    
    # Encode the result as a JSON string
    json_str = json.dumps(str(square_root))
    
    return json_str

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
        # decimal_value: The problem description states "decimal value".
        # The function uses math.sqrt(decimal_value), which expects a float or an integer,
        # and it must be non-negative for real square roots.
        # The example uses Decimal('3.9'), but math.sqrt would raise a TypeError for a Decimal object.
        # Given the `math` module is imported and used, and no `decimal` module is imported,
        # it's most reasonable to generate a standard float value.
        # We generate a float from 0.00 to 100.00 to ensure non-negativity and a reasonable range.
        decimal_value = fdp.ConsumeIntInRange(0, 10000) / 100.0

        # precision: This is an optional integer parameter with a default of 2.
        # It's used in the rounding operation. A reasonable range for precision in rounding is 0 to 10.
        # We will always consume and pass a value for precision to fully test the parameter.
        precision = fdp.ConsumeIntInRange(0, 10)

        out_a = solve_a(decimal_value, precision)
        out_b = solve_b(decimal_value, precision)
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
