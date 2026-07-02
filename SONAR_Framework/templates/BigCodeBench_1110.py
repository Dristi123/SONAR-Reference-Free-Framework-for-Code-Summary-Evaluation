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
from operator import itemgetter
import itertools


def _solve_a_impl(word_dict):
    """
    Given a dictionary of words as keys and letters as values, count the frequency of each letter in the words.
    
    Parameters:
    word_dict (dict): The dictionary with words as keys and their letters as values.
    
    Returns:
    dict: A dictionary with letters as keys and their frequencies as values.
    
    Requirements:
    - collections.Counter
    - operator.itemgetter
    - itertools
    
    Example:
    >>> word_dict = {'apple': 'a', 'banana': 'b', 'cherry': 'c', 'date': 'd', 'elderberry': 'e', 'fig': 'f', 'grape': 'g', 'honeydew': 'h'}
    >>> counts = _solve_a_impl(word_dict)
    >>> print(counts)
    {'e': 9, 'a': 6, 'r': 6, 'p': 3, 'n': 3, 'y': 3, 'd': 3, 'l': 2, 'b': 2, 'h': 2, 'g': 2, 'c': 1, 't': 1, 'f': 1, 'i': 1, 'o': 1, 'w': 1}
    """
    letters = list(itertools.chain.from_iterable(word_dict.keys()))
    count_dict = dict(Counter(letters))
    
    sorted_dict = dict(sorted(count_dict.items(), key=itemgetter(1), reverse=True))
    
    return sorted_dict

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
        num_entries = fdp.ConsumeIntInRange(1, 10)
        word_dict = {}
        for _ in range(num_entries):
            # Generate a string for the dictionary key (word)
            key_length = fdp.ConsumeIntInRange(1, 100)
            word_key = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))

            # Generate a string for the dictionary value (letter).
            # Although the function's logic ignores values and only processes keys,
            # the description and example specify "letters as values".
            # Therefore, we generate a single character string as the value.
            value_length = 1 
            word_value = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))

            word_dict[word_key] = word_value

        out_a = solve_a(word_dict)
        out_b = solve_b(word_dict)
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
