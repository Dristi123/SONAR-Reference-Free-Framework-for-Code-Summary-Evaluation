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


def _solve_a_impl(Pt, xt, Pli, Ple, Pri, Pre, direction, span_begin, span_end):
    span_length = span_end - span_begin
    if direction == "ltr":
        Vi = abs(Pt*(xt-span_begin)/span_length - Pri)
        Ve = abs(Pt*(xt-span_begin)/span_length - Pre)
    elif direction == "rtl":
        Vi = abs(Pt*(span_end - xt)/span_length - Pli)
        Ve = abs(Pt*(span_end - xt)/span_length - Ple)
    return round(max(Vi,Ve),3)

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
        Pt = fdp.ConsumeIntInRange(-10000, 10000) / 100.0
        xt = fdp.ConsumeIntInRange(-10000, 10000) / 100.0
        Pli = fdp.ConsumeIntInRange(-10000, 10000) / 100.0
        Ple = fdp.ConsumeIntInRange(-10000, 10000) / 100.0
        Pri = fdp.ConsumeIntInRange(-10000, 10000) / 100.0
        Pre = fdp.ConsumeIntInRange(-10000, 10000) / 100.0
        direction = fdp.PickValueInList(["ltr", "rtl"])

        # Ensure span_length (span_end - span_begin) is not zero to prevent division by zero.
        # We'll make span_length strictly positive.
        span_begin = fdp.ConsumeIntInRange(-10000, 10000) / 100.0
        # Generate a positive span_length and add it to span_begin to get span_end.
        # Max 1000 / 100.0 = 10.0, Min 1 / 100.0 = 0.01
        span_length_val = fdp.ConsumeIntInRange(1, 1000) / 100.0
        span_end = span_begin + span_length_val

        out_a = solve_a(Pt, xt, Pli, Ple, Pri, Pre, direction, span_begin, span_end)
        out_b = solve_b(Pt, xt, Pli, Ple, Pri, Pre, direction, span_begin, span_end)
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
