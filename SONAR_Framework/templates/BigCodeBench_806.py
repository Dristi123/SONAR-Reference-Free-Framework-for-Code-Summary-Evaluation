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
import nltk
nltk.download('stopwords')

from nltk.corpus import stopwords

from collections import Counter

# Constants
STOPWORDS = set(stopwords.words('english'))

def _solve_a_impl(text, n=2):
    """
    Remove duplicate and stopwords from a string "text."
    Then, generate a count of n-grams (default is bigrams) in the text.

    Parameters:
    - text (str): The text string to analyze.
    - n (int): The size of the n-grams.

    Returns:
    - dict: The count of the n-grams in the text.

    Requirements:
    - re
    - nltk.corpus.stopwords
    - collections.Counter

    Example:
    >>> text = "The quick brown fox jumps over the lazy dog and the dog was not that quick to respond."
    >>> ngrams = _solve_a_impl(text)
    >>> print(ngrams)
    Counter({('quick', 'brown'): 1, ('brown', 'fox'): 1, ('fox', 'jumps'): 1, ('jumps', 'lazy'): 1, ('lazy', 'dog'): 1, ('dog', 'dog'): 1, ('dog', 'quick'): 1, ('quick', 'respond'): 1})
    """
    # Normalize spaces and remove punctuation
    text = re.sub(r'[^\w\s]', '', text)  # Remove all punctuation
    text = re.sub(r'\s+', ' ', text)  # Normalize whitespace

    # Filter out stopwords and split into words
    words = [word.lower() for word in text.split() if word.lower() not in STOPWORDS]

    # Generate n-grams
    ngrams = zip(*[words[i:] for i in range(n)])

    return Counter(ngrams)

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
            num_words = fdp.ConsumeIntInRange(2, 10)
            words = []
            for _ in range(num_words):
                if fdp.ConsumeBool():
                    words.append(fdp.PickValueInList(stopwords_sample))
                else:
                    words.append(''.join(fdp.PickValueInList(word_chars) for _ in range(fdp.ConsumeIntInRange(2, 8))))
            text = ' '.join(words)
            n = fdp.ConsumeIntInRange(1, 5) # n-gram size, typically 1 (unigram) to 5 (pentagram)

            out_a = solve_a(text, n)
            out_b = solve_b(text, n)
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
