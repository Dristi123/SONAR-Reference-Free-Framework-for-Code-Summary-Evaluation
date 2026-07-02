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


import re
import random
import string

def _solve_a_impl(n, pattern, seed=None):
    """
    Generate a random string of length 'n' and find all non-overlapping matches
    of the regex 'pattern'.

    The function generates a random string of ASCII Letters and Digits using 
    the random module. By providing a seed the results are reproducable.
    Non overlapping matches of the provided pattern are then found using the re
    module.
    
    Parameters:
    n (int): The length of the random string to be generated.
    pattern (str): The regex pattern to search for in the random string.
    seed (int, optional): A seed parameter for the random number generator for reproducible results. Defaults to None.

    Returns:
    list: A list of all non-overlapping matches of the regex pattern in the generated string.

    Requirements:
    - re
    - random
    - string

    Example:
    >>> _solve_a_impl(100, r'[A-Za-z]{5}', seed=12345)
    ['mrKBk', 'BqJOl', 'NJlwV', 'UfHVA', 'LGkjn', 'vubDv', 'GSVAa', 'kXLls', 'RKlVy', 'vZcoh', 'FnVZW', 'JQlqL']

    >>> _solve_a_impl(1000, r'[1-9]{2}', seed=1)
    ['51', '84', '16', '79', '16', '28', '63', '82', '94', '18', '68', '42', '95', '33', '64', '38', '69', '56', '32', '16', '18', '19', '27']
     """
    if seed is not None:
        random.seed(seed)
    rand_str = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(n))
    matches = re.findall(pattern, rand_str)
    return matches

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
        # Generate inputs for n
                n_val = fdp.ConsumeIntInRange(1, 2000) # 'n' represents length, so a positive integer range

                # Generate inputs for pattern
                pattern_len = fdp.ConsumeIntInRange(1, 50) # A reasonable length for a regex pattern
                pattern_val = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))

                # Generate inputs for seed (optional)
                # Decide whether to pass a seed or None
                use_seed = fdp.ConsumeBool()
                seed_arg_val = None
                if use_seed:
                    seed_arg_val = fdp.ConsumeIntInRange(0, 100000) # A positive integer range for seed

                # Set a fixed random seed for the global random module before calling solve_a.
                # This is crucial for reproducibility, especially when task_func's 'seed' argument is None,
                # ensuring that the global random state is identical for both calls.
                random.seed(42)
                out_a = solve_a(n_val, pattern_val, seed=seed_arg_val)

                # Set the same fixed random seed for the global random module before calling solve_b.
                random.seed(42)
                out_b = solve_b(n_val, pattern_val, seed=seed_arg_val)
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
