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


import base64
import binascii
import os
import hashlib

def _solve_a_impl(hex_str, salt_size):
    """
    Converts a hex string to bytes, salts it with a random value of specified size, and computes its SHA256 hash.

    The function generates a random salt of the given size, appends it to the byte representation of the
    hex string, and then computes the SHA256 hash of the salted data. The salt and hash
    are returned as a tuple.

    Parameters:
        hex_str (str): The hex string to be hashed.
        salt_size (int): The size of the random salt to be generated.

    Returns:
        tuple: A tuple containing the base64-encoded salt and the SHA256 hash.

    Requirements:
    - base64
    - binascii
    - os
    - hashlib

    Examples:
    >>> result = _solve_a_impl("F3BE8080", 16)
    >>> isinstance(result, tuple) and len(result) == 2
    True
    >>> isinstance(result[0], str) and isinstance(result[1], str)
    True
    """
    salt = os.urandom(salt_size)
    data = binascii.unhexlify(hex_str.replace('\\x', ''))
    salted_data = salt + data
    hash_value = hashlib.sha256(salted_data).hexdigest()

    return (base64.b64encode(salt).decode('utf-8'), hash_value)

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
        # Generate hex_str
                # A hex string must have an even number of hex characters for binascii.unhexlify.
                # Let's pick a length for the 'raw' hex characters, then double it.
                # Max 50 hex pairs means 100 hex characters, a reasonable upper bound.
                num_hex_pairs = fdp.ConsumeIntInRange(0, 50) 
                hex_chars_pool = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']
                hex_str = ''.join(fdp.PickValueInList(hex_chars_pool) for _ in range(num_hex_pairs * 2))

                # Generate salt_size
                # salt_size should be a non-negative integer.
                # os.urandom expects an int, and 0 is a valid size (returns b'').
                # A reasonable upper bound like 128 bytes should prevent excessive memory usage.
                salt_size = fdp.ConsumeIntInRange(0, 128)

                # Call the function under test (solve_a)
                out_a = solve_a(hex_str, salt_size)

                # Call solve_b with identical arguments as required by the template.
                # Note: Since task_func uses os.urandom internally, calling it twice with the same
                # arguments will produce different salt values (unless salt_size is 0),
                # leading to different hash results. Thus, out_a will generally not equal out_b.
                # This part of the template is primarily for differential fuzzing where solve_a and
                # solve_b are different implementations of the same logic that should yield identical results.
                # For this specific problem, we are merely fulfilling the call requirement.
                out_b = solve_b(hex_str, salt_size)
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
