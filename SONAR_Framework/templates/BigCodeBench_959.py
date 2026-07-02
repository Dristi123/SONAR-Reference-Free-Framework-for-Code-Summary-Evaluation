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


def _solve_a_impl(text, seed=None):
    """
    Transforms the input text by replacing each alphabetic character with a random letter,
    while preserving the case and non-alphabetic characters of the original text.

    Parameters:
    - text (str): The input text to be transformed.
    - seed (int, optional): Random seed for reproducibility. Defaults to None (not set).

    Returns:
    - str: A transformed string with random letters replacing the alphabetic characters of the input text,
      preserving non-alphabetic characters and the original case.

    Requirements:
    - string
    - random

    Notes:
    - Alphabet replacements are chosen from ascii characters of the same case as the original.

    Example:
    >>> text = 'Hello, world!'
    >>> _solve_a_impl(text, 0)
    'Mynbi, qpmzj!'
    """

    def replace_with_random_char(c):
        if c.isalpha():
            if c.islower():
                return random.choice(string.ascii_lowercase)
            else:
                return random.choice(string.ascii_uppercase)
        return c

    if seed is not None:
        random.seed(seed)
    return "".join(replace_with_random_char(c) for c in text)

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
        char_pool = list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ') + list('0123456789 .,!?-')
        text_len = fdp.ConsumeIntInRange(1, 50)
        text = ''.join(fdp.PickValueInList(char_pool) for _ in range(text_len))

        # The 'seed' parameter is optional. Use a boolean to decide if it's None or an int.
        use_seed_param = fdp.ConsumeBool()
        seed_val = None
        if use_seed_param:
            seed_val = fdp.ConsumeIntInRange(0, 1000000) # A wide range for the seed integer

        # Generate a fixed seed for the global 'random' module state for Atheris's requirement.
        # This ensures that if 'seed_val' is None, both solve_a and solve_b experience the same random sequence.
        # If 'seed_val' is not None, task_func will internally set its own seed, overriding this global state,
        # but the rule still requires setting it before each call.
        fuzz_random_seed = fdp.ConsumeIntInRange(0, 1000000)

        random.seed(fuzz_random_seed)
        out_a = solve_a(text, seed_val)

        random.seed(fuzz_random_seed)
        out_b = solve_b(text, seed_val)
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
