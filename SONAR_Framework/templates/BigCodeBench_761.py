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


import json
import re
from collections import Counter

# Constants
REPLACE_NONE = "None"

def _solve_a_impl(json_str):
    """
    Process a JSON string by:
    1. Removing None values.
    2. Counting the frequency of each unique value.
    3. Replacing all email addresses with the placeholder "None".
    
    Parameters:
    json_str (str): The JSON string to be processed.
    
    Returns:
    dict: A dictionary containing:
        - "data": Processed JSON data.
        - "value_counts": A Counter object with the frequency of each unique value.
    
    Requirements:
    - json
    - re
    - collections.Counter
    
    Example:
    >>> json_str = '{"name": "John", "age": null, "email": "john@example.com"}'
    >>> _solve_a_impl(json_str)
    {'data': {'name': 'John', 'email': 'None'}, 'value_counts': Counter({'John': 1, 'None': 1})}
    """
    data = json.loads(json_str)
    
    # Remove None values and replace emails
    processed_data = {}
    for key, value in data.items():
        if value is None:
            continue
        if isinstance(value, str) and re.match(r"[^@]+@[^@]+\.[^@]+", value):
            value = REPLACE_NONE
        processed_data[key] = value

    # Count frequency of each unique value
    value_counts = Counter(processed_data.values())

    return {"data": processed_data, "value_counts": value_counts}

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
        data_dict = {}
        num_items = fdp.ConsumeIntInRange(1, 5) # Generate a dictionary with 1 to 5 key-value pairs

        for _ in range(num_items):
            key = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10))) # Key length 1 to 15

            # Determine the type of value to generate
            value_type_choice = fdp.PickValueInList(['null', 'string', 'email_string', 'int', 'float', 'bool'])

            if value_type_choice == 'null':
                value = None
            elif value_type_choice == 'string':
                value = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10))) # Regular string length 1 to 30
            elif value_type_choice == 'email_string':
                # Generate parts for an email-like string to test the regex
                # Ensure parts are not empty for basic email format
                prefix = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))
                domain = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))
                tld = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))
                value = f"{prefix}@{domain}.{tld}"
            elif value_type_choice == 'int':
                value = fdp.ConsumeIntInRange(-10000, 10000)
            elif value_type_choice == 'float':
                value = fdp.ConsumeIntInRange(-10000, 10000) / 100.0
            elif value_type_choice == 'bool':
                value = fdp.ConsumeBool()

            data_dict[key] = value

        # Convert the Python dictionary to a JSON string
        json_str = json.dumps(data_dict)

        out_a = solve_a(json_str)
        out_b = solve_b(json_str)
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
