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
import re

# Constants
WORD_LIST = ["sample", "text", "contains", "several", "words", "including"]

def _solve_a_impl(n_sentences):
    """
    Generate a string of random sentences using a predefined word list. 
    Each sentence is guaranteed to have one period at the end, and no period within the sentence.
    The generated sentences will be concatenated into a single string, 
    with all letters in lowercase and all non-alphanumeric characters except spaces removed.

    Parameters:
    - n_sentences (int): The number of sentences to generate.

    Returns:
    - str: A string containing the generated sentences in lowercase 
         with non-alphanumeric characters removed (except for single periods ending sentences).
    
    Requirements:
    - random
    - re
    
    Example:
    >>> random.seed(42)
    >>> result = _solve_a_impl(2)
    >>> print(result)
    sample sample including contains text text text including sample including. words sample words several sample sample sample text text words.
    
    Note: 
    - The actual output will vary due to the randomness of sentence generation.
    """
    sentences = []
    for _ in range(n_sentences):
        sentence_len = random.randint(5, 10)
        sentence = " ".join(random.choice(WORD_LIST) for _ in range(sentence_len)) + "."
        sentences.append(sentence)

    # Join sentences and ensure no extra spaces around periods
    text = " ".join(sentences)
    # Remove unwanted characters, ensure only letters, spaces, or periods remain
    text = re.sub(r'[^\w\s.]', '', text).lower()
    # Normalize spaces ensuring single space between words and no trailing spaces before periods
    text = re.sub(r'\s+\.', '.', text)
    text = re.sub(r'\s+', ' ', text)

    return text.strip()

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
        n_sentences = fdp.ConsumeIntInRange(1, 100) # The number of sentences to generate.

        random.seed(42)
        out_a = solve_a(n_sentences)
        random.seed(42)
        out_b = solve_b(n_sentences)
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
