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


from itertools import combinations
import math

def _solve_a_impl(x, w):
    """
    Find the continuous substring of x, which has the maximum total weight, given a dictionary where the keys are characters and the values are their weights.

    Parameters:
    - x (str): The input string.
    - w (dict): The dictionary of character weights.

    Returns:
    - max_substr (str): The continuous substring with the highest weight.

    Requirements:
    - itertools
    - math

    Example:
    >>> _solve_a_impl('c', {'a': 1, 'b': 2, 'c': 3})
    'c'
    >>> _solve_a_impl('abc', {'a': 10, 'b': -5, 'c': 3})
    'a'
    """
    max_weight = -math.inf
    max_substr = ''

    for start, end in combinations(range(len(x) + 1), 2):
        substr = x[start:end]
        weight = sum(w.get(c, 0) for c in substr)
        if weight > max_weight:
            max_weight = weight
            max_substr = substr

    return max_substr

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
      
            x_len = fdp.ConsumeIntInRange(1, 100)
            x = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))

            w = {}
            num_weights = fdp.ConsumeIntInRange(1, 26) # Number of character-weight pairs
            for _ in range(num_weights):
                char_key = fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz'))  # single char key to match chars in x
                weight_val = fdp.ConsumeIntInRange(-100, 100) # Integer weight
                w[char_key] = weight_val

            out_a = solve_a(x, w)
            out_b = solve_b(x, w)
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
