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


def _solve_a_impl(X, N,D,K,sigma_X,sigma_A,Z):
    M = Z.T @ Z + (sigma_X**2/sigma_A**2)*np.eye(K)
    part1 = N*D/2 * np.log(2*np.pi) + (N - K)*D*np.log(sigma_X) + K*D*np.log(sigma_A)+D/2*np.log(np.linalg.det(M))
    part2_inside = np.eye(N) - (Z @ np.linalg.inv(M) @ Z.T)
    part2 = -1/(2 * sigma_X**2) * np.trace(X.T @ part2_inside @ X)
    return part2 - part1

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
        import numpy as np

        # Generate N, D, K for matrix dimensions.
        # Ranges are chosen to keep computation tractable for fuzzing,
        # and to avoid zero or excessively large dimensions which might cause issues.
        N = fdp.ConsumeIntInRange(1, 7) # Number of rows for X and Z
        D = fdp.ConsumeIntInRange(1, 7) # Number of columns for X
        K = fdp.ConsumeIntInRange(1, 5) # Number of columns for Z (and size of square matrix M)

        # Generate sigma_X and sigma_A.
        # These represent standard deviations, so they must be positive.
        # Using a range from 0.01 to 10.0 ensures positivity and avoids division by zero.
        sigma_X = fdp.ConsumeIntInRange(1, 1000) / 100.0
        sigma_A = fdp.ConsumeIntInRange(1, 1000) / 100.0

        # Generate X, the data matrix.
        # It has shape (N, D). Elements are floats.
        X_elements = [fdp.ConsumeIntInRange(-10000, 10000) / 100.0 for _ in range(N * D)]
        X = np.array(X_elements).reshape((N, D))

        # Generate Z, the binary matrix.
        # It has shape (N, K). Elements are 0 or 1.
        # fdp.ConsumeBool() generates True/False, which conveniently convert to 1/0 when used in a NumPy array.
        Z_elements = [fdp.ConsumeBool() for _ in range(N * K)]
        Z = np.array(Z_elements).reshape((N, K))

        # Call the function under test.
        # As per the problem description, 'solve_a' and 'solve_b' are placeholders
        # for the 'log_likelyhood' function in this context.
        out_a = solve_a(X, N, D, K, sigma_X, sigma_A, Z)
        out_b = solve_b(X, N, D, K, sigma_X, sigma_A, Z)
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
