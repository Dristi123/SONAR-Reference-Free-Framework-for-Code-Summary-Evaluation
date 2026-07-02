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


import pandas as pd
from scipy.stats import pearsonr


def _solve_a_impl(data):
    """
    Calculates the Pearson correlation coefficient between numerical scores and categorical grades.

    This function performs three main tasks:
    1. Converts scores from string format to floats.
    2. Encodes categorical grades into numerical values based on their rank order.
    3. Computes the Pearson correlation coefficient between the numerical scores and the encoded grades.

    Parameters:
    - data (dict): A dictionary containing two keys:
                 - 'Score_String': A list of scores in string format.
                 - 'Grade': A list of corresponding grades in string format.
                 Each list under these keys must have the same length.

    Returns:
    - correlation (float): The Pearson correlation coefficient between the converted numerical scores and encoded grades.
           Returns NaN if the input data frame has less than 2 rows, as the correlation coefficient cannot be calculated in this case.

    Requirements:
    - pandas
    - scipy

    Example:
    >>> round(_solve_a_impl({'Score_String': ['80.5', '85.7', '90.2'], 'Grade': ['B', 'B+', 'A-']}),2)
    -0.46
    """
    df = pd.DataFrame(data)
    if len(df) < 2:  # Check if the data frame has less than 2 rows
        return float("nan")  # or return None

    df["Score_Float"] = df["Score_String"].astype(float)
    df["Grade_Encoded"] = df["Grade"].astype("category").cat.codes
    correlation = pearsonr(df["Score_Float"], df["Grade_Encoded"])[0]
    return correlation

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
      
            data_dict = {}

                    # Determine the length of the lists. The function handles less than 2 rows.
                    # Let's allow for 0 to 10 elements.
            list_len = fdp.ConsumeIntInRange(0, 10)

            score_strings = []
            for _ in range(list_len):
                # Generate a float score and convert it to string
                score_float = fdp.ConsumeIntInRange(0, 10000) / 100.0 # Scores typically 0-100
                score_strings.append(str(score_float))

            grade_strings = []
            # Define a common set of possible grades
            # The specific grades don't matter as much as them being categorical strings
            # and being consistent for both implementations.
            possible_grades = ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F']
            for _ in range(list_len):
                # Pick a grade string from the list of possible grades
                grade_strings.append(fdp.PickValueInList(possible_grades))

            data_dict['Score_String'] = score_strings
            data_dict['Grade'] = grade_strings

            out_a = solve_a(data_dict)
            out_b = solve_b(data_dict) # Call with identical arguments
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
