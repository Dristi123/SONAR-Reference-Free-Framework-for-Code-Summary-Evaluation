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
import math

def _solve_a_impl(LETTERS=[chr(i) for i in range(97, 123)]):
    """
    Create a dictionary where keys are letters from a predefined list LETTERS and values are lists of random integers.
    Then, calculates the population standard deviation for each list of integers and returns a dictionary of these values.

    The random integers for each key are generated within the range 0 to 100, and each list contains between 1 to 10 integers.

    Parameters:
        LETTERS (list of str, optional): A list of single-character strings to be used as keys in the output dictionary.
                                         Defaults to the lowercase English alphabets ['a', 'b', ..., 'z'].

    Returns:
        dict: A dictionary where each key corresponds to a letter from the input list and each value is the 
              population standard deviation of a list of random integers associated with that key.

    Requirements:
    - random
    - math

    Example:
    >>> import random
    >>> random.seed(42)
    >>> sd_dict = _solve_a_impl()
    >>> print(sd_dict)
    {'a': 45.5, 'b': 29.4659125092029, 'c': 25.575354649194974, 'd': 28.271717316074028, 'e': 29.118550788114437, 'f': 16.886056048968, 'g': 27.48108440364026, 'h': 32.67476090195611, 'i': 8.5, 'j': 17.5406234036238, 'k': 22.993205518152532, 'l': 2.0, 'm': 25.468935326524086, 'n': 10.23067283548187, 'o': 35.13922924736349, 'p': 26.649654437396617, 'q': 27.027763503479157, 'r': 20.316629447296748, 's': 24.997777679003566, 't': 0.0, 'u': 30.070288030250428, 'v': 21.82864622275892, 'w': 37.92308004368844, 'x': 29.899006961502092, 'y': 33.89321466016465, 'z': 21.0}
    """
    random_dict = {k: [random.randint(0, 100) for _ in range(random.randint(1, 10))] for k in LETTERS}
    sd_dict = {
        k: math.sqrt(sum((i - sum(v) / len(v)) ** 2 for i in v) / len(v))
        for k, v in random_dict.items()
    }
    return sd_dict

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
        
            use_custom_letters = fdp.ConsumeBool()

            if use_custom_letters:
                num_letters = fdp.ConsumeIntInRange(1, 50) # Number of letters for the custom list

                # Manually define char_pool to avoid requiring an 'import string' statement
                # inside the binding code, aligning with the "Output ONLY the binding code" rule.
                char_pool = []
                # Lowercase letters (matching the default range)
                char_pool.extend([chr(i) for i in range(ord('a'), ord('z') + 1)])
                # Uppercase letters
                char_pool.extend([chr(i) for i in range(ord('A'), ord('Z') + 1)])
                # Digits
                char_pool.extend([str(i) for i in range(10)])
                # A few common symbols to broaden the "single-character strings" domain
                char_pool.extend(['!', '@', '#', '$', '%', '&', '*', '+', '-', '_', '='])

                # Cap num_letters by pool size to prevent potential infinite loops
                # if `num_letters` requests more unique characters than available in `char_pool`.
                num_letters = min(num_letters, len(char_pool))

                arg_letters = []
                seen_chars = set()

                # Generate a list of unique single-character strings as dictionary keys.
                # This prevents redundant keys in the internal dictionary construction,
                # ensuring that each `num_letters` effectively results in `num_letters` distinct keys.
                for _ in range(num_letters):
                    char = fdp.PickValueInList(char_pool)
                    # Ensure the picked character is unique within the list
                    while char in seen_chars:
                        char = fdp.PickValueInList(char_pool)
                    seen_chars.add(char)
                    arg_letters.append(char)

                # Set random seed before each call, as task_func uses random internally.
                random.seed(42)
                out_a = solve_a(LETTERS=arg_letters)
                random.seed(42)
                out_b = solve_b(LETTERS=arg_letters)
            else:
                # If the fuzzer decides not to provide custom letters,
                # call task_func without arguments to trigger its default behavior for LETTERS.
                random.seed(42)
                out_a = solve_a()
                random.seed(42)
                out_b = solve_b()
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
