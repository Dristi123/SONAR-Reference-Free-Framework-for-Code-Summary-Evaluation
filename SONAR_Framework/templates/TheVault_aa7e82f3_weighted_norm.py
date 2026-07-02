import atheris
import sys
import random
from typing import List, Tuple, Dict, Optional, Any, Set
from collections import defaultdict, Counter, OrderedDict
from itertools import combinations, permutations, product
from functools import reduce
import math, re, hashlib, copy, string
import torch
total = 0
matches = 0
_discarded = 0
MAX_CASES = 1000
_attempts = 0
MAX_ATTEMPTS = MAX_CASES * 5


def _solve_a_impl(input, Re):
    Re = Re.to(input.device)
    return torch.matmul(torch.matmul(input.transpose(1, 2), Re), input).squeeze()

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
        import torch

        # Generate dimensions for the input tensor
        # B: batch size
        # N: vector dimension
        B = fdp.ConsumeIntInRange(1, 5)  # Small batch size for fuzzing efficiency
        N = fdp.ConsumeIntInRange(1, 10) # Small vector dimension

        # Generate elements for the 'input' tensor (B, N, 1)
        # Elements are floats derived from integers to ensure reasonable values
        input_elements = [fdp.ConsumeIntInRange(-10000, 10000) / 100.0 for _ in range(B * N * 1)]
        input_tensor = torch.tensor(input_elements, dtype=torch.float32).reshape(B, N, 1)

        # Generate elements for the 'Re' tensor (N, N)
        # 'Re' is the weighting matrix, its dimensions are determined by 'N'
        re_elements = [fdp.ConsumeIntInRange(-10000, 10000) / 100.0 for _ in range(N * N)]
        Re_tensor = torch.tensor(re_elements, dtype=torch.float32).reshape(N, N)

        # Call the functions under test with the generated inputs
        out_a = solve_a(input_tensor, Re_tensor)
        out_b = solve_b(input_tensor, Re_tensor)
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
