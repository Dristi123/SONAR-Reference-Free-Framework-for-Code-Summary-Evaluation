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
import json
from collections import defaultdict
import string

def _solve_a_impl(json_string):
    """
    Process a JSON string containing a "text" field: convert to lowercase, remove punctuation, and count word frequency.

    This function takes a JSON string with a field named "text", and returns a dictionary with word counts. 
    It processes the text by converting it to lowercase, removing all punctuation and non-alphanumeric characters 
    (except spaces), and then counting the frequency of each word.

    Parameters:
    - json_string (str): A JSON string with a "text" field to process.

    Returns:
    - dict: A dictionary with words as keys and their frequency counts as values. If the "text" field is missing, 
      returns an empty dictionary.

    Requirements:
    - re
    - json
    - collections
    - string

    Example:
    >>> json_input = '{"text": "Hello world! Hello universe. World, meet universe."}'
    >>> _solve_a_impl(json_input)
    {'hello': 2, 'world': 2, 'universe': 2, 'meet': 1}

    Notes:
    - Punctuation is removed using the `string.punctuation` constant.
    - The function is case-insensitive and treats words like "Hello" and "hello" as the same word.
    - If the JSON string is malformed or the "text" field is missing, an empty dictionary is returned.
    """
    try:
        # Load JSON and extract text
        data = json.loads(json_string)
        text = data.get('text', '')
    except json.JSONDecodeError:
        return {}

    # Lowercase, remove non-alphanumeric characters except spaces, remove punctuation
    text = re.sub('[^\sa-zA-Z0-9]', '', text).lower().strip()
    text = text.translate({ord(c): None for c in string.punctuation})

    # Count words
    word_counts = defaultdict(int)
    for word in text.split():
        word_counts[word] += 1

    return dict(word_counts)

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
        # Generate the content for the 'text' field within the JSON
                # The text can contain a wide range of characters including alphanumeric, spaces, and punctuation
                # as the function specifically handles their removal/conversion.
                char_pool = list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ ') + list('.,!?;:\'\"()-')
                num_words = fdp.ConsumeIntInRange(1, 10)
                words = [''.join(fdp.PickValueInList(char_pool) for _ in range(fdp.ConsumeIntInRange(1, 8))) for _ in range(num_words)]
                text_content = ' '.join(words)

                # Create a dictionary that will be serialized to JSON.
                # Ensure it has a 'text' field as described.
                json_data_dict = {"text": text_content}

                # Serialize the dictionary to a JSON string.
                # json.dumps handles proper escaping and formatting.
                json_string = json.dumps(json_data_dict)

                out_a = solve_a(json_string)
                out_b = solve_b(json_string)
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
