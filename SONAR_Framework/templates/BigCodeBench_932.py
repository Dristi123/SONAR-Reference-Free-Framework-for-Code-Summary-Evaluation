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
import re

def _solve_a_impl(word: str) -> list:
    """
    Finds the most common two-letter combination in a given, cleaned word (lowercased and alphabetic characters only) 
    and returns its frequency. The search is case-insensitive and ignores non-alphabetic characters.
    
    Requirements:
    - collections.Counter
    - re
    
    Parameters:
    - word (str): The input string containing the word to analyze. The word should have a length of at least 2 to form pairs.
    
    Returns:
    - list: A list containing a single tuple. The tuple consists of the most frequent two-letter combination (str) 
      and its frequency (int). Returns an empty list if the word has fewer than 2 letters, or after cleaning, 
      the word has fewer than 2 alphabetic characters.
    
    Examples:
    >>> _solve_a_impl("aaBBcc")
    [('aa', 1)]
    >>> _solve_a_impl("abc!abc")
    [('ab', 2)]
    >>> _solve_a_impl("a")
    []
    >>> _solve_a_impl("abcd")
    [('ab', 1)]
    >>> _solve_a_impl("a1b2c3")
    [('ab', 1)]
    """
    # Clean the word: lowercase and keep alphabetic characters only
    clean_word = re.sub('[^a-z]', '', word.lower())
    
    if len(clean_word) < 2:
        return []
    
    pairs = [clean_word[i:i+2] for i in range(len(clean_word) - 1)]
    pair_counter = Counter(pairs)
    most_common = pair_counter.most_common(1)
    
    # This check ensures we return the result directly from most_common without additional filtering
    return most_common

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
        word_length = fdp.ConsumeIntInRange(1, 100)
        word = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))
        out_a = solve_a(word)
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
