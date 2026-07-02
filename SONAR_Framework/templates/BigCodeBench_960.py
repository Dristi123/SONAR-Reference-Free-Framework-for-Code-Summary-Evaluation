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
    Generates a password that mirrors the structure of the given text by replacing alphabetic
    characters with random ascii lowercase letters, digits with random single-digit numbers,
    spaces wth either a random digit or random lowercase letter at equal probabilities, and
    leaving other characters unchanged.

    Parameters:
    - text (str): The text to be mirrored in the generated password. Must not be empty.
    - seed (int, optional): Seed for the random number generator. Defaults to None (not set).

    Returns:
    - str: The generated password.

    Raises:
    - ValueError: If the input text is empty.

    Requirements:
    - random
    - string

    Note:
    - This function does not handle high Unicode characters and focuses only on ASCII values.

    Examples:
    >>> _solve_a_impl("hello world! 123", 0)
    'mbqmp3jytre!v553'
    >>> _solve_a_impl("apple321#", seed=42)
    'uahev901#'
    """
    if seed is not None:
        random.seed(seed)
    if not text:
        raise ValueError("text cannot be empty.")
    password = ""
    for char in text:
        random_lowercase = random.choice(string.ascii_lowercase)
        random_digit = random.choice(string.digits)
        if char.isalpha():
            password += random_lowercase
        elif char.isdigit():
            password += random_digit
        elif char == " ":
            if random.random() < 0.5:
                password += random_lowercase
            else:
                password += random_digit
        else:
            password += char
    return password

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
       
            text_length = fdp.ConsumeIntInRange(1, 100) # text must not be empty
                    # The function replaces letters, digits, spaces, and leaves other characters unchanged.
                    # It focuses on ASCII values. To cover all relevant branches (isalpha, isdigit, space, other),
                    # we generate text from a pool of ASCII letters (upper and lower), digits, spaces, and punctuation.
            char_pool = string.ascii_letters + string.digits + " " + string.punctuation
            text_input = ''.join(fdp.PickValueInList(list(char_pool)) for _ in range(text_length))

            has_seed = fdp.ConsumeBool()
            if has_seed:
                # Seed can be any hashable object, but integers are most common.
                # fdp.ConsumeInt(4) generates a 32-bit integer.
                seed_input = fdp.ConsumeInt(4)
            else:
                seed_input = None

            random.seed(42)
            out_a = solve_a(text_input, seed_input)
            random.seed(42)
            out_b = solve_b(text_input, seed_input)
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
