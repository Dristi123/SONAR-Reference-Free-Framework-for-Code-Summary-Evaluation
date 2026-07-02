import atheris
import sys
import random
from typing import List, Tuple, Dict, Optional, Any, Set
from collections import defaultdict, Counter, OrderedDict
from itertools import combinations, permutations, product
from functools import reduce
import math, re, hashlib, copy, string
import numpy as np
total = 0
matches = 0
_discarded = 0
MAX_CASES = 1000
_attempts = 0
MAX_ATTEMPTS = MAX_CASES * 5


def _solve_a_impl(Vj, Yij, Ui, reg, eta):
    first_term = reg * Vj
    second_term = np.multiply(Ui, (Yij - np.dot(Ui, Vj)))
    return eta * (first_term - second_term)

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
        # Ensure numpy is imported for array operations
                import numpy as np

                # Determine a common vector length for Vj and Ui
                # The description implies Vj and Ui are vectors, and they participate
                # in a dot product, so their lengths must match.
                vec_len = fdp.ConsumeIntInRange(1, 10) # Vector length between 1 and 10 elements

                # Generate Vj: a NumPy array of floats
                Vj_elements = []
                for _ in range(vec_len):
                    Vj_elements.append(fdp.ConsumeIntInRange(-10000, 10000) / 100.0)
                Vj = np.array(Vj_elements)

                # Generate Yij: a scalar float
                Yij = fdp.ConsumeIntInRange(-10000, 10000) / 100.0

                # Generate Ui: a NumPy array of floats, with the same length as Vj
                Ui_elements = []
                for _ in range(vec_len): # Use the same vec_len for Ui
                    Ui_elements.append(fdp.ConsumeIntInRange(-10000, 10000) / 100.0)
                Ui = np.array(Ui_elements)

                # Generate reg: a scalar float (regularization parameter)
                reg = fdp.ConsumeIntInRange(-10000, 10000) / 100.0

                # Generate eta: a scalar float (learning rate)
                eta = fdp.ConsumeIntInRange(-10000, 10000) / 100.0

                # Call the functions under test with the generated inputs
                out_a = solve_a(Vj, Yij, Ui, reg, eta)
                out_b = solve_b(Vj, Yij, Ui, reg, eta)
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
