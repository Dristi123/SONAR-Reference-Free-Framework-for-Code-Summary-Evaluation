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


import itertools
import json


def _solve_a_impl(json_list, r):
    """
    Generate all possible combinations of r elements from a given number list taken from JSON string input.
    
    Parameters:
    json_list (str): JSON string containing the number list.
    r (int): The number of elements in each combination.

    Returns:
    list: A list of tuples, each tuple representing a combination.

    Note:
    - The datetime to be extracted is located in the 'number_list' key in the JSON data.

    Raises:
    - Raise an Exception if the json_list is an invalid JSON, empty, or does not have 'number_list' key.
    
    Requirements:
    - itertools
    - json
    
    Example:
    >>> combinations = _solve_a_impl('{"number_list": [1, 2, 3, 4, 5]}', 3)
    >>> print(combinations)
    [(1, 2, 3), (1, 2, 4), (1, 2, 5), (1, 3, 4), (1, 3, 5), (1, 4, 5), (2, 3, 4), (2, 3, 5), (2, 4, 5), (3, 4, 5)]
    """
    try:
        # Convert JSON string to Python dictionary
        data = json.loads(json_list)

        # Extract number_list from dictionary
        number_list = data['number_list']
        return list(itertools.combinations(number_list, r))
    except Exception as e:
        raise e

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
        # Determine a potential length for the number_list. This length is used to constrain 'r'.
                # For valid JSON cases, the actual list length will match this.
                # Minimum list length is 1 for valid inputs per example and typical use of combinations.
                potential_list_len = fdp.ConsumeIntInRange(1, 10) 

                # 'r' must be between 0 and the length of the list (inclusive)
                r_arg = fdp.ConsumeIntInRange(0, potential_list_len)

                # Generate json_list_arg based on different scenarios to cover described error conditions
                scenario = fdp.ConsumeIntInRange(0, 3) # 0: happy path, 1: invalid JSON, 2: no 'number_list' key, 3: empty string

                if scenario == 0: # Happy path: valid JSON with 'number_list'
                    number_list_elements = []
                    for _ in range(potential_list_len): # Use potential_list_len for actual list creation
                        number_list_elements.append(fdp.ConsumeIntInRange(-100, 100)) # Numbers in the list
                    json_data = {"number_list": number_list_elements}
                    json_list_arg = json.dumps(json_data)
                elif scenario == 1: # Invalid JSON string
                    json_list_arg = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))
                    # This generates a random string which is highly likely to be invalid JSON
                elif scenario == 2: # Valid JSON, but without the 'number_list' key
                    other_list_elements = []
                    other_list_len = fdp.ConsumeIntInRange(0, 10) # Length for a dummy list under a different key
                    for _ in range(other_list_len):
                        other_list_elements.append(fdp.ConsumeIntInRange(-100, 100))
                    json_data = {"another_key": other_list_elements}
                    json_list_arg = json.dumps(json_data)
                else: # scenario == 3: Empty string
                    json_list_arg = ""

                out_a = solve_a(json_list_arg, r_arg)
                out_b = solve_b(json_list_arg, r_arg)
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
