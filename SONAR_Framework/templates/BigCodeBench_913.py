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


from typing import List, Union
import numpy as np
import scipy.fft

def _solve_a_impl(data: List[Union[int, str]], repetitions: int = 1):
    """
    Calculates the mode(s), their count(s), and the fast fourier transform of the data after repeating it a specified number of times.
    in a list of elements that can be repeated a specified number of times.
    
    Note:
    If the data is empty or the number of repetitions is less than or equal to 0, the function will return empty arrays.
    
    Parameters:
    - data (List[Union[int, str]]): The original list of elements (integers and/or strings).
    - repetitions (int, optional): The number of times to repeat the original list before calculating the mode. Defaults to 1.

    Requirements:
    - numpy
    - scipy
    
    Returns:
    - dict: A dictionary with two keys:
        'mode': a numpy array of the mode(s), sorted in ascending order.
        'count': a numpy array of the count(s) of the mode(s).
        
    Examples:
    >>> _solve_a_impl([1, '2', '2'], repetitions=1)
    {'mode': array(['2'], dtype='<U1'), 'count': [2], 'fft': array([ 5.-0.j, -1.+0.j, -1.-0.j])}
    """
    
    def calculate_mode(data):
        # Use a dictionary to count occurrences, considering both value and type
        counts = {}
        for item in data:
            key = (item, type(item))  # Distinguish between types
            counts[key] = counts.get(key, 0) + 1

        # Find the maximum count and corresponding values
        max_count = max(counts.values())
        mode_items = [value for (value, value_type), count in counts.items() if count == max_count]

        return mode_items, [max_count] * len(mode_items)
    
    if not data or repetitions <= 0:  # Handle empty data or no repetitions
        return {'mode': np.array([], dtype='object'), 'count': np.array([], dtype=int), 'fft': np.array([])}

    # Repeat the data
    repeated_data = data * repetitions

    # Calculate mode
    mode, count = calculate_mode(repeated_data)
    # using scipy.stats to calculate fft
    return {'mode': np.sort(mode), 'count': count, 'fft': scipy.fft.fft(data)}

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
        # Generate 'data' (List[Union[int, str]])
                # The Note mentions that data can be empty, so list length can be 0.
                data_length = fdp.ConsumeIntInRange(0, 10) # Max list length 10
                data_list = []
                for _ in range(data_length):
                    if fdp.ConsumeBool(): # Decide if the element is an int or a string
                        # Generate an integer
                        data_list.append(fdp.ConsumeIntInRange(-1000, 1000))
                    else:
                        # Generate a string. Per the rules, use ConsumeUnicodeNoSurrogates for general strings.
                        # The function signature allows any string, even if scipy.fft.fft might struggle with non-numeric ones.
                        data_list.append(''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10))))

                # Generate 'repetitions' (int)
                # The Note states the function handles repetitions <= 0, so include negative and zero values in the range.
                repetitions = fdp.ConsumeIntInRange(-5, 10) # A reasonable range for repetitions

                # Call the functions with the generated arguments
                out_a = solve_a(data_list, repetitions)
                out_b = solve_b(data_list, repetitions)
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
