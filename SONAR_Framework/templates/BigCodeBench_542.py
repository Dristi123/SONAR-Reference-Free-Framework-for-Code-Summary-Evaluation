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


import hashlib
import random
import struct

KEYS = ['470FC614', '4A0FC614', '4B9FC614', '4C8FC614', '4D7FC614']


def _solve_a_impl(hex_keys=KEYS, seed=42):
    """
    Given a list of hexadecimal string keys, this function selects one at random,
    converts it into a floating-point number, and then computes its MD5 hash. An optional
    seed parameter allows for deterministic random choices for testing purposes.

    Parameters:
    hex_keys (list of str): A list of hexadecimal strings to choose from.
    seed (int, optional): A seed for the random number generator to ensure deterministic behavior.

    Returns:
    str: The MD5 hash of the floating-point number derived from the randomly selected hexadecimal string.

    Raises:
    ValueError: If contains invalid hexadecimal strings.

    Requirements:
    - struct
    - hashlib
    - random

    Example:
    >>> _solve_a_impl(['1a2b3c4d', '5e6f7g8h'])
    '426614caa490f2c185aebf58f1d4adac'
    """

    random.seed(seed)
    hex_key = random.choice(hex_keys)

    try:
        float_num = struct.unpack('!f', bytes.fromhex(hex_key))[0]
    except ValueError as e:
        raise ValueError("Invalid hexadecimal string in hex_keys.") from e

    hashed_float = hashlib.md5(str(float_num).encode()).hexdigest()
    return hashed_float

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
        # Generate the seed for the task_func
            seed_arg = fdp.ConsumeIntInRange(0, 1000000)

            # Generate the list of hexadecimal keys
            # Determine the number of keys in the list (between 1 and 10)
            num_keys = fdp.ConsumeIntInRange(1, 10)
            hex_keys_list = []

            # Define the character set for hexadecimal digits
            hex_char_set = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f', 'A', 'B', 'C', 'D', 'E', 'F']

            # Generate each hex key string. A 4-byte float requires 8 hex characters.
            for _ in range(num_keys):
                hex_key_str = ''.join(fdp.PickValueInList(hex_char_set) for _ in range(8))
                hex_keys_list.append(hex_key_str)

            # Call the function under test (task_func) for the 'out_a' comparison
            # Set random seed immediately before the call to ensure deterministic behavior for the harness.
            random.seed(42)
            out_a = solve_a(hex_keys=hex_keys_list, seed=seed_arg)

            # Call the function under test (task_func) for the 'out_b' comparison
            # Set random seed immediately before the call again to ensure identical random sequences for both calls.
            random.seed(42)
            out_b = solve_b(hex_keys=hex_keys_list, seed=seed_arg)
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
