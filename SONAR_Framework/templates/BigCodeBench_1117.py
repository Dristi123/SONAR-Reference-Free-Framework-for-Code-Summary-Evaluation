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
import json

# Constants
PREFICES = ['EMP$$', 'MAN$$', 'DEV$$', 'HR$$']
LEVELS = ['Junior', 'Mid', 'Senior']

def _solve_a_impl(department_data):
    """
    Generate a JSON object from employee data based on given department codes and their employee counts.

    Note:
    - The keys are department codes (from the list: ['EMP$$', 'MAN$$', 'DEV$$', 'HR$$']) and the values are lists of 
    employee levels ('Junior', 'Mid', 'Senior') in that department.

    Parameters:
    department_data (dict): A dictionary with department codes as keys and number of employees as values.

    Returns:
    str: A JSON object representing employee levels for each department.

    Requirements:
    - collections
    - random
    - json

    Example:
    >>> random.seed(0)
    >>> department_info = {'EMP$$': 10, 'MAN$$': 5, 'DEV$$': 8, 'HR$$': 7}
    >>> level_data_json = _solve_a_impl(department_info)
    >>> print(level_data_json)
    {"EMP$$": ["Mid", "Mid", "Junior", "Mid", "Senior", "Mid", "Mid", "Mid", "Mid", "Mid"], "MAN$$": ["Senior", "Junior", "Senior", "Junior", "Mid"], "DEV$$": ["Junior", "Junior", "Senior", "Mid", "Senior", "Senior", "Senior", "Junior"], "HR$$": ["Mid", "Junior", "Senior", "Junior", "Senior", "Mid", "Mid"]}
    """
    level_data = collections.defaultdict(list)
    
    for prefix, num_employees in department_data.items():
        if prefix not in PREFICES:
            continue

        for _ in range(num_employees):
            level = random.choice(LEVELS)
            level_data[prefix].append(level)

    return json.dumps(level_data)

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
        # Initialize department_data dictionary
        department_data = {}

        # Iterate over each possible prefix defined in PREFICES
        for prefix in PREFICES:
            # Use fdp.ConsumeBool() to randomly decide whether to include this prefix
            # as a key in the department_data dictionary.
            if fdp.ConsumeBool():
                # If included, generate a random number of employees for this department.
                # The example shows employee counts like 10, 5, 8, 7.
                # A reasonable range for fuzzing would be 0 (empty department) to a moderate number like 20.
                # 0 is valid as range(0) correctly results in no employees being added.
                num_employees = fdp.ConsumeIntInRange(0, 20)
                department_data[prefix] = num_employees

        # The task_func uses random.choice internally, so we need to set a fixed seed
        # immediately before calling both solve_a and solve_b to ensure consistent
        # pseudo-random sequences for deterministic comparison.
        random.seed(42)
        out_a = solve_a(department_data)
        random.seed(42)
        out_b = solve_b(department_data)
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
