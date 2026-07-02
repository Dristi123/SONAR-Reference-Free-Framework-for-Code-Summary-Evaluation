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


def _solve_a_impl(df, column_name, exchange_rate): 
    df[column_name] = (df[column_name] * df[exchange_rate]).round(2)
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
        # Generate a pandas DataFrame
                num_rows = fdp.ConsumeIntInRange(1, 5)  # Number of rows in the DataFrame
                # Ensure at least two columns are created, so 'column_name' and 'exchange_rate' can be picked
                num_cols = fdp.ConsumeIntInRange(2, 5)  # Number of columns in the DataFrame

                # Generate unique column names
                # We use a set to ensure uniqueness for column names, then convert to list
                # as fdp.PickValueInList expects a list.
                generated_column_names = set()
                while len(generated_column_names) < num_cols:
                    generated_column_names.add(''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10))))
                column_names_list = list(generated_column_names)

                # Generate data for the DataFrame. All values are floats.
                data = {}
                for col_name in column_names_list:
                    data[col_name] = [fdp.ConsumeIntInRange(-10000, 10000) / 100.0 for _ in range(num_rows)]

                # Assume pandas is imported as pd in the global scope for the fuzzer environment
                import pandas as pd 
                df_input = pd.DataFrame(data)

                # Choose the column to convert and the exchange rate column from the generated column names
                column_to_convert = fdp.PickValueInList(column_names_list)
                exchange_rate_column = fdp.PickValueInList(column_names_list)

                # The function modifies the DataFrame in place, so pass copies to solve_a and solve_b
                df_for_a = df_input.copy()
                df_for_b = df_input.copy()

                out_a = solve_a(df_for_a, column_to_convert, exchange_rate_column)
                out_b = solve_b(df_for_b, column_to_convert, exchange_rate_column)
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
