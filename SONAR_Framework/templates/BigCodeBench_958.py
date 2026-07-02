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


def _solve_a_impl(text, seed=None):
    """
    Scramble the letters in each word of a given text, keeping the first and last letters of each word intact.

    Parameters:
    text (str): The text to be scrambled.
    seed (int, optional): A seed for the random number generator to ensure reproducible results.
                          Defaults to None (not set).

    Returns:
    str: The scrambled text.

    Requirements:
    - random
    - re

    Notes:
    - Words are determined by regex word boundaries.
    - The scrambling only affects words longer than three characters, leaving shorter words unchanged.

    Examples:
    >>> _solve_a_impl('Hello, world!', 0)
    'Hello, wlrod!'
    >>> _solve_a_impl("Programming is fun, isn't it?", 42)
    "Prmiangmrog is fun, isn't it?"
    """
    if seed is not None:
        random.seed(seed)

    def scramble_word(match):
        word = match.group(0)
        if len(word) > 3:
            middle = list(word[1:-1])
            random.shuffle(middle)
            return word[0] + "".join(middle) + word[-1]
        else:
            return word

    pattern = r"\b\w+\b"
    scrambled_text = re.sub(pattern, scramble_word, text)

    return scrambled_text

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
        word_chars = list('abcdefghijklmnopqrstuvwxyz')
        num_words = fdp.ConsumeIntInRange(1, 5)
        words = [''.join(fdp.PickValueInList(word_chars) for _ in range(fdp.ConsumeIntInRange(2, 8))) for _ in range(num_words)]
        text_input = ' '.join(words)

        # Decide if the seed argument should be None or an integer
        use_seed_arg = fdp.ConsumeBool()
        seed_arg = None
        if use_seed_arg:
            seed_arg = fdp.ConsumeIntInRange(0, 100000) # Use a reasonable range for the seed

        # If seed_arg is None, task_func will use the global random state.
        # To ensure reproducibility between solve_a and solve_b in this case,
        # we explicitly seed the global random generator.
        # If seed_arg is not None, task_func handles seeding internally.

        if seed_arg is None:
            random.seed(42)
        out_a = solve_a(text_input, seed_arg)

        if seed_arg is None:
            random.seed(42) # Re-seed for the second call to ensure identical random sequence
        out_b = solve_b(text_input, seed_arg)
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
