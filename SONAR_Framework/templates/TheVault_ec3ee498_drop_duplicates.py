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


def _solve_a_impl(df, column_name):
    df = df._solve_a_impl(subset=['id'], keep='last')
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
        # Generate DataFrame 'df'
                num_rows = fdp.ConsumeIntInRange(1, 10)
                num_cols = fdp.ConsumeIntInRange(1, 5) # Ensure at least 1 column, max 5

                # Initialize column names, ensuring 'id' is present
                column_names = ['id']
                generated_col_names_set = {'id'} # Use a set to track unique names

                # Generate additional column names if num_cols > 1
                for i in range(num_cols - 1):
                    while True:
                        new_col_name = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))
                        if new_col_name and new_col_name not in generated_col_names_set: # Ensure non-empty and unique
                            column_names.append(new_col_name)
                            generated_col_names_set.add(new_col_name)
                            break

                data_dict = {}
                for col_name in column_names:
                    if col_name == 'id':
                        # Generate 'id' column with a small range to encourage duplicates
                        data_dict[col_name] = [fdp.ConsumeIntInRange(0, 5) for _ in range(num_rows)]
                    else:
                        # Generate other columns with a mix of integer and string data
                        if fdp.ConsumeBool(): # Randomly choose data type
                            data_dict[col_name] = [fdp.ConsumeIntInRange(-1000, 1000) for _ in range(num_rows)]
                        else:
                            data_dict[col_name] = [''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10))) for _ in range(num_rows)]

                df = pd.DataFrame(data_dict)

                # Generate 'column_name'
                # The description implies it should be one of the DataFrame's columns.
                # The function under test hardcodes 'id', but for comparison with solve_b,
                # it's best to pick an actual column name from the generated df.
                column_name = fdp.PickValueInList(column_names)

                # Call the functions under test with a copy of the DataFrame to prevent side-effects
                out_a = solve_a(df.copy(), column_name)
                out_b = solve_b(df.copy(), column_name)
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
