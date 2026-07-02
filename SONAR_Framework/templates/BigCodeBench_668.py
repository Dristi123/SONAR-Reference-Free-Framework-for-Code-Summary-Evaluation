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
import math

def _solve_a_impl(x):
    """
    Find the sub-sequence of a dictionary, x, with the minimum total length, where the keys are letters and the values are their lengths.

    Parameters:
    - x (dict): The dictionary of letter lengths.

    Returns:
    - list: The subsequence with the minimum total length.

    Requirements:
    - itertools
    - math

    Example:
    >>> _solve_a_impl({'a': 1, 'b': 2, 'c': 3})
    ['a']
    >>> _solve_a_impl({'a': 1, 'b': -2, 'c': -5, 'd': 4})
    ['b', 'c']
    """
    min_length = math.inf
    min_subseq = []

    for r in range(1, len(x) + 1):
        for subseq in itertools.combinations(x.items(), r):
            length = sum(length for letter, length in subseq)
            if length < min_length:
                min_length = length
                min_subseq = [letter for letter, length in subseq]

    return min_subseq

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
        # Generate the dictionary 'x'
                x = {}
                # Determine the number of key-value pairs for the dictionary
                # Use fdp.ConsumeIntInRange for dictionary size, typically 1 to 10 for reasonable fuzzing depth.
                num_elements = fdp.ConsumeIntInRange(1, 10) 

                for _ in range(num_elements):
                    # Generate a key: a single character string.
                    # The description states "keys are letters", implying single characters.
                    # Use ConsumeUnicodeNoSurrogates(1) for a single character key.
                    key = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))

                    # Generate a value: an integer representing length.
                    # Examples show both positive and negative integer values are possible.
                    # Use a reasonable range for integers.
                    value = fdp.ConsumeIntInRange(-1000, 1000)

                    # Add to the dictionary, handling potential duplicate keys by overwriting
                    # (which is standard dictionary behavior and fine for fuzzing).
                    x[key] = value

                out_a = solve_a(x)
                out_b = solve_b(x)
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
