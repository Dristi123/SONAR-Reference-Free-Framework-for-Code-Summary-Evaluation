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

# Constants
LETTERS = string.ascii_letters
DIGITS = string.digits

def _solve_a_impl(length, num_digits):
    """
    Generate a random password with a specified length and number of digits.

    The function creates a random password consisting of letters and digits. The total length of the password
    and the number of digits in it are specified by the user. The characters in the password are randomly
    shuffled to ensure variability.

    Parameters:
    - length (int): The total length of the password. Must be a positive integer.
    - num_digits (int): The number of digits to be included in the password. Must be a non-negative integer and
                      less than or equal to the total length of the password.

    Returns:
    - str: A string representing the randomly generated password.

    Requirements:
    - random
    - string

    Examples:
    >>> _solve_a_impl(10, 3)
    'Vpbr812Ooh'
    >>> _solve_a_impl(5, 2)
    '4Ob3h'
    """

    random.seed(42)
    if length <= 0:
        raise ValueError("Length must be a positive integer.")
    if not (0 <= num_digits <= length):
        raise ValueError("num_digits must be a non-negative integer and less than or equal to length.")

    password = []
    for _ in range(length - num_digits):
        password.append(random.choice(LETTERS))
    for _ in range(num_digits):
        password.append(random.choice(DIGITS))

    random.shuffle(password)

    return ''.join(password)

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
        length = fdp.ConsumeIntInRange(1, 100) # Length must be a positive integer.
        num_digits = fdp.ConsumeIntInRange(0, length) # num_digits must be non-negative and <= length.

        random.seed(42)
        out_a = solve_a(length, num_digits)
        random.seed(42) # Re-seed for the second call to ensure identical random sequences
        out_b = solve_b(length, num_digits)
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
