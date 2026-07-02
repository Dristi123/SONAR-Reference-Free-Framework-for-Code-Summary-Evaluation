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


import numpy as np
from itertools import product
import string


def _solve_a_impl(length, seed=None, alphabets=list(string.ascii_lowercase)):
    """
    Generate a list of 10 randomly picked strings from all possible strings of a given
    length from the provided series of characters, using a specific seed for
    reproducibility.

    Parameters:
    length (int): The length of the strings to generate.
    seed (int): The seed for the random number generator. Default is None.
    alphabets (list, optional): The series of characters to generate the strings from. 
                Default is lowercase English alphabets.

    Returns:
    list: A list of generated strings.

    Requirements:
    - numpy
    - itertools.product
    - string

    Example:
    >>> _solve_a_impl(2, 123)
    ['tq', 'ob', 'os', 'mk', 'du', 'ar', 'wx', 'ec', 'et', 'vx']

    >>> _solve_a_impl(2, 123, alphabets=['x', 'y', 'z'])
    ['xz', 'xz', 'zx', 'xy', 'yx', 'zx', 'xy', 'xx', 'xy', 'xx']
    """
    np.random.seed(seed)
    all_combinations = [''.join(p) for p in product(alphabets, repeat=length)]
    return np.random.choice(all_combinations, size=10).tolist()

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
        length_val = fdp.ConsumeIntInRange(1, 4)

        use_custom_seed = fdp.ConsumeBool()
        if use_custom_seed:
            seed_val = fdp.ConsumeIntInRange(0, 2**31 - 1)
        else:
            seed_val = None

        use_custom_alphabets = fdp.ConsumeBool()
        if use_custom_alphabets:
            num_chars = fdp.ConsumeIntInRange(1, 10)
            alphabets_val = []
            for _ in range(num_chars):
                alphabets_val.append(''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10))))
        else:
            alphabets_val = None

        # The task_func uses np.random.seed(seed) internally.
        # Therefore, simply passing the same 'seed_val' to both solve_a and solve_b
        # ensures identical random sequences within their execution.
        # No need for external _fuzz_np.random.seed calls before solve_a/b.
        out_a = solve_a(length_val, seed=seed_val, alphabets=alphabets_val)
        out_b = solve_b(length_val, seed=seed_val, alphabets=alphabets_val)
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
