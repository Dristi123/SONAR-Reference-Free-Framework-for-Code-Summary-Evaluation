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


def _solve_a_impl(size, offset, device=None):
    if type(size) != type(offset):
        raise ValueError(f"size and offset must have the same type: get {type(size)} and {type(offset)}.")
    if isinstance(size, tuple) and len(size) != len(offset):
        raise ValueError(f"size and offset must have the same length: get {len(size)} and {len(offset)}.")
    output = torch.zeros(size, device=device)
    output[offset] = 1.0
    return output

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
        is_tuple_type = fdp.ConsumeBool()

        if is_tuple_type:
            # Generate tuple inputs for size and offset
            # Number of dimensions for the tensor
            num_dims = fdp.ConsumeIntInRange(1, 4) 
            size_elements = []
            offset_elements = []
            for _ in range(num_dims):
                # Each dimension's size must be at least 1 for a valid tensor
                dim_size = fdp.ConsumeIntInRange(1, 10)
                # Offset for this dimension must be a valid index (0 to dim_size - 1)
                dim_offset = fdp.ConsumeIntInRange(0, dim_size - 1)
                size_elements.append(dim_size)
                offset_elements.append(dim_offset)
            size = tuple(size_elements)
            offset = tuple(offset_elements)
        else:
            # Generate int inputs for size and offset (1D case)
            # The size of the 1D tensor must be at least 1
            tensor_size = fdp.ConsumeIntInRange(1, 10)
            # Offset must be a valid index (0 to tensor_size - 1)
            offset = fdp.ConsumeIntInRange(0, tensor_size - 1)
            size = tensor_size

        # Call the functions with the generated arguments
        out_a = solve_a(size, offset)
        out_b = solve_b(size, offset)
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
