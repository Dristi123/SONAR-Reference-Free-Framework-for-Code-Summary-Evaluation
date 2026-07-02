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
import hashlib
import time


def _solve_a_impl(data_dict: dict, seed=0) -> dict:
    """
    Process the given dictionary by performing the following operations:
    1. Add a key "a" with a value of 1.
    2. Generate a random salt of length 5 using lowercase ASCII letters.
    3. For each key-value pair in the dictionary, concatenate the value with the generated salt, 
       hash the concatenated string using SHA-256, and update the value with the hashed string.
    4. Add a 'timestamp' key with the current UNIX timestamp as its value.

    Parameters:
    data_dict (dict): The dictionary to be processed. Values should be string-convertible.
    seed (int, Optional): Seed value for the random number generator. Defaults to 0.

    Returns:
    dict: The processed dictionary with the hashed values and added keys.

    Requirements:
    - Uses the random, string, hashlib, and time libraries.

    Example:
    >>> _solve_a_impl({'key': 'value'})["key"]
    '8691a011016e0fba3c2b0b8a26e4c9c722975f1defe42f580ab55a9c97dfccf8'

    """
    random.seed(seed)
    # Constants
    SALT_LENGTH = 5
    
    # Add the key 'a' with value 1
    data_dict.update(dict(a=1))

    # Generate a random salt
    salt = ''.join(random.choice(string.ascii_lowercase) for _ in range(SALT_LENGTH))

    # Concatenate the salt with the values and hash the concatenated string
    for key in data_dict.keys():
        data_dict[key] = hashlib.sha256((str(data_dict[key]) + salt).encode()).hexdigest()

    # Timestamp the process
    data_dict['timestamp'] = time.time()

    return data_dict

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
        # Generate data_dict argument
                num_items = fdp.ConsumeIntInRange(1, 10) # Number of key-value pairs in the dictionary
                data_dict_arg = {}
                for _ in range(num_items):
                    key = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10))) # Keys are strings

                    # Values can be string-convertible, so generate a mix of types
                    value_type_choice = fdp.ConsumeIntInRange(0, 3)
                    if value_type_choice == 0:
                        value = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10))) # String value
                    elif value_type_choice == 1:
                        value = fdp.ConsumeIntInRange(-1000, 1000) # Integer value
                    elif value_type_choice == 2:
                        value = fdp.ConsumeIntInRange(-10000, 10000) / 100.0 # Float value
                    else: # value_type_choice == 3
                        value = fdp.ConsumeBool() # Boolean value

                    data_dict_arg[key] = value

                # Generate seed argument
                seed_arg = fdp.ConsumeIntInRange(0, 2**31 - 1) # Seed for random number generator

                # Call solve_a
                random.seed(42) # Set fixed seed for random module before each call
                # Pass a copy of data_dict_arg because task_func modifies the dictionary in-place
                out_a = solve_a(data_dict_arg.copy(), seed_arg)

                # Call solve_b
                random.seed(42) # Set fixed seed for random module before each call
                # Pass a fresh copy of data_dict_arg to ensure identical starting state for solve_b
                out_b = solve_b(data_dict_arg.copy(), seed_arg)
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
