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
import collections

# Constants
VALID_CHARACTERS = string.ascii_letters + string.digits

def _solve_a_impl(n_strings, string_length):
    """
    Generate n random strings of a specified length, count the frequency of each character across all strings, and return the result as a dictionary.

    Parameters:
    - n_strings (int): The number of random strings to generate.
    - string_length (int): The length of each random string.

    Returns:
    - dict: A dictionary containing character counts with characters as keys and their frequencies as values.

    Requirements:
    - random
    - string
    - collections

    Constants:
    - VALID_CHARACTERS: A string containing all valid characters (ASCII letters and digits) that can be used in the random strings.

    Example:
    >>> random.seed(42)
    >>> _solve_a_impl(2, 3)
    {'O': 1, 'h': 1, 'b': 1, 'V': 1, 'r': 1, 'p': 1}
    """
    strings = [''.join(random.choice(VALID_CHARACTERS) for _ in range(string_length)) for _ in range(n_strings)]
    character_counts = collections.Counter(''.join(strings))
    return dict(character_counts)

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
      
            n_strings = fdp.ConsumeIntInRange(1, 50)
            string_length = fdp.ConsumeIntInRange(1, 50)

            random.seed(42)
            out_a = solve_a(n_strings, string_length)
            random.seed(42)
            out_b = solve_b(n_strings, string_length)
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
