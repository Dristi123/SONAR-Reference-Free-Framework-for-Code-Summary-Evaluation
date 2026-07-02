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


import string
import random
import re


def _solve_a_impl(elements, pattern, seed=100):
    """
    Replace each character in each element of the Elements list with a random 
    character and format the element into a pattern "%{0}%", where {0} is the
    replaced element. Finally, concatenate all the formatted elements into a 
    single string and search for the regex pattern specified in the parameter 
    pattern. Return the true or false value based on the search result.
        
    Parameters:
        elements (List[str]): The list of elements.
        pattern (str): The pattern to format the elements.
        seed (int, Optional): The seed for the random number generator. Defaults to 100.
    
    Returns:    
        List[str]: The list of formatted elements with replaced characters.
        bool: The search result based on the regex pattern.
        
    Requirements:
        - re
        - string
        - random
        
    Example:
    >>> ELEMENTS = ["abc", "def"]
    >>> pattern = ".*"
    >>> replaced_elements, result = _solve_a_impl(ELEMENTS, pattern, 234)
    >>> print(replaced_elements)
    ['%vqd%', '%LAG%']
    """
    # Set the seed for reproducibility
    random.seed(seed)
    replaced_elements = []
    
    for element in elements:
        replaced = ''.join([random.choice(string.ascii_letters) for _ in element])
        formatted = '%{}%'.format(replaced)
        replaced_elements.append(formatted)
        
    # Concatenate all the formatted elements into a single string
    concatenated_elements = ''.join(replaced_elements)
    # Search for the regex pattern in the concatenated string
    search_result = re.search(pattern, concatenated_elements)
    # Return the search result
    return replaced_elements, bool(search_result)

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
        elements_len = fdp.ConsumeIntInRange(0, 10)
        elements = []
        for _ in range(elements_len):
            elements.append(''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10))))

        pattern = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))

        seed = fdp.ConsumeIntInRange(0, 2**32 - 1)

        out_a = solve_a(elements, pattern, seed)
        out_b = solve_b(elements, pattern, seed)
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
