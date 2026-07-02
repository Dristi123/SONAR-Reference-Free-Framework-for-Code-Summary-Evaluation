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
import string

# Constants
LETTERS = string.ascii_letters

def _solve_a_impl(list_of_lists):
    """
    If you have a nested list, replace each sublist with a random letter and return a count of each letter in the final list.

    Parameters:
    - list_of_lists (list): A nested list.

    Returns:
    - dict: A dictionary containing count of each letter in the list.

    Requirements:
    - collections
    - random
    - string

    Example:
    >>> random.seed(42)
    >>> _solve_a_impl([['Pizza', 'Burger'], ['Pizza', 'Coke'], ['Pasta', 'Coke']])
    {'O': 1, 'h': 1, 'b': 1}
    """
    flat_list = [random.choice(LETTERS) for _ in list_of_lists]

    return dict(Counter(flat_list))

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
        list_of_lists = []
        outer_list_length = fdp.ConsumeIntInRange(1, 10) # Number of sublists

        for _ in range(outer_list_length):
            sublist = []
            sublist_length = fdp.ConsumeIntInRange(1, 5) # Length of each sublist
            for _ in range(sublist_length):
                # The function only cares about the number of sublists, not their content.
                # However, to form a valid nested list as per the example, we populate sublists with strings.
                sublist.append(''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10))))
            list_of_lists.append(sublist)

        # Set random seed before the first call to ensure deterministic behavior for fuzzing
        random.seed(42)
        out_a = solve_a(list_of_lists)

        # Set random seed again before the second call to ensure both calls experience the same random sequence
        random.seed(42)
        out_b = solve_b(list_of_lists)
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
