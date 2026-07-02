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
from string import punctuation

# Predefined list of common stopwords
PREDEFINED_STOPWORDS = {
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", 
    "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", 
    "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves", 
    "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", 
    "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", 
    "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", 
    "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", 
    "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", 
    "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "more"
}

def _solve_a_impl(text):
    """
    Clean the specified text by removing URLs, stopwords, and punctuation.

    Parameters:
    text (str): The text to be cleaned.

    Returns:
    str: The cleaned text with URLs, predefined stopwords, and punctuation removed.

    Requirements:
    - re
    - string.punctuation

    Example:
    >>> _solve_a_impl('Visit https://www.python.org for more info. I love to eat apples.')
    'Visit info love eat apples'
    """
    # Constants
    PUNCTUATION = set(punctuation)

    # Remove URLs
    text = re.sub('http[s]?://\S+', '', text)

    # Remove punctuation
    text = re.sub('[{}]'.format(re.escape(''.join(PUNCTUATION))), '', text)

    # Tokenize the text
    words = text.split()

    # Remove stopwords
    cleaned_words = [word for word in words if word.lower() not in PREDEFINED_STOPWORDS]

    return ' '.join(cleaned_words)

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
                            'is', 'are', 'was', 'be', 'have', 'do', 'a', 'an',
                            'the', 'and', 'but', 'or', 'in', 'on', 'at', 'to',
                            'for', 'of', 'with', 'this', 'not', 'if', 'more']
        word_chars = list('abcdefghijklmnopqrstuvwxyz')
        num_tokens = fdp.ConsumeIntInRange(1, 10)
        tokens = []
        for _ in range(num_tokens):
            choice = fdp.ConsumeIntInRange(0, 2)
            if choice == 0:
                tokens.append(fdp.PickValueInList(stopwords_sample))
            elif choice == 1:
                tokens.append(''.join(fdp.PickValueInList(word_chars) for _ in range(fdp.ConsumeIntInRange(2, 8))))
            else:
                domain = ''.join(fdp.PickValueInList(word_chars) for _ in range(fdp.ConsumeIntInRange(3, 8)))
                tokens.append(f'https://{domain}.com')
        text_input = ' '.join(tokens)
        if fdp.ConsumeBool():
            text_input += fdp.PickValueInList(list('.,!?;:'))

        out_a = solve_a(text_input)
        out_b = solve_b(text_input)
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
