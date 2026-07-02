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


def _solve_a_impl(tag_version: object) -> object:
    valid_tag_name = False
    while not valid_tag_name:
        new_tag_name = input(f"Tag name [{tag_version.tag_format()}]: ").strip()
        if len(new_tag_name) > 0:
            if tag_version.set_version_from_tag_name(new_tag_name):
                valid_tag_name = True
            else:
                print("Invalid tag name. Must follow 'REL_YYYY.MM.DD.B' format")
        else:
            valid_tag_name = True
    return tag_version

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
        # Generate fuzzed data for the mock objects and input replacement.
                # 1. Fuzzed string for tag_version.tag_format()
                tag_format_str_fuzzed = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))

                # 2. List of fuzzed strings for input() responses.
                # The loop in _request_tag_name can run multiple times. Limit the number of attempts
                # to ensure the fuzzer does not run indefinitely.
                num_input_attempts = fdp.ConsumeIntInRange(1, 10)
                fuzzed_input_responses = [
                    ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))
                    for _ in range(num_input_attempts)
                ]

                # 3. List of fuzzed booleans for tag_version.set_version_from_tag_name() return values.
                # This determines if the mock validation passes or fails for each non-empty input.
                fuzzed_set_version_returns = [
                    fdp.ConsumeBool()
                    for _ in range(num_input_attempts) # Provide a boolean for each potential call
                ]

                # Call the solve_a and solve_b wrappers.
                # It is assumed that `solve_a` and `solve_b` are pre-defined wrapper functions
                # that correctly mock `builtins.input` and the `tag_version` object's methods,
                # ensuring isolation and restoration of `builtins.input` after each call.
                # These wrappers should pass *copies* of the lists to their internal mocks
                # to guarantee identical argument consumption.
                # The wrappers should return the final accepted tag name (or None if no tag was accepted).
                out_a = solve_a(tag_format_str_fuzzed, fuzzed_input_responses, fuzzed_set_version_returns)
                out_b = solve_b(tag_format_str_fuzzed, fuzzed_input_responses, fuzzed_set_version_returns)
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
