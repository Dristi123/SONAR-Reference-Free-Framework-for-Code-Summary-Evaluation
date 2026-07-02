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


def _solve_a_impl(df, col):
    df.replace({col:{'alpha': 1, 'beta': 2, 'gamma': 3, 'delta': 4}}, inplace = True)
    return df

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
        import pandas as pd

        # Generate the column name 'col'
        # The problem description implies 'col' is a specific column in the DataFrame.
        # We'll generate a random but valid column name.
        col_name_length = fdp.ConsumeIntInRange(1, 100)
        col = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))

        # Generate the number of rows for the DataFrame
        num_rows = fdp.ConsumeIntInRange(1, 10) # Keep the number of rows relatively small for efficiency

        data_dict = {}
        column_names = set() # To keep track of generated column names and avoid accidental duplicates

        # Add the target column specified by 'col' with VOC names
        # The 'voc_choices' are derived directly from the 'replace' dictionary in the function.
        voc_choices = ['alpha', 'beta', 'gamma', 'delta']
        data_dict[col] = [fdp.PickValueInList(voc_choices) for _ in range(num_rows)]
        column_names.add(col)

        # Add other random columns to the DataFrame (optional)
        num_additional_cols = fdp.ConsumeIntInRange(0, 3) # Keep the number of additional columns small
        for i in range(num_additional_cols):
            other_col_name_length = fdp.ConsumeIntInRange(1, 100)
            other_col_name = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))

            # Ensure generated column names are unique within this DataFrame.
            # While pandas handles duplicate column names (e.g., by appending .1),
            # explicitly avoiding them simplifies the DataFrame structure for fuzzing.
            while other_col_name in column_names:
                other_col_name_length = fdp.ConsumeIntInRange(1, 100)
                other_col_name = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))

            column_names.add(other_col_name)
            # Fill other columns with random integers
            data_dict[other_col_name] = [fdp.ConsumeIntInRange(0, 100) for _ in range(num_rows)]

        # Create the pandas DataFrame
        df_original = pd.DataFrame(data_dict)

        # Call the function under test (solve_a and solve_b are aliases for map_voc_names).
        # Since map_voc_names modifies the DataFrame inplace, we must pass a copy
        # to each call to ensure they operate on identical initial states.
        out_a = solve_a(df_original.copy(), col)
        out_b = solve_b(df_original.copy(), col)
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
