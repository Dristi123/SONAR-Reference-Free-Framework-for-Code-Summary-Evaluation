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
import heapq

# Constants
LETTERS = list('abcdefghijklmnopqrstuvwxyz')

def _solve_a_impl(my_dict):
    """
    Create a dictionary in which the keys are letters and the values are random integers.
    Find the 3 most common letters in the dictionary.

    Parameters:
    - my_dict (dict): The dictionary to process.

    Returns:
    - most_common_letters (list): The 3 most common letters.

    Requirements:
    - collections
    - heapq

    Example:
    >>> random.seed(43)
    >>> my_dict = {letter: random.randint(1, 100) for letter in LETTERS}
    >>> most_common_letters = _solve_a_impl(my_dict)
    >>> print(most_common_letters)
    ['d', 'v', 'c']
    """
    letter_counter = Counter(my_dict)
    most_common_letters = heapq.nlargest(3, letter_counter, key=letter_counter.get)

    return most_common_letters

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
        # Determine the number of key-value pairs for my_dict.
                # The example uses all LETTERS (26), so let's allow up to that many,
                # but also allow fewer to test edge cases.
                num_pairs = fdp.ConsumeIntInRange(1, len(LETTERS))

                # Create a mutable list of available letters to ensure unique keys
                available_letters = list(LETTERS)
                my_dict = {}

                for _ in range(num_pairs):
                    # Pick a unique letter for the key
                    # Ensure there are still letters available to pick from
                    if not available_letters:
                        break # Should not happen if num_pairs <= len(LETTERS)
                    chosen_letter_idx = fdp.ConsumeIntInRange(0, len(available_letters) - 1)
                    key = available_letters.pop(chosen_letter_idx)

                    # Consume an integer for the value.
                    # The example uses random.randint(1, 100).
                    value = fdp.ConsumeIntInRange(1, 100)
                    my_dict[key] = value

                out_a = solve_a(my_dict)
                out_b = solve_b(my_dict)
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
