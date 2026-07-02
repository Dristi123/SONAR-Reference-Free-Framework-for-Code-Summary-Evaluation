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


def _solve_a_impl(G):
    gamma = torch.atan2(G[..., 1, 2], G[..., 0, 2])
    sin = torch.sin(gamma)
    cos = torch.cos(gamma)
    beta = torch.atan2(cos * G[..., 0, 2] + sin * G[..., 1, 2], G[..., 2, 2])
    alpha = torch.atan2(-sin * G[..., 0, 0] + cos * G[..., 1, 0], -sin * G[..., 0, 1] + cos * G[..., 1, 1])
    return alpha, beta, gamma

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

        # Generate batch dimensions
        num_batch_dims = fdp.ConsumeIntInRange(0, 3) # Allow 0 to 3 batch dimensions
        batch_shape = []
        for _ in range(num_batch_dims):
            batch_shape.append(fdp.ConsumeIntInRange(1, 5)) # Each batch dim size between 1 and 5

        # Final shape will be batch_shape + (3, 3)
        tensor_shape = tuple(batch_shape + [3, 3])

        # Calculate total number of elements
        num_elements = 1
        for dim_size in tensor_shape:
            num_elements *= dim_size

        # Generate float values for the tensor elements
        tensor_elements = []
        for _ in range(num_elements):
            tensor_elements.append(fdp.ConsumeIntInRange(-10000, 10000) / 100.0)

        # Create the torch tensor
        # Convert to float32 for typical use in ML frameworks
        G = torch.tensor(tensor_elements, dtype=torch.float32).reshape(tensor_shape)

        # Call the functions under test
        # Assuming solve_a and solve_b are aliases for so3_element, or similar implementations
        out_a = solve_a(G)
        out_b = solve_b(G)
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
