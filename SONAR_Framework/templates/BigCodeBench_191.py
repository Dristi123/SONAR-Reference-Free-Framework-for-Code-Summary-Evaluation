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
from scipy import stats

def _solve_a_impl(animals, mean):
    """
    Simulates sales in a pet shop based on a randomly determined number of customers.
    Each customer randomly buys one type of animal from the specified list of animals.
    The function displays and returns a summary of the sales, where the number of customers 
    follows a Poisson distribution with the specified mean (mu).

    Parameters:
        animals (list of str): A list of animal types available for sale.

    Returns:
        dict: A dictionary with animal types as keys and the number of sales as values.

    Requirements:
    - random
    - scipy.stats

    Examples:
    >>> ANIMALS = ['Dog', 'Cat', 'Bird', 'Fish', 'Hamster']
    >>> sales = _solve_a_impl(ANIMALS, 120)
    >>> isinstance(sales, dict)
    True
    >>> all(animal in ANIMALS for animal in sales.keys())
    True
    >>> sum(sales.values()) >= 0  # sum of sales should be non-negative
    True
    """
    if not animals:
        return {}

    sales = {animal: 0 for animal in animals}
    num_customers = stats.poisson(mu=mean).rvs()

    for _ in range(num_customers):
        animal = random.choice(animals)
        sales[animal] += 1
    return sales

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
        # Generate 'mean' (float, non-negative)
                mean = fdp.ConsumeIntInRange(0, 100000) / 100.0

                # Generate 'animals' (list of strings)
                num_animals = fdp.ConsumeIntInRange(0, 10) # 0 to 10 animal types
                animals = []
                for _ in range(num_animals):
                    # Each animal name string length between 1 and 20
                    animal_name_len = fdp.ConsumeIntInRange(1, 20)
                    animals.append(''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10))))

                random.seed(42)
                out_a = solve_a(animals, mean)
                random.seed(42)
                out_b = solve_b(animals, mean)
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
