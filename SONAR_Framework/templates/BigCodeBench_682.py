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


from collections import Counter
import math

def _solve_a_impl(nested_dict):
    """
    Aggregate the values of the same keys from a nested dictionary and remove the "ele" key. For each remaining key take the sine.
    
    Parameters:
    - nested_dict (dict): The nested dictionary. Default is NESTED_DICT constant.
    
    Returns:
    - dict: A dictionary with aggregated values.

    Requirements:
    - math
    - collections

    Example:
    >>> _solve_a_impl({
    ...     'dict1': {'ale': 1, 'ele': 2, 'ile': 3},
    ...     'dict2': {'ele': 4, 'ole': 5, 'ule': 6},
    ...     'dict3': {'ile': 7, 'ale': 8, 'ele': 9}
    ... })
    {'ale': 0.4121184852417566, 'ile': -0.5440211108893698, 'ole': -0.9589242746631385, 'ule': -0.27941549819892586}
    """
    counter = Counter()
    for sub_dict in nested_dict.values():
        counter.update(sub_dict)

    counter.pop('ele', None)

    return {k: math.sin(v) for k,v in counter.items()}

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
        nested_dict = {}
        # Determine the number of sub-dictionaries in the main dictionary
        num_sub_dicts = fdp.ConsumeIntInRange(1, 5)

        for i in range(num_sub_dicts):
            # Generate a unique key for the sub-dictionary
            outer_key = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))

            inner_dict = {}
            # Determine the number of key-value pairs in the current sub-dictionary
            num_inner_pairs = fdp.ConsumeIntInRange(1, 5)

            for j in range(num_inner_pairs):
                # Generate a key for the inner dictionary
                # The example uses short string keys like 'ale', 'ele', 'ile', 'ole', 'ule'.
                # We allow for slightly longer strings as there's no explicit restriction.
                inner_key = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))

                # Generate a float value for the inner dictionary.
                # The function uses math.sin, so float values are appropriate.
                # Values can range from -100 to 100.
                inner_value = fdp.ConsumeIntInRange(-10000, 10000) / 100.0

                inner_dict[inner_key] = inner_value

            nested_dict[outer_key] = inner_dict

        out_a = solve_a(nested_dict)
        out_b = solve_b(nested_dict)
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
