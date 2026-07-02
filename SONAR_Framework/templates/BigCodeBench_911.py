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


from functools import reduce
import operator
import string

def _solve_a_impl(letters):
    """
    Calculate the product of the corresponding numbers for a list of uppercase letters, 
    where \"A\" corresponds to 1, \"B\" to 2, etc.
    
    Parameters:
    letters (list of str): A list of uppercase letters.
    
    Returns:
    int: The product of the numbers corresponding to the input letters.
    
    Requirements:
    - functools.reduce
    - operator
    - string
    
    Examples:
    >>> _solve_a_impl([\"A\", \"B\", \"C\"])
    6
    
    >>> _solve_a_impl([\"A\", \"E\", \"I\"])
    45
    
    Note:
    The function uses a predefined dictionary to map each uppercase letter to its corresponding number.
    """
    # Creating a dictionary to map each letter to its corresponding number
    letter_to_number = {letter: i+1 for i, letter in enumerate(string.ascii_uppercase)}
    
    # Convert the letters to numbers
    numbers = [letter_to_number[letter] for letter in letters]
    
    # Calculate the product using functools.reduce and operator.mul
    product = reduce(operator.mul, numbers, 1)
    
    return product

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
        # Generate 'letters' (list of uppercase letters)
                letters_length = fdp.ConsumeIntInRange(1, 10) # Determine the length of the list
                letters = []
                # Populate the list with uppercase letters
                for _ in range(letters_length):
                    # Each element is a single uppercase letter from A-Z
                    # Using list(string.ascii_uppercase) to provide the character set to PickValueInList
                    letter = fdp.PickValueInList(list(string.ascii_uppercase))
                    letters.append(letter)

                # Call the function under test
                out_a = solve_a(letters)
                out_b = solve_b(letters)
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
