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
from string import ascii_uppercase

def _solve_a_impl(dict1):
    """
    Assign each employee of a company a unique ID based on their department code, consisting of the department code, followed by a random string of 5 letters.

    Parameters:
    dict1 (dict): A dictionary with department codes as keys and number of employees 
                  as values.

    Returns:
    list: A list of unique employee IDs for all departments.

    Requirements:
    - random
    - string.ascii_uppercase

    Example:
    >>> random.seed(0)
    >>> d = {'EMP$$': 10, 'MAN$$': 5, 'DEV$$': 8, 'HR$$': 7}
    >>> emp_ids = _solve_a_impl(d)
    >>> print(emp_ids)
    ['EMP$$MYNBI', 'EMP$$QPMZJ', 'EMP$$PLSGQ', 'EMP$$EJEYD', 'EMP$$TZIRW', 'EMP$$ZTEJD', 'EMP$$XCVKP', 'EMP$$RDLNK', 'EMP$$TUGRP', 'EMP$$OQIBZ', 'MAN$$RACXM', 'MAN$$WZVUA', 'MAN$$TPKHX', 'MAN$$KWCGS', 'MAN$$HHZEZ', 'DEV$$ROCCK', 'DEV$$QPDJR', 'DEV$$JWDRK', 'DEV$$RGZTR', 'DEV$$SJOCT', 'DEV$$ZMKSH', 'DEV$$JFGFB', 'DEV$$TVIPC', 'HR$$CVYEE', 'HR$$BCWRV', 'HR$$MWQIQ', 'HR$$ZHGVS', 'HR$$NSIOP', 'HR$$VUWZL', 'HR$$CKTDP']
    """
    employee_ids = []
    
    for prefix, num_employees in dict1.items():
        for _ in range(num_employees):
            random_str = ''.join(random.choice(ascii_uppercase) for _ in range(5))
            employee_ids.append(f'{prefix}{random_str}')

    return employee_ids

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
        # Generate dict1 for task_func
                num_departments = fdp.ConsumeIntInRange(1, 5) # Number of department entries, e.g., 1 to 5 departments
                dict1 = {}
                for _ in range(num_departments):
                    # Generate department code (key)
                    # Example shows 'EMP$$', 'MAN$$' etc. - strings of varying characters.
                    # Using ConsumeUnicodeNoSurrogates for general string keys.
                    key_len = fdp.ConsumeIntInRange(1, 10) # Length of department code, e.g., 1 to 10 characters
                    key = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))

                    # Generate number of employees (value)
                    # Example shows positive integers like 10, 5, 8.
                    # Number of employees should be at least 1.
                    value = fdp.ConsumeIntInRange(1, 100) # Number of employees per department, e.g., 1 to 100

                    dict1[key] = value

                # Seed random for reproducible results between solve_a and solve_b
                random.seed(42)
                out_a = solve_a(dict1)

                random.seed(42) # Re-seed for solve_b to ensure identical random sequences
                out_b = solve_b(dict1)
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
