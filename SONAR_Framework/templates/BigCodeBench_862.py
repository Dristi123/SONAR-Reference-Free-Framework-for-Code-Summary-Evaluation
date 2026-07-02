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
import string
from collections import defaultdict


def _solve_a_impl(n, seed=None):
    """
    Generate a dictionary with lists of random lowercase english letters. 
    
    Each key in the dictionary  represents a unique letter from the alphabet,
    and the associated value is a list, containing randomly generated instances
    of that letter based on a seed.

    The function randomly selects 'n' letters from the alphabet (a-z) and places each 
    occurrence in the corresponding list within the dictionary. The randomness is based
    on the provided seed value; the same seed will produce the same distribution of letters.

    The dictionary has only those keys for which a letter was generated.

    Parameters:
    n (int): The number of random letters to generate.
    seed (int, optional): A seed value for the random number generator. If None, the randomness
                          is based on system time or the OS's randomness source.

    Returns:
    defaultdict: A dictionary where the keys are characters ('a' to 'z') and the values 
                 are lists of randomly generated letters. Each list may have 0 to 'n' occurrences of 
                 its associated letter, depending on the randomness and seed.

    Requirements:
    - collections.defaultdict
    - random
    - string

    Example:
    >>> _solve_a_impl(5, seed=123)
    defaultdict(<class 'list'>, {'b': ['b'], 'i': ['i'], 'c': ['c'], 'y': ['y'], 'n': ['n']})

    >>> _solve_a_impl(30, seed=1)
    defaultdict(<class 'list'>, {'e': ['e'], 's': ['s'], 'z': ['z', 'z', 'z'], 'y': ['y', 'y', 'y', 'y'], 'c': ['c'], 'i': ['i', 'i'], 'd': ['d', 'd'], 'p': ['p', 'p', 'p'], 'o': ['o', 'o'], 'u': ['u'], 'm': ['m', 'm'], 'g': ['g'], 'a': ['a', 'a'], 'n': ['n'], 't': ['t'], 'w': ['w'], 'x': ['x'], 'h': ['h']})
    """
    LETTERS = string.ascii_lowercase
    random.seed(seed)
    letter_dict = defaultdict(list)
    for _ in range(n):
        letter = random.choice(LETTERS)
        letter_dict[letter].append(letter)
    return letter_dict

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
        n = fdp.ConsumeIntInRange(1, 1000)
        use_seed = fdp.ConsumeBool()
        if use_seed:
            seed = fdp.ConsumeIntInRange(-100000, 100000)
        else:
            seed = None

        random.seed(seed)
        out_a = solve_a(n, seed=seed)
        random.seed(seed)
        out_b = solve_b(n, seed=seed)
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
