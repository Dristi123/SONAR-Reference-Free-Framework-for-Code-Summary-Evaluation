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
import random
from nltk.corpus import words
from random import sample

# Ensure the words corpus is downloaded
import nltk
nltk.download('words')

# Constants
SAMPLE_ENGLISH_WORDS = set(words.words())  # Correct initialization

def _solve_a_impl(s, n):
    """
    Extract up to n different English words from a string, ignoring case. 
    The string is split into words and only the English words are retained.
    If there are fewer than n different English words, all distinct ones are returned.
    
    Parameters:
    - s (str): The string to extract words from.
    - n (int): The maximum number of different English words to extract.
    
    Returns:
    - List[str]: A list of up to n different English words found in the string.

    Requirements:
    - re
    - nltk
    - random
    
    Example:
    Given the nature of random sampling, the specific output can vary.
    >>> s = 'This is an example string with some random words: Apple, banana, Test, hello, world'
    >>> len(_solve_a_impl(s, 5)) <= 5
    True
    >>> set(_solve_a_impl("apple Apple APPle", 3)) == {"apple"}
    True
    """

    word_list = re.findall(r'\b\w+\b', s.lower())  # Convert to lowercase for comparison
    english_words = [word for word in word_list if word in SAMPLE_ENGLISH_WORDS]
    if len(english_words) < n:
        return english_words
    else:
        return sample(english_words, n)

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
        english_words = ['apple', 'banana', 'computer', 'dragon', 'engine', 'forest',
                         'guitar', 'house', 'island', 'jungle', 'kitchen', 'lemon',
                         'monkey', 'nature', 'ocean', 'planet', 'queen', 'river',
                         'school', 'tiger', 'umbrella', 'village', 'window', 'yellow']
        word_chars = list('abcdefghijklmnopqrstuvwxyz')
        num_tokens = fdp.ConsumeIntInRange(1, 10)
        tokens = []
        for _ in range(num_tokens):
            if fdp.ConsumeBool():
                tokens.append(fdp.PickValueInList(english_words))
            else:
                tokens.append(''.join(fdp.PickValueInList(word_chars) for _ in range(fdp.ConsumeIntInRange(2, 6))))
        s = ' '.join(tokens)
        n = fdp.ConsumeIntInRange(1, 10) # n should be a positive integer, max 10 seems reasonable for fuzzing

        random.seed(42)
        out_a = solve_a(s, n)
        random.seed(42)
        out_b = solve_b(s, n)
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
