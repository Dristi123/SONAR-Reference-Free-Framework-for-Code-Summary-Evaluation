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
from nltk.stem import PorterStemmer

def _solve_a_impl(text_series):
    """
    Process a pandas Series of text data by lowercasing all letters, removing non-alphanumeric 
    characters (except spaces), removing punctuation, and stemming each word to its root form.
    
    Stemming is done using the NLTK's PorterStemmer, which applies a series of rules to find the stem of each word.
    
    Parameters:
    - text_series (pandas.Series): A Series object containing string entries representing text data.

    Requirements:
    - re
    - nltk

    Returns:
    - pandas.Series: A Series where each string has been processed to remove non-alphanumeric characters,
      punctuation, converted to lowercase, and where each word has been stemmed.
    
    Examples:
    >>> input_series = pd.Series(["This is a sample text.", "Another example!"])
    >>> output_series = _solve_a_impl(input_series)
    >>> print(output_series.iloc[0])
    thi is a sampl text
    >>> print(output_series.iloc[1])
    anoth exampl

    """
    stemmer = PorterStemmer()

    def process_text(text):
        # Remove non-alphanumeric characters (except spaces)
        text = re.sub('[^\sa-zA-Z0-9]', '', text).lower().strip()
        # Stem each word in the text
        text = " ".join([stemmer.stem(word) for word in text.split()])

        return text

    # Apply the processing to each entry in the Series
    return text_series.apply(process_text)

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
        import pandas as pd
        series_len = fdp.ConsumeIntInRange(1, 10)
        text_list = []
        for _ in range(series_len):
            # Text can contain a variety of characters, including alphanumeric, spaces, and punctuation.
            # The function handles removal and conversion internally.
            text_list.append(''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10))))
        text_series = pd.Series(text_list)

        out_a = solve_a(text_series)
        out_b = solve_b(text_series)
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
