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

def _solve_a_impl(max_length, n_samples, seed=None):
    """Generate a list containing random strings of lowercase letters. Each string's length varies from 1 to `max_length`.
    An optional seed can be set for the random number generator for reproducible results.

    Note:
    The function utilizes the `random.choices` function to generate random strings and combines them into a list.

    Parameters:
    max_length (int): The maximum length of the strings.
    n_samples (int): The number of strings to return.
    seed (int, optional): A seed for the random number generator. If None, the generator is initialized without a seed.

    Returns:
    list: A list containing random strings. Each string is a random combination of lowercase letters, 
    and their lengths will vary from 1 to `max_length`.

    Requirements:
    - random
    - string

    Raises:
    ValueError: If max_length is smaller than 1.

    Example:
    >>> _solve_a_impl(3, 12, seed=12)
    ['gn', 'da', 'mq', 'rp', 'aqz', 'ex', 'o', 'b', 'vru', 'a', 'v', 'ncz']
    >>> _solve_a_impl(5, n_samples=8, seed=1)
    ['ou', 'g', 'tmjf', 'avlt', 's', 'sfy', 'aao', 'rzsn']

    """
    # Handling negative input
    if max_length < 1:
        raise ValueError("max_length must be larger than or equal to 1.")

    # Constants within the function for better encapsulation
    LETTERS = string.ascii_lowercase

    # Setting the seed for the random number generator for reproducibility
    if seed is not None:
        random.seed(seed)

    all_combinations = []

    for i in range(n_samples):
        random_length = random.randint(1, max_length)
        combination = ''.join(random.choices(LETTERS, k=random_length))
        all_combinations.append(combination)


    # Simplifying the reduction using native functionality
    return all_combinations

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
       
            max_length = fdp.ConsumeIntInRange(1, 1000) # max_length must be >= 1, choose a reasonable upper bound
            n_samples = fdp.ConsumeIntInRange(0, 200) # n_samples can be 0, choose a reasonable upper bound

            # Determine if 'seed' should be None or an integer
            use_seed_param = fdp.ConsumeBool()
            seed = None
            if use_seed_param:
                seed = fdp.ConsumeIntInRange(0, 2**32 - 1) # A typical range for random seeds

            # Set a fixed seed for the global random state before calling solve_a
            # This is for the fuzzer's own determinism and consistency between solve_a and solve_b calls.
            # The task_func will then use its own 'seed' parameter if provided, overriding this global seed.
            random.seed(42)
            out_a = solve_a(max_length, n_samples, seed)

            # Set the fixed seed again before calling solve_b to ensure identical random sequences
            random.seed(42)
            out_b = solve_b(max_length, n_samples, seed)
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
