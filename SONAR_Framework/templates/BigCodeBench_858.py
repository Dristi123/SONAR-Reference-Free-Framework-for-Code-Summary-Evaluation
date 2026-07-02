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


import string
import random
from collections import Counter


def _solve_a_impl(n, seed=None):
    """
    Generate a number of random lowercase letters and count their occurrences.

    This function takes an integer input to determine how many random letters 
    to generate and an optional seed for consistent randomness. It then creates 
    a list of these letters, chosen from the English lowercase alphabet, and 
    counts each letter's occurrences. The result is returned as a Counter 
    object (from the collections module) which behaves like a dictionary where 
    the keys are the letters, and the values are their counts.

    Parameters:
    n (int): The number of random letters to generate.
    seed (int, optional): A seed for the random number generator for consistent
                         results. Defaults to None.

    Returns:
    Counter: A collections.Counter object with the count of each letter.

    Requirements:
    - collections
    - string
    - random

    Example:
    >>> letter_counts = _solve_a_impl(1000, seed=123)
    >>> print(letter_counts)
    Counter({'v': 48, 'b': 47, 'n': 46, 'r': 46, 'k': 46, 'z': 46, 'c': 44, 'e': 43, 'q': 43, 'l': 43, 'y': 42, 'm': 42, 'a': 42, 'u': 42, 'd': 36, 'o': 34, 'j': 34, 'g': 34, 'f': 33, 'h': 33, 'p': 32, 'w': 30, 'x': 30, 'i': 29, 't': 28, 's': 27})
    >>> _solve_a_impl(10, seed=12)
    Counter({'v': 2, 'l': 2, 'p': 1, 'i': 1, 'q': 1, 'e': 1, 'm': 1, 'a': 1})

    Note: 
    The function internally uses a list to store the randomly generated 
    letters before counting them. The randomness of letter selection can be 
    consistent by providing a seed.
    """
    LETTERS = string.ascii_lowercase
    if seed is not None:
        random.seed(seed)
    letters = [random.choice(LETTERS) for _ in range(n)]
    letter_counts = Counter(letters)
    return letter_counts

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
        n_val = fdp.ConsumeIntInRange(1, 1000)
        use_seed = fdp.ConsumeBool()
        seed_val = None
        if use_seed:
            # Use ConsumeInt(4) for a 32-bit integer range for the seed
            seed_val = fdp.ConsumeInt(4) 

        # Ensure a consistent random state for both calls, as task_func uses random internally.
        # The internal random.seed(seed_val) in task_func will override this if seed_val is not None,
        # but this ensures consistency when seed_val IS None.
        random.seed(42) 
        out_a = solve_a(n_val, seed=seed_val)

        random.seed(42) 
        out_b = solve_b(n_val, seed=seed_val)
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
