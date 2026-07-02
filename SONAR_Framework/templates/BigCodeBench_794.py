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


import string
import random



def _solve_a_impl(length, random_seed=None):
    """
    Generate a random string of a given length, with each character being either
    a parenthesis (from the set "(){}[]") 
    or a lowercase English character.
    For function uses a optional random_seed when sampling characters.

    Parameters:
    length (int): The length of the string to generate.
    random_seed (int): Random seed for rng. Used in picking random characters.
                       Defaults to None.

    Returns:
    str: The generated string.

    Requirements:
    - string
    - random

    Note: The function uses the internal string constant BRACKETS for 
          definition of the bracket set.

    Example:
    >>> string = _solve_a_impl(10, random_seed=1)
    >>> print(string)
    ieqh]{[yng
    
    >>> string = _solve_a_impl(34, random_seed=42)
    >>> print(string)
    hbrpoigf)cbfnobm(o{rak)vrjnvgfygww

    >>> string = _solve_a_impl(23, random_seed=1)
    >>> print(string)
    ieqh]{[yng]by)a{rogubbb
    """
    random.seed(random_seed)
    # Constants
    BRACKETS = "(){}[]"
    return ''.join(random.choice(string.ascii_lowercase + BRACKETS) for _ in range(length))

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
        length = fdp.ConsumeIntInRange(0, 100) # Length can be 0, resulting in an empty string.
        use_custom_seed = fdp.ConsumeBool()
        if use_custom_seed:
            random_seed_val = fdp.ConsumeInt(8) # Use ConsumeInt(8) for a wide range of integer seeds
        else:
            random_seed_val = None

        random.seed(random_seed_val)
        out_a = solve_a(length, random_seed=random_seed_val)

        random.seed(random_seed_val) # Re-seed for the second function call
        out_b = solve_b(length, random_seed=random_seed_val)
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
