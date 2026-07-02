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


import pandas as pd
from collections import Counter

def _solve_a_impl(d):
    """
    Count the occurrence of values with the keys "x," "y" and "z" from a list of dictionaries "d."

    Parameters:
    d (list): A list of dictionaries.

    Returns:
    dict: A dictionary with keys as 'x', 'y', and 'z' and values as Counter objects.

    Requirements:
    - pandas
    - collections.Counter

    Example:
    >>> data = [{'x': 1, 'y': 10, 'z': 5}, {'x': 3, 'y': 15, 'z': 5}, {'x': 2, 'y': 1, 'z': 7}]
    >>> print(_solve_a_impl(data))
    {'x': Counter({1: 1, 3: 1, 2: 1}), 'y': Counter({10: 1, 15: 1, 1: 1}), 'z': Counter({5: 2, 7: 1})}
    >>> data = [{'x': 2, 'y': 10}, {'y': 15, 'z': 5}, {'x': 2, 'z': 7}]
    >>> print(_solve_a_impl(data))
    {'x': Counter({2.0: 2}), 'y': Counter({10.0: 1, 15.0: 1}), 'z': Counter({5.0: 1, 7.0: 1})}
    """
    df = pd.DataFrame(d)
    counts = {}

    for key in ['x', 'y', 'z']:
        if key in df.columns:
            counts[key] = Counter(df[key].dropna().tolist())
        else:
            counts[key] = Counter()

    return counts

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
        list_len = fdp.ConsumeIntInRange(0, 10) # Generate a list with 0 to 10 dictionaries
        d = []
        for _ in range(list_len):
            current_dict = {}
            # Decide for each key ('x', 'y', 'z') if it should be present in the dictionary
            # and what type of value it should have (integer or float).

            # Key 'x'
            if fdp.ConsumeBool(): # Include key 'x'
                if fdp.ConsumeBool(): # Integer value for 'x'
                    current_dict['x'] = fdp.ConsumeIntInRange(-10000, 10000)
                else: # Float value for 'x'
                    current_dict['x'] = fdp.ConsumeIntInRange(-10000, 10000) / 100.0

            # Key 'y'
            if fdp.ConsumeBool(): # Include key 'y'
                if fdp.ConsumeBool(): # Integer value for 'y'
                    current_dict['y'] = fdp.ConsumeIntInRange(-10000, 10000)
                else: # Float value for 'y'
                    current_dict['y'] = fdp.ConsumeIntInRange(-10000, 10000) / 100.0

            # Key 'z'
            if fdp.ConsumeBool(): # Include key 'z'
                if fdp.ConsumeBool(): # Integer value for 'z'
                    current_dict['z'] = fdp.ConsumeIntInRange(-10000, 10000)
                else: # Float value for 'z'
                    current_dict['z'] = fdp.ConsumeIntInRange(-10000, 10000) / 100.0

            d.append(current_dict)

        out_a = solve_a(d)
        out_b = solve_b(d)
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
