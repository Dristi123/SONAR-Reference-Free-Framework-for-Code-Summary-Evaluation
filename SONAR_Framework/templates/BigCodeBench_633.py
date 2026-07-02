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


def _solve_a_impl(text: str) -> dict:
    """
    Analyzes a given text string by removing duplicate words and stopwords defined by nltk.corpus ,
    and then returns a frequency distribution of the remaining words.

    Parameters:
    - text (str): The text string to analyze.

    Returns:
    - dict: The frequency distribution of the words in the text after filtering.

    Requirements:
    - re
    - nltk.corpus

    Note:
    - A manually defined set of common English stopwords is used for filtering.

    Examples:
    >>> _solve_a_impl("The quick brown fox jumps over the lazy dog and the dog was not that quick to respond.")
    {'quick': 1, 'brown': 1, 'fox': 1, 'jumps': 1, 'lazy': 1, 'dog': 1, 'respond': 1}

    >>> _solve_a_impl("hello hello world")
    {'hello': 1, 'world': 1}
    """
    # Remove duplicate words
    stop_words = set(stopwords.words('english'))
    text = ' '.join(sorted(set(text.split()), key=text.index))
    # Tokenize and remove stopwords
    words = [word for word in re.findall(r'\b\w+\b', text.lower()) if word not in stop_words]
    
    # Create frequency distribution
    freq_dist = {}
    for word in words:
        freq_dist[word] = freq_dist.get(word, 0) + 1
    
    return freq_dist

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
     
            stopwords_sample = ['i', 'me', 'my', 'we', 'you', 'he', 'she', 'it', 'they',
                                'is', 'are', 'was', 'be', 'have', 'do', 'does', 'did',
                                'a', 'an', 'the', 'and', 'but', 'or', 'in', 'on', 'at',
                                'to', 'for', 'of', 'with', 'this', 'not', 'by', 'from']
            word_chars = list('abcdefghijklmnopqrstuvwxyz')
            num_words = fdp.ConsumeIntInRange(1, 10)
            words = []
            for _ in range(num_words):
                if fdp.ConsumeBool():
                    words.append(fdp.PickValueInList(stopwords_sample))
                else:
                    words.append(''.join(fdp.PickValueInList(word_chars) for _ in range(fdp.ConsumeIntInRange(2, 8))))
            text = ' '.join(words)
            out_a = solve_a(text)
            out_b = solve_b(text)
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
