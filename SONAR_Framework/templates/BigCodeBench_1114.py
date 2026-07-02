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


from collections import defaultdict
from random import randint

def _solve_a_impl(dict1):
    """
    Create a dictionary of employee data for departments starting with 'EMP$$'. 
    The keys are department codes and the values are lists of the salaries of employees in that department.
    
    Parameters:
    dict1 (dict): A dictionary with department codes as keys and number of employees as values.
    
    Returns:
    dict: A dictionary with department codes starting with 'EMP$$' as keys and lists of employee salaries as values.
    
    Requirements:
    - collections
    - random
    
    Example:
    >>> import random
    >>> random.seed(0)
    >>> d = {'EMP$$1': 10, 'MAN$$1': 5, 'EMP$$2': 8, 'HR$$1': 7}
    >>> emp_data = _solve_a_impl(d)
    >>> print(emp_data.keys())
    dict_keys(['EMP$$1', 'EMP$$2'])
    """
    employee_data = defaultdict(list)
    
    for prefix, num_employees in dict1.items():
        if not prefix.startswith('EMP$$'):
            continue

        salaries = [randint(1, 100) for _ in range(num_employees)]
        employee_data[prefix].extend(salaries)

    return dict(employee_data)

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
        # Generate dict1
                dict1_len = fdp.ConsumeIntInRange(1, 10) # Number of departments
                dict1 = {}
                for _ in range(dict1_len):
                    key_len = fdp.ConsumeIntInRange(1, 20) # Length of department code string
                    if fdp.ConsumeBool():
                        suffix = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(0, 5)))
                        key = 'EMP$$' + suffix
                    else:
                        key = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))
                    value = fdp.ConsumeIntInRange(1, 100) # Number of employees (must be positive for randint to generate salaries)
                    dict1[key] = value

                # Call solve_a and solve_b with the generated input
                import random
                random.seed(42)
                out_a = solve_a(dict1)

                random.seed(42)
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
