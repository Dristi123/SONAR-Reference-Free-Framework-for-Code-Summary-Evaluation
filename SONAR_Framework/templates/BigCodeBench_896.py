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
import random
import itertools

def _solve_a_impl(length, count, seed=0):
    """
    Generate a number of random strings with a specified length from a fixed set of letters ('a', 'b', 'c', 'd', 'e'),
    and analyze the frequency of each letter in the generated strings.
    
    Parameters:
    - length (int): The length of each string to be generated. Should be a non-negative integer.
    - count (int): The number of random strings to generate. Should be a non-negative integer.
    - seed (int, optional): A seed for the random number generator to ensure reproducibility.
    
    Requirements:
    - collections.Counter
    - random
    - itertools
    
    Returns:
    - Counter: A collections.Counter object containing the frequency of each letter in the generated strings.
    
    Example:
    >>> _solve_a_impl(5, 2, seed=1)
    Counter({'a': 3, 'd': 3, 'c': 2, 'e': 1, 'b': 1})
    >>> _solve_a_impl(0, 100, seed=2)
    Counter()
    """
    random.seed(seed)
    strings = [''.join(random.choices(['a', 'b', 'c', 'd', 'e'], k=length)) for _ in range(count)]
    letter_frequency = Counter(itertools.chain(*strings))
    
    return letter_frequency

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
     
            length = fdp.ConsumeIntInRange(0, 100)
            count = fdp.ConsumeIntInRange(0, 100)
            seed = fdp.ConsumeInt(8) # Using 8 bytes for a broad range of integer seeds

            out_a = solve_a(length, count, seed)
            out_b = solve_b(length, count, seed)
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
