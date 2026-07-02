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


import collections
from queue import PriorityQueue
import random

# Constants
LETTERS = ['a', 'b', 'c', 'd', 'e']

def _solve_a_impl(string_length=100):
    """
    Create a random string of a given length from a predefined list of letters and count the frequency 
    of each letter, returning an ordered dictionary sorted by frequency in descending order.

    Parameters:
    - string_length (int, optional): The length of the random string to be generated. Default is 100.

    Returns:
    - collections.OrderedDict: An ordered dictionary where keys are letters and values are 
      their frequencies in the generated string, sorted in descending order of frequency.

    Requirements:
    - collections
    - queue.PriorityQueue
    - random

    Example:
    >>> random.seed(0)
    >>> freq = _solve_a_impl(50)
    >>> freq  # Example output: OrderedDict([('e', 15), ('a', 12), ('b', 10), ('d', 8), ('c', 5)])
    OrderedDict(...)
    """

    string = ''.join([LETTERS[random.randint(0, len(LETTERS)-1)] for _ in range(string_length)])

    freq = collections.Counter(string)

    pq = PriorityQueue()
    for letter, count in freq.items():
        pq.put((-count, letter))

    sorted_freq = collections.OrderedDict()
    while not pq.empty():
        count, letter = pq.get()
        sorted_freq[letter] = -count

    return sorted_freq

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
        string_length_val = fdp.ConsumeIntInRange(1, 500) # String length should be positive, and 500 is a reasonable upper bound for fuzzing performance.

        random.seed(42)
        out_a = solve_a(string_length_val)
        random.seed(42)
        out_b = solve_b(string_length_val)
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
