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


import math
from sympy import isprime


def _solve_a_impl(input_list):
    """
    Filter the prime numbers from the specified list, sort the prime numbers 
    ascending based on their radian value converted to degrees, and return the sorted list.
    
    The function uses the isprime function from the sympy library to determine prime numbers 
    and the degrees function from the math library to sort the numbers based on their degree value.

    Parameters:
    input_list (list[int]): A list of integers to be filtered and sorted.

    Returns:
    list[int]: A sorted list of prime numbers based on their degree value.

    Requirements:
    - math
    - sympy

    Examples:
    >>> _solve_a_impl([4, 5, 2, 7, 89, 90])
    [2, 5, 7, 89]
    
    >>> _solve_a_impl([101, 102, 103, 104])
    [101, 103]
    """
    primes = [i for i in input_list if isprime(i)]
    sorted_primes = sorted(primes, key=lambda x: (math.degrees(x), x))
    return sorted_primes

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
       
            list_length = fdp.ConsumeIntInRange(0, 10) # List length can be 0 or small
            input_list = []
            for _ in range(list_length):
                # Integers are expected. The problem statement and examples use positive integers.
                # isprime and math.degrees handle these.
                # Limiting the range to avoid excessively large numbers for isprime performance.
                input_list.append(fdp.ConsumeIntInRange(1, 200)) 

            out_a = solve_a(input_list)
            out_b = solve_b(input_list)
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
