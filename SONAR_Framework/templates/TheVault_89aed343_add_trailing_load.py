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


def _solve_a_impl(axle_spacing, axle_wt, space_to_trailing_load,
        distributed_load, span1_begin, span2_end, pt_load_spacing=0.5):
    mod_axle_spacing = axle_spacing[:]
    mod_axle_wt = axle_wt[:]
    if space_to_trailing_load < 0.0:
        raise ValueError("Must enter a positive float for space to trialing"
                            "load.")
    elif distributed_load < 0.0:
        raise ValueError("Must enter a positive float for distributed load.")
    elif pt_load_spacing <= 0.0:
        raise ValueError("Must enter a positive float (or nothing for default"
                            "value of 0.5) for the point load spacing.")
    elif distributed_load != 0.0 and space_to_trailing_load != 0.0:
        total_span_length = span2_end - span1_begin
        num_loads = int(total_span_length/pt_load_spacing)
        equivalent_pt_load = distributed_load*pt_load_spacing
        mod_axle_spacing.append(space_to_trailing_load)
        mod_axle_wt.append(equivalent_pt_load)
        for x in range(num_loads):
            mod_axle_spacing.append(pt_load_spacing)
            mod_axle_wt.append(equivalent_pt_load)
    return mod_axle_spacing, mod_axle_wt

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
        # Generate axle_spacing (list of floats)
                axle_spacing_len = fdp.ConsumeIntInRange(0, 10)
                axle_spacing = []
                for _ in range(axle_spacing_len):
                    axle_spacing.append(fdp.ConsumeIntInRange(-10000, 10000) / 100.0)

                # Generate axle_wt (list of floats)
                axle_wt_len = fdp.ConsumeIntInRange(0, 10)
                axle_wt = []
                for _ in range(axle_wt_len):
                    axle_wt.append(fdp.ConsumeIntInRange(-10000, 10000) / 100.0)

                # Generate space_to_trailing_load (float >= 0.0)
                # The ValueError is raised for < 0.0. So 0.0 and positive are allowed.
                space_to_trailing_load = fdp.ConsumeIntInRange(0, 10000) / 100.0

                # Generate distributed_load (float >= 0.0)
                # The ValueError is raised for < 0.0. So 0.0 and positive are allowed.
                distributed_load = fdp.ConsumeIntInRange(0, 10000) / 100.0

                # Generate span1_begin (float)
                span1_begin = fdp.ConsumeIntInRange(-10000, 10000) / 100.0

                # Generate span2_end (float)
                span2_end = fdp.ConsumeIntInRange(-10000, 10000) / 100.0

                # Generate pt_load_spacing (float > 0.0)
                # The ValueError is raised for <= 0.0. So it must be strictly positive.
                pt_load_spacing = fdp.ConsumeIntInRange(1, 10000) / 100.0 # Ensures > 0.0

                # Call the function with generated arguments
                out_a = solve_a(axle_spacing, axle_wt, space_to_trailing_load,
                                distributed_load, span1_begin, span2_end, pt_load_spacing)
                out_b = solve_b(axle_spacing, axle_wt, space_to_trailing_load,
                                distributed_load, span1_begin, span2_end, pt_load_spacing)
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
