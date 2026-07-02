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


import random
import string

POSSIBLE_LETTERS = ['a', 'b', 'c']
def _solve_a_impl(word):
    """
    Generates a list of random pairs of adjacent letters from the given word. The number of such pairs will be equal to the length of the constant POSSIBLE_LETTERS.
    
    Parameters:
    word (str): The input string. Must only contain letters.
    
    Returns:
    list: A list of random pairs of adjacent letters from the word. If the word has fewer than 2 letters, returns a list of empty strings based on POSSIBLE_LETTERS length.
    
    Requirements:
    - random
    - string
    
    Raises:
    ValueError: If the input contains non-letter characters.
    
    Examples:
    >>> random.seed(0)
    >>> _solve_a_impl('abcdef')
    ['de', 'de', 'ab']
    >>> _solve_a_impl('xyz')
    ['yz', 'yz', 'yz']
    """
    if not all(char in string.ascii_letters for char in word):
        raise ValueError("Input must only contain letters.")
    
    if len(word) < 2:
        return ['' for _ in range(len(POSSIBLE_LETTERS))]
    
    pairs = [''.join(x) for x in zip(word, word[1:])]
    random_pairs = [random.choice(pairs) for _ in range(len(POSSIBLE_LETTERS))]

    return random_pairs

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
        word = ''.join(fdp.PickValueInList(list(string.ascii_letters)) for _ in range(fdp.ConsumeIntInRange(1, 100)))

        random.seed(42)
        out_a = solve_a(word)
        random.seed(42)
        out_b = solve_b(word)
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
