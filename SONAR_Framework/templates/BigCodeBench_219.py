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


import math
import statistics
import numpy as np


def _solve_a_impl(input_list):
    """
    Sorts the input list in ascending order based on the degree value of its elements, and then 
    calculates the mean, median, and mode of both the sorted list and the same for the magnitude of 
    the fast fourier transform of the degree values upto the nearest integer.

    Parameters:
    input_list (list): A list of numbers to be sorted and analyzed.

    Returns:
    tuple: A tuple containing the rounded mean, median and mode of the sorted list along with those 
    for the magnitude of the fast fourier transform of the degree values.

    Requirements:
    - math
    - statistics
    - numpy

    Example:
    >>> input_list = [30, 45, 60, 90, 180]
    >>> stats = _solve_a_impl(input_list)
    >>> print(stats)
    (81, 60, 30, 10712, 8460, 8460)
    """
    fft = np.abs(np.fft.fft([math.degrees(x) for x in input_list]))
    sorted_list = sorted(input_list, key=lambda x: (math.degrees(x), x))
    mean = statistics.mean(sorted_list)
    median = statistics.median(sorted_list)
    mode = statistics.mode(sorted_list)
    mean_fft = round(statistics.mean(fft))
    median_fft = round(statistics.median(fft))
    mode_fft = round(statistics.mode(fft))
    return (mean, median, mode, mean_fft, median_fft, mode_fft)

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
        list_len = fdp.ConsumeIntInRange(1, 10)
        input_list = []
        for _ in range(list_len):
            input_list.append(fdp.ConsumeIntInRange(-10000, 10000) / 100.0)

        out_a = solve_a(input_list)
        out_b = solve_b(input_list)
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
