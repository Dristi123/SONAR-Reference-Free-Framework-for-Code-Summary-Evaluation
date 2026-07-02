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
import json
import zlib

def _solve_a_impl(data_dict):
    """
    Serializes a dictionary to a JSON string, compresses it using zlib, and then encodes the compressed
    data with base64.

    Parameters:
    data_dict (dict): The dictionary to be compressed and encoded. The dictionary should only contain
                      data that can be serialized to JSON.

    Returns:
    str: A base64 encoded string that represents the zlib-compressed JSON string of the dictionary.

    Requirements:
    - base64
    - zlib
    - json
    
    Example:
    >>> data = {'key1': 'value1', 'key2': 'value2'}
    >>> encoded_data = _solve_a_impl(data)
    >>> print(encoded_data)
    eJyrVspOrTRUslJQKkvMKU01VNJRAIkYwUWMlGoBw5sKmw==
    """
    json_str = json.dumps(data_dict)
    compressed = zlib.compress(json_str.encode())
    return base64.b64encode(compressed).decode()

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
        # Generate the dictionary to be passed to task_func
                data_dict = {}
                # Determine the number of key-value pairs in the dictionary
                num_items = fdp.ConsumeIntInRange(0, 5) # Limit dictionary size for performance

                for _ in range(num_items):
                    # Generate key: A non-empty unicode string
                    key_length = fdp.ConsumeIntInRange(1, 20)
                    key = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))

                    # Generate value: Choose a JSON-serializable type for the value
                    value_type_choice = fdp.ConsumeIntInRange(0, 4) # 0:str, 1:int, 2:float, 3:bool, 4:None

                    if value_type_choice == 0:
                        # String value
                        value_length = fdp.ConsumeIntInRange(1, 50)
                        value = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))
                    elif value_type_choice == 1:
                        # Integer value
                        value = fdp.ConsumeIntInRange(-100000, 100000)
                    elif value_type_choice == 2:
                        # Float value
                        value = fdp.ConsumeIntInRange(-100000, 100000) / 100.0
                    elif value_type_choice == 3:
                        # Boolean value
                        value = fdp.ConsumeBool()
                    else: # value_type_choice == 4
                        # None value (JSON null)
                        value = None

                    data_dict[key] = value

                # Call the function under test with the generated dictionary
                out_a = solve_a(data_dict)
                out_b = solve_b(data_dict)
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
