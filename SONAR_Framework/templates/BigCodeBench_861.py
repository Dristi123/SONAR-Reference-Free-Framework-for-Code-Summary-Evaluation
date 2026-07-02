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
from random import choice, seed

# Constants
POSSIBLE_ITEMS = ['apple', 'banana', 'cherry', 'date', 'elderberry']

def _solve_a_impl(list_of_lists):
    """
    Create a "shopping cart" (Counter object) for each list in list_of_lists. 
    The items in the cart are randomly selected from a predefined list of possible items (POSSIBLE_ITEMS).
    The frequency of each item in the cart corresponds to the length of the list.

    Parameters:
    - list_of_lists (list): A list of lists, each representing a 'basket'.

    Returns:
    - baskets (list): A list of Counters, each representing a 'shopping cart'.

    Requirements:
    - collections
    - random

    Example:
    >>> baskets = _solve_a_impl([[1, 2, 3], [4, 5]])
    >>> all(isinstance(basket, Counter) for basket in baskets) # Illustrative, actual items will vary due to randomness
    True
    >>> sum(len(basket) for basket in baskets) # The sum of lengths of all baskets; illustrative example
    3
    """
    seed(42)  # Set the seed for reproducibility
    baskets = []
    for list_ in list_of_lists:
        basket = Counter()
        for _ in list_:
            basket[choice(POSSIBLE_ITEMS)] += 1
        baskets.append(basket)

    return baskets

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
        outer_list_len = fdp.ConsumeIntInRange(0, 5) # A list of 0 to 5 baskets

        for _ in range(outer_list_len):
            inner_list = []
            inner_list_len = fdp.ConsumeIntInRange(0, 10) # Each basket can have 0 to 10 items
            for _ in range(inner_list_len):
                # The actual values of elements in the inner lists do not affect the function's logic,
                # as only the length of the inner list is used to determine item frequency.
                # So, we can consume a simple integer as a placeholder.
                inner_list.append(fdp.ConsumeInt(4)) 
            list_of_lists.append(inner_list)

        # The task_func itself sets random.seed(42) internally.
        # However, for consistency with the fuzzer's general requirements for functions
        # that use random, we set the seed here as well.
        # This ensures that if the internal seeding of task_func were ever removed,
        # the fuzzer would still provide consistent random states for out_a and out_b.
        random.seed(42)
        out_a = solve_a(list_of_lists)
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
