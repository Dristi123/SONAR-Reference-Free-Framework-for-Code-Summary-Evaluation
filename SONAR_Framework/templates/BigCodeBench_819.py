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
import random


def _solve_a_impl(iterations=5, min_delay=1.0, max_delay=2.0, seed=None):
    """
    Simulates a delay and then returns a message indicating the elapsed time. This is repeated for a specified number of iterations.

    For each iteration the delay is randomly sampled from a uniform distribution specified by min_delay and max_delay.
    After each iteration the message: '{delay} seconds have passed', where {delay} is replaces with the actual delay
    of the iteration with 2 positions after the decimal point, is saved to an array.

    The function returns a list of all messages, as well as the total delay.

    Parameters:
    - iterations (int): The number of times the delay and message should be simulated. Default is 5.
    - min_delay (float): The duration (in seconds) of the delay between messages. Default is 1.0.
    - max_delay (float): The max delay of each iteration in seconds. Default is 2.0
    - seed (float): The seed used for random sampling the delays for each iteration. Defalut is None.

    Returns:
    - list of str: A list of messages indicating the elapsed time for each iteration.
    - float: The total amount of delay

    Raises:
    - ValueError: If iterations is not a positive integer or if min_delay/max_delay is not a positive floating point value.

    Requirements:
    - time
    - random
    
    Example:
    >>> messages, delay = _solve_a_impl(2, 0.4, seed=1)
    >>> print(messages)
    ['0.61 seconds have passed', '1.76 seconds have passed']
    >>> print(delay)
    2.3708767696794144

    >>> messages, delay = _solve_a_impl(2, 2.0, 4.2, seed=12)
    >>> print(messages)
    ['3.04 seconds have passed', '3.45 seconds have passed']
    >>> print(delay)
    6.490494998960768
    """
    random.seed(seed)

    # Input validation
    if not isinstance(iterations, int) or iterations <= 0:
        raise ValueError("iterations must be a positive integer.")
    if not isinstance(min_delay, (int, float)) or min_delay <= 0:
        raise ValueError("min_delay must be a positive floating point value.")
    if not isinstance(max_delay, (int, float)) or max_delay <= min_delay:
        raise ValueError("max_delay must be a floating point value larger than min_delay.")

    total_delay = 0
    messages = []

    for _ in range(iterations):
        delay = random.uniform(min_delay, max_delay)
        total_delay += delay
        time.sleep(delay)
        message_string = f'{delay:.2f} seconds have passed'
        messages.append(message_string)
    
    return messages, total_delay

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
        # Generate inputs for task_func
                iterations = fdp.ConsumeIntInRange(1, 3) # Limit iterations to a small number due to time.sleep performance

                # min_delay must be a positive float
                # max_delay must be a float strictly greater than min_delay
                # We generate two raw integer values (representing cents, e.g., 1 to 20 for 0.01s to 0.20s)
                # to ensure both positive values and then sort them to get min and max.
                raw_delay_1_cents = fdp.ConsumeIntInRange(1, 20) # Range 1-20 represents 0.01 to 0.20 seconds
                raw_delay_2_cents = fdp.ConsumeIntInRange(1, 20)

                # Convert to floats and ensure min_delay_val <= max_delay_val
                min_delay_val = min(raw_delay_1_cents, raw_delay_2_cents) / 100.0
                max_delay_val = max(raw_delay_1_cents, raw_delay_2_cents) / 100.0

                # If min_delay_val and max_delay_val are equal, increment max_delay_val
                # to strictly satisfy the 'max_delay > min_delay' condition.
                if min_delay_val >= max_delay_val:
                    max_delay_val = min_delay_val + 0.01 # Smallest possible increment to guarantee max_delay > min_delay

                # seed can be None or an integer/float. The examples use integers.
                # We'll use an integer seed as it's common for random.seed().
                seed_val = fdp.ConsumeIntInRange(0, 1000000)

                # Call the function under test with the generated inputs.
                # Note: The 'time.sleep' call inside task_func will make fuzzing slow.
                # This setup assumes the fuzzing framework handles it or the small ranges
                # are sufficient for coverage.
                out_a = solve_a(iterations=iterations, min_delay=min_delay_val, max_delay=max_delay_val, seed=seed_val)
                out_b = solve_b(iterations=iterations, min_delay=min_delay_val, max_delay=max_delay_val, seed=seed_val)
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
