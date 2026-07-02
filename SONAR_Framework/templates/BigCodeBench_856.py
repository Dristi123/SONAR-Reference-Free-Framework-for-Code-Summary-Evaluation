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
from itertools import combinations
import numpy as np


def _solve_a_impl(shape=(3, 3), low=1, high=10, seed=None):
    """
    Generate a matrix of specified shape and random numbers within a specified 
    range. Generate a list of all possible number pairs (all possible combinations of
    two numbers which are in the matrix) in the matrix.
    Calculate the sum of the products of all pairs.

    Parameters:
    shape (tuple): Shape of the matrix, default is (3, 3).
    low (int): Lower bound of the random number generation, inclusive (default is 1).
    high (int): Upper bound of the random number generation, exclusive (default is 10).
    seed (int, optional): Seed for the random number generator for reproducible results. If None, the random number 
                          generator is initialized without a seed (default is None).

    Returns:
    int: The sum of products of all possible number pairs within the generated matrix.
    np.array: The generated matrix.

    Raises:
    ValueError: If high <= low

    Requirements:
    - functools.reduce
    - itertools.combinations
    - numpy

    Example:
    >>> _solve_a_impl((2, 2), 1, 5, seed=42)
    (43, array([[3, 4],
           [1, 3]]))

    >>> _solve_a_impl((5, 4), seed=1)
    (4401, array([[6, 9, 6, 1],
           [1, 2, 8, 7],
           [3, 5, 6, 3],
           [5, 3, 5, 8],
           [8, 2, 8, 1]]))
    """
    if seed is not None:
        np.random.seed(seed)

    if high <= low:
        raise ValueError("The 'high' parameter must be greater than 'low'.")

    matrix = np.random.randint(low, high, shape)
    values = matrix.flatten()

    all_pairs = list(combinations(values, 2))

    sum_of_products = reduce(lambda a, b: a + b, [np.prod(pair) for pair in all_pairs])

    return sum_of_products, matrix

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
        import random # Required for the general random seed instruction
        import numpy as _fuzz_np # Required for the general numpy seed instruction

        # Generate shape tuple
        dim1 = fdp.ConsumeIntInRange(1, 5)  # Restrict dimensions to avoid excessively large matrices
        dim2 = fdp.ConsumeIntInRange(1, 5)
        shape = (dim1, dim2)

        # Generate low and high values, ensuring high > low
        low = fdp.ConsumeIntInRange(-20, 20)  # A reasonable range for numbers in the matrix
        # Ensure high is strictly greater than low
        # Consume a positive difference and add it to low
        diff = fdp.ConsumeIntInRange(1, 40) # Ensures high is between low + 1 and low + 40
        high = low + diff

        # Generate seed parameter for task_func
        use_seed_param = fdp.ConsumeBool()
        seed_param = fdp.ConsumeIntInRange(0, 1000) if use_seed_param else None

        # Set global random and numpy seeds before calling solve_a
        # This ensures deterministic behavior, especially if seed_param is None
        random.seed(42)
        _fuzz_np.random.seed(42)
        out_a = solve_a(shape=shape, low=low, high=high, seed=seed_param)

        # Set global random and numpy seeds again before calling solve_b
        random.seed(42)
        _fuzz_np.random.seed(42)
        out_b = solve_b(shape=shape, low=low, high=high, seed=seed_param)
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
