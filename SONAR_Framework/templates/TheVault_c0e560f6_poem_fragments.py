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


def _solve_a_impl(poem_series, split_into):
    poem = poem_series
    poem_author = poem.author
    poem_title = poem.title
    poem_content = poem.content
    poem_pa= poem.content.split('.\n')
    i=0
    while ((i+1)!=(len(poem_pa))):
        if (len(poem_pa[i].split())>=split_into):
            poem_pa[i]=poem_pa[i]+'.\n'
            i+=1
        else:
            poem_pa[i] =  poem_pa[i]+'.\n'+poem_pa[i+1]
            del poem_pa[i+1]
    return  (poem_author, poem_title  ,poem_pa)

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
        class MockPoemSeries:
            def __init__(self, author, title, content):
                self.author = author
                self.title = title
                self.content = content

        # Generate author string
        author_str = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))

        # Generate title string
        title_str = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))

        # Generate content string, mimicking "sentences" or "paragraphs" separated by '.\n'
        num_poem_fragments = fdp.ConsumeIntInRange(1, 10)
        content_parts = []
        for _ in range(num_poem_fragments):
            num_words_in_part = fdp.ConsumeIntInRange(1, 50) # Each part will have 1 to 50 words
            words = [''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10))) for _ in range(num_words_in_part)]
            content_parts.append(' '.join(words))

        # Join the generated fragments with '.\n' to form the full content string
        content_str = '.\n'.join(content_parts)

        # Instantiate the mock poem series object
        poem_series_obj = MockPoemSeries(author_str, title_str, content_str)

        # Generate the split_into integer, representing the minimum word count threshold
        split_into_val = fdp.ConsumeIntInRange(1, 50)

        # Call the functions under test
        out_a = solve_a(poem_series_obj, split_into_val)
        out_b = solve_b(poem_series_obj, split_into_val)
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
