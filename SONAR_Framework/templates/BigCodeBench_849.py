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
from nltk.corpus import stopwords
from collections import Counter

STOPWORDS = set(stopwords.words('english'))

def _solve_a_impl(input_string):
    """
    Divide a multi-line string into individual lines, remove stopwords, and count the frequency of each word.

    Parameters:
    - input_string (str): The multi-line string.

    Returns:
    - dict: A dictionary with word frequencies where each key is a unique word and the value is its frequency.

    Requirements:
    - re
    - nltk.corpus
    - collections

    Example:
    >>> _solve_a_impl('line a\\nfollows by line b\\n...bye\\n')
    {'line': 2, 'follows': 1, 'b': 1, 'bye': 1}
    """
    lines = input_string.split('\n')
    word_count = Counter()
    for line in lines:
        words = re.findall(r'\b\w+\b', line)
        words = [word for word in words if word not in STOPWORDS]
        word_count.update(words)
    return dict(word_count)

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
        stopwords_sample = ['i', 'me', 'we', 'you', 'he', 'she', 'it', 'they',
                            'is', 'are', 'was', 'be', 'have', 'do', 'does',
                            'a', 'an', 'the', 'and', 'but', 'or', 'in', 'on',
                            'at', 'to', 'for', 'of', 'with', 'this', 'not']
        word_chars = list('abcdefghijklmnopqrstuvwxyz')
        num_lines = fdp.ConsumeIntInRange(1, 5)
        lines = []
        for _ in range(num_lines):
            num_words = fdp.ConsumeIntInRange(1, 8)
            words = []
            for _ in range(num_words):
                if fdp.ConsumeBool():
                    words.append(fdp.PickValueInList(stopwords_sample))
                else:
                    words.append(''.join(fdp.PickValueInList(word_chars) for _ in range(fdp.ConsumeIntInRange(2, 8))))
            lines.append(' '.join(words))
        input_string = '\n'.join(lines)

        out_a = solve_a(input_string)
        out_b = solve_b(input_string)
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
