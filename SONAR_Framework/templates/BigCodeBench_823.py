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


import time
import numpy as np


def _solve_a_impl(samples=10, delay=0.1):
    """
    Make a delay for a given amount of time for a specified number of samples,
    measure the actual delay and calculate the statistical properties of the
    delay times.

    Parameters:
    - samples (int): Number of samples for which the delay is measured.
                     Default is 10.
    - delay (float): Amount of time (in seconds) for each delay.
                     Default is 0.1 second.

    Returns:
    tuple: The mean and standard deviation of the delay times.

    Requirements:
    - time
    - numpy

    Example:
    >>> mean, std = _solve_a_impl(samples=5, delay=0.05)
    >>> print(f'Mean: %.3f, Std: %.1f' % (mean, std))
    Mean: 0.050, Std: 0.0
    >>> mean, std = _solve_a_impl(100, 0.001)
    >>> print(f'Mean: %.3f, Std: %.4f' % (mean, std))
    Mean: 0.001, Std: 0.0000
    """
    delay_times = []

    for _ in range(samples):
        t1 = time.time()
        time.sleep(delay)
        t2 = time.time()
        delay_times.append(t2 - t1)

    delay_times = np.array(delay_times)

    mean = np.mean(delay_times)
    std = np.std(delay_times)

    return mean, std

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
      
            samples = fdp.ConsumeIntInRange(1, 100)
                    # Delay should be positive. Using a range that gives 0.001 to 1.0 seconds.
            delay = fdp.ConsumeIntInRange(1, 1000) / 1000.0 

            out_a = solve_a(samples, delay)
            out_b = solve_b(samples, delay)
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
