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
import itertools
import random


# Constants
ALPHABET = 'abcdefghijklmnopqrstuvwxyz'

def _solve_a_impl(list_of_lists, seed=0):
    """
    Count the frequency of each letter in a list of lists. If a list is empty, 
    fill it with a random sample from the alphabet, and then count the letters.
    
    Parameters:
    list_of_lists (list): The list of lists.
    seed (int): The seed for the random number generator. Defaults to 0.
    
    Returns:
    Counter: A Counter object with the frequency of each letter.
    
    Requirements:
    - collections.Counter
    - itertools
    - random.sample
    
    Example:
    >>> dict(_solve_a_impl([['a', 'b', 'c'], [], ['d', 'e', 'f']]))
    {'a': 1, 'b': 2, 'c': 1, 'd': 1, 'e': 1, 'f': 1, 'm': 1, 'y': 1, 'n': 1, 'i': 1, 'q': 1, 'p': 1, 'z': 1, 'j': 1, 't': 1}
    """
    random.seed(seed)
    flattened_list = list(itertools.chain(*list_of_lists))

    for list_item in list_of_lists:
        if list_item == []:
            flattened_list += random.sample(ALPHABET, 10)

    counter = Counter(flattened_list)
    
    return counter

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
        # Generate list_of_lists
        num_outer_lists = fdp.ConsumeIntInRange(1, 10)
        list_of_lists = []
        for _ in range(num_outer_lists):
            inner_list_len = fdp.ConsumeIntInRange(0, 10) # Inner lists can be empty
            current_inner_list = []
            for _ in range(inner_list_len):
                # Elements are single characters from ALPHABET
                char = fdp.PickValueInList(list(ALPHABET))
                current_inner_list.append(char)
            list_of_lists.append(current_inner_list)

        # Generate seed
        seed = fdp.ConsumeIntInRange(0, 1000000)

        # Call the function under test (task_func) with identical arguments
        out_a = solve_a(list_of_lists, seed)
        out_b = solve_b(list_of_lists, seed)
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
