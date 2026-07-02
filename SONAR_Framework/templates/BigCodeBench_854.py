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


from functools import reduce
from itertools import permutations
import math

def _solve_a_impl(numbers):
    '''
    Generate all permutations of a given list of numbers and calculate the sum 
    of the factorials of each number in each permutation.
    If an empty list is given, the function returns empty lists.

    Parameters:
    numbers (list of int): A list of integers to permute and calculate 
                           factorial sums.

    Returns:
    list of int: A list containing the sums of the factorials of each number 
                 in each permutation.
    list of list of int: A list containing all permutations of numbers.

    Raises:
    TypeError: If numbers is not a list of integers.
    ValueError: If input numbers are negative.

    Requirements:
    - functools.reduce
    - itertools.permutations
    - math.factorial

    Example:
    >>> fac, perm = _solve_a_impl([1, 2, 3])
    >>> print(fac)
    [9, 9, 9, 9, 9, 9]
    >>> print(perm)
    [(1, 2, 3), (1, 3, 2), (2, 1, 3), (2, 3, 1), (3, 1, 2), (3, 2, 1)]

    >>> fac, perm = _solve_a_impl([0, 4])
    >>> print(fac)
    [25, 25]
    >>> print(perm)
    [(0, 4), (4, 0)]
    '''

    if not isinstance(numbers, list):
        raise TypeError("numbers should be a list of integers.")
    
    if not all(isinstance(number, int) for number in numbers):
        raise TypeError("numbers should be a list of integers.")
    
    if not all(number >= 0 for number in numbers):
        raise ValueError("each number in numbers should be non negative.")

    if len(numbers) == 0:
        return [], []

    all_permutations = list(permutations(numbers))
    sums = [reduce(lambda a, b: a + b, [math.factorial(n) for n in permutation]) for permutation in all_permutations]
    return sums, all_permutations

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
    
            numbers_len = fdp.ConsumeIntInRange(0, 8) # Limit length to avoid excessive permutations
            numbers = []
            for _ in range(numbers_len):
                # Numbers must be non-negative. Keep the range small to prevent huge factorial values.
                numbers.append(fdp.ConsumeIntInRange(0, 10)) # Max 10! = 3,628,800

            out_a = solve_a(numbers)
            out_b = solve_b(numbers)
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
