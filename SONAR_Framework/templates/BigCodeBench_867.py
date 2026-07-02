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


import re
import string


def _solve_a_impl(text1, text2):
    """
    This function takes two strings, removes any ASCII punctuation using regular expressions, 
    and returns the cleaned strings as a tuple. It targets punctuation characters defined in 
    `string.punctuation`, which includes the following characters:
    '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'

    Note: This function may not remove non-ASCII or uncommon punctuation symbols.

    Parameters:
    text1, text2 (str): The original texts containing punctuation.

    Returns:
    tuple: A tuple containing the cleaned texts (text1, text2) with punctuation removed.

    Requirements:
    - re
    - string

    Example:
    >>> cleaned_text1, cleaned_text2 = _solve_a_impl("Hello, world!", "How's it going?")
    >>> print(cleaned_text1, cleaned_text2)
    Hello world Hows it going

    >>> cleaned_text1, cleaned_text2 = _solve_a_impl("test (with parenthesis []!!)", "And, other; stuff ^_`")
    >>> print(cleaned_text1, cleaned_text2)
    test with parenthesis  And other stuff 
    """
    # Constants
    PUNCTUATION = string.punctuation

    cleaned_texts = []

    # Remove punctuation from each text string
    for text in [text1, text2]:
        cleaned_text = re.sub('['+re.escape(PUNCTUATION)+']', '', text)
        cleaned_texts.append(cleaned_text)

    return tuple(cleaned_texts)

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
        char_pool = list('abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ') + list('!"#$%&\'()*+,-./:;<=>?@[]^_`{|}~')
        text1 = ''.join(fdp.PickValueInList(char_pool) for _ in range(fdp.ConsumeIntInRange(1, 30)))
        text2 = ''.join(fdp.PickValueInList(char_pool) for _ in range(fdp.ConsumeIntInRange(1, 30)))
        out_a = solve_a(text1, text2)
        out_b = solve_b(text1, text2)
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
