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


from collections import Counter
import itertools
from random import randint

def _solve_a_impl(T1, RANGE=100):
    """
    Convert elements in 'T1' to integers and create a list of random integers where the number of integers 
    is determined by the sum of the integers in `T1`. Random integers are generated between 0 and `RANGE` 
    (default is 100). Count the occurrences of each number in the generated list using a Counter.
    
    Parameters:
    T1 (tuple of tuples): Each inner tuple contains string representations of numbers that are converted to integers.
    RANGE (int, optional): The upper limit for the random number generation. Defaults to 100.
    
    Returns:
    Counter: A Counter object representing the count of each number appearing in the list of generated random integers.
    
    Requirements:
    - collections.Counter
    - itertools
    - random.randint
    
    Example:
    >>> import random
    >>> random.seed(42)
    >>> T1 = (('13', '17', '18', '21', '32'), ('07', '11', '13', '14', '28'), ('01', '05', '06', '08', '15', '16'))
    >>> counts = _solve_a_impl(T1)
    >>> print(counts)  # Output will be a Counter object with random counts.
    Counter({20: 6, 81: 5, 14: 5, 97: 5, 48: 5, 68: 5, 87: 5, 35: 4, 28: 4, 11: 4, 54: 4, 27: 4, 29: 4, 64: 4, 77: 4, 33: 4, 58: 4, 10: 4, 46: 4, 8: 4, 98: 4, 34: 4, 3: 3, 94: 3, 31: 3, 17: 3, 13: 3, 69: 3, 71: 3, 89: 3, 0: 3, 43: 3, 19: 3, 93: 3, 37: 3, 80: 3, 82: 3, 76: 3, 92: 3, 75: 2, 4: 2, 25: 2, 91: 2, 83: 2, 12: 2, 45: 2, 5: 2, 70: 2, 84: 2, 47: 2, 59: 2, 41: 2, 99: 2, 7: 2, 40: 2, 51: 2, 72: 2, 63: 2, 95: 2, 74: 2, 96: 2, 67: 2, 62: 2, 30: 2, 16: 2, 86: 1, 53: 1, 57: 1, 44: 1, 15: 1, 79: 1, 73: 1, 24: 1, 90: 1, 26: 1, 85: 1, 9: 1, 21: 1, 88: 1, 50: 1, 18: 1, 65: 1, 6: 1, 49: 1, 32: 1, 1: 1, 55: 1, 22: 1, 38: 1, 2: 1, 39: 1})
    """
    int_list = [list(map(int, x)) for x in T1]
    flattened_list = list(itertools.chain(*int_list))
    total_nums = sum(flattened_list)

    random_nums = [randint(0, RANGE) for _ in range(total_nums)]
    counts = Counter(random_nums)

    return counts

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
        # Generate T1 (tuple of tuples of strings representing numbers)
        num_outer_tuples = fdp.ConsumeIntInRange(1, 5) # Number of inner tuples
        T1_list = []
        for _ in range(num_outer_tuples):
            num_inner_strings = fdp.ConsumeIntInRange(1, 5) # Number of string numbers in each inner tuple
            inner_tuple_list = []
            for _ in range(num_inner_strings):
                # Generate an integer between 0 and 100, then convert to string.
                # This range balances avoiding overly large sums (which would create very long random lists)
                # with providing diverse numeric string inputs.
                num_as_int = fdp.ConsumeIntInRange(0, 100)
                inner_tuple_list.append(str(num_as_int))
            T1_list.append(tuple(inner_tuple_list))
        T1_arg = tuple(T1_list)

        # Generate RANGE (optional integer parameter)
        call_with_range = fdp.ConsumeBool()
        if call_with_range:
            # RANGE should be non-negative, as it's used as the upper bound in randint(0, RANGE).
            # The default is 100. We'll allow a range from 0 to 200.
            RANGE_arg = fdp.ConsumeIntInRange(0, 200)
        else:
            RANGE_arg = None # This will cause task_func to use its default RANGE value

        # Ensure 'random' module is imported if not globally available in the fuzzing harness.
        import random

        # Call task_func for solve_a
        random.seed(42) # Set seed for reproducibility and identical random sequences
        if RANGE_arg is not None:
            out_a = solve_a(T1_arg, RANGE_arg)
        else:
            out_a = solve_a(T1_arg)

        # Call task_func for solve_b
        random.seed(42) # Set seed again for the second call
        if RANGE_arg is not None:
            out_b = solve_b(T1_arg, RANGE_arg)
        else:
            out_b = solve_b(T1_arg)
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
