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


import random
import string
import base64
import zlib
def _solve_a_impl(string_length=100):
    """
    Create a random string of a specified length with uppercase letters and digits, compress it with zlib, 
    and then encode the compressed string in base64.

    Parameters:
    - string_length (int, optional): The length of the random string to be generated. Default is 100.

    Returns:
    str: The compressed string in base64.

    Requirements:
    - base64
    - zlib
    - random
    - string

    Example:
    >>> random.seed(1)
    >>> compressed_string = _solve_a_impl(50)
    >>> print(compressed_string)
    eJxzNTH0CgqMMHJxMgkwdAyM8rQwc3IMMffzCHDyCAjy9PQI9HY0CY1wtzRx9YmKMg8wjgQAWN0NxA==
    """
    # Generate a random string
    random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=string_length))
    
    # Compress the string
    compressed_string = zlib.compress(random_string.encode('utf-8'))
    
    # Encode the compressed string in base64
    encoded_compressed_string = base64.b64encode(compressed_string)

    return encoded_compressed_string.decode('utf-8')

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
        if fdp.ConsumeBool():
            string_length_val = fdp.ConsumeIntInRange(0, 500) # Choose a reasonable max length for fuzzing
            random.seed(42)
            out_a = solve_a(string_length=string_length_val)
            random.seed(42)
            out_b = solve_b(string_length=string_length_val)
        else:
            # Test with default string_length
            random.seed(42)
            out_a = solve_a()
            random.seed(42)
            out_b = solve_b()
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
