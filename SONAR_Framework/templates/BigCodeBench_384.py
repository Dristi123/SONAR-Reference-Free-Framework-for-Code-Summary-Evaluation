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


import collections
import random
import itertools


ANIMALS = ['Cat', 'Dog', 'Elephant', 'Lion', 'Tiger', 'Bear', 'Giraffe', 'Horse', 'Rabbit', 'Snake', 'Zebra']

def _solve_a_impl(animal_dict, max_count=10, seed=0):
    """
    Given a constant list of animals in ANIMALS, and a dictionary 'animal_dict' with keys as people's names and values
    as their favorite animal names, reverse the keys and values in a given dictionary and count the occurrences of each
    predefined animal name with a random count. Return the reversed dictionary and the counter with animal name
    occurrences.

    This function performs two tasks:
    1. It reverses the given dictionary (animal_dict) such that the original values become keys and the original 
    keys become lists of values.
    2. It counts the occurrences of each animal name in a predefined list (ANIMALS). The count of each animal name
    is a random integer between 1 and max_count (inclusive).

    Parameters:
    animal_dict (dict): A dictionary with keys as names and values as animal names.
    max_count (int, Optional): A positive integer denoting the maximum count of each animal. Default is 10.
    Must be greater than 0.
    seed (int, Optional): An integer to seed the random number generator. Default is 0.

    Returns:
    tuple: A tuple where the first element is a reversed dictionary and the second element is a counter with animal 
           name occurrences (with randomness in count).

    Requirements:
    - collections
    - random
    - itertools

    Example:
    >>> animal_dict = {'John': 'Cat', 'Alice': 'Dog', 'Bob': 'Elephant', 'Charlie': 'Lion', 'David': 'Tiger', 'Sue': 'Pangolin'}
    >>> reversed_dict, animal_counter = _solve_a_impl(animal_dict, 15, 77)
    >>> reversed_dict
    {'Cat': ['John'], 'Dog': ['Alice'], 'Elephant': ['Bob'], 'Lion': ['Charlie'], 'Tiger': ['David']}
    >>> dict(animal_counter.most_common(5))
    {'Giraffe': 14, 'Cat': 13, 'Zebra': 9, 'Snake': 8, 'Elephant': 6}
    """
    if max_count < 1:
        raise ValueError("max_count must be a positive integer")

    random.seed(seed)

    reversed_dict = {v: [] for v in animal_dict.values() if isinstance(v, str) and v in ANIMALS}
    for k, v in animal_dict.items():
        if isinstance(v, str) and v in ANIMALS:
            reversed_dict[v].append(k)

    animal_counter = collections.Counter(itertools.chain.from_iterable([[v] * random.randint(1, max_count) for v in ANIMALS]))
    return reversed_dict, animal_counter

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
     
            animal_dict_len = fdp.ConsumeIntInRange(0, 10)
            animal_dict = {}
            for _ in range(animal_dict_len):
                key = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))
                # Mix valid ANIMALS values with random strings so filter logic is exercised
                if fdp.ConsumeBool():
                    value = fdp.PickValueInList(ANIMALS)
                else:
                    value = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))
                animal_dict[key] = value

            max_count = fdp.ConsumeIntInRange(1, 100) # max_count must be > 0
            seed = fdp.ConsumeIntInRange(0, 100000)

            random.seed(seed)
            out_a = solve_a(animal_dict, max_count, seed)
            random.seed(seed)
            out_b = solve_b(animal_dict, max_count, seed)
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
