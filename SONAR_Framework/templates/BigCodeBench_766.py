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
import collections


def _solve_a_impl(string, patterns=['nnn', 'aaa', 'sss', 'ddd', 'fff']):
    """
    Counts the occurrence of specific patterns in a string.
    
    Parameters:
    string (str): The input string.
    patterns (list[str], optional): List of patterns to search for. Defaults to ['nnn', 'aaa', 'sss', 'ddd', 'fff'].
    
    Returns:
    dict: A dictionary with patterns as keys and their counts as values.

    Raises:
    - TypeError: If string is not a str.
    - TypeError: If patterns is not a list of str.
    
    Requirements:
    - re
    - collections
    
    Example:
    >>> _solve_a_impl("nnnaaaasssdddeeefffggg")
    {'nnn': 1, 'aaa': 1, 'sss': 1, 'ddd': 1, 'fff': 1}
    >>> _solve_a_impl('asdfasdfasdfasdaaaaf', patterns=['a', 'asdf'])
    {'a': 8, 'asdf': 3}
    >>> _solve_a_impl('123kajhdlkfah12345k,jk123', patterns=['123', '1234'])
    {'123': 3, '1234': 1}
    """

    if not isinstance(string, str):
        raise TypeError("Input string should be of type string.")

    if not isinstance(patterns, list):
        raise TypeError("patterns should be a list of strings.")
    
    if not all(isinstance(s, str) for s in patterns):
        raise TypeError("patterns should be a list of strings.")

    

    pattern_counts = collections.defaultdict(int)

    for pattern in patterns:
        pattern_counts[pattern] = len(re.findall(pattern, string))

    return dict(pattern_counts)

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
        string_length = fdp.ConsumeIntInRange(1, 100)
        input_string = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))

        patterns_list_length = fdp.ConsumeIntInRange(1, 10)
        input_patterns = []
        for _ in range(patterns_list_length):
            pattern_length = fdp.ConsumeIntInRange(1, 20)
            input_patterns.append(''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10))))

        out_a = solve_a(input_string, input_patterns)
        out_b = solve_b(input_string, input_patterns)
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
