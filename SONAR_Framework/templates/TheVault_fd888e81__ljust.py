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


def _solve_a_impl(input, width, fillchar=None):
    if fillchar is None:
        fillchar = ' '
    if isinstance(input, str):
        return input.ljust(width, fillchar)
    else:
        delta_len = width - len(input)
        if delta_len <= 0:
            return input
        else:
            return input + [fillchar for _ in range(delta_len)]

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
        # Determine the type of the 'input' argument: string or list of strings
                is_string_input = fdp.ConsumeBool()

                input_arg = None
                if is_string_input:
                    # Generate a string for 'input'
                    # Length can be 0 for empty strings, up to 100.
                    input_arg = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))
                else:
                    # Generate a list of strings for 'input'
                    # List length can be 0, up to 10 elements.
                    list_len = fdp.ConsumeIntInRange(0, 10)
                    input_arg = [
                        ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10))) # Each string element length 0-50
                        for _ in range(list_len)
                    ]

                # Generate 'width' argument
                # Width can be 0 or positive, up to 100.
                width = fdp.ConsumeIntInRange(0, 100)

                # Generate 'fillchar' argument, which can be None or a string
                fillchar_arg = None
                if fdp.ConsumeBool(): # 50% chance for fillchar to be None
                    fillchar_arg = None
                else:
                    if is_string_input:
                        # If 'input' is a string, 'fillchar' for str.ljust must be a single character.
                        fillchar_arg = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10))) # Ensure length 1
                    else:
                        # If 'input' is a list, 'fillchar' can be any string (it becomes a list element).
                        # Length can be 0 for an empty string as a fill element.
                        fillchar_arg = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))

                # Call the functions under test with the generated arguments
                out_a = solve_a(input_arg, width, fillchar_arg)
                out_b = solve_b(input_arg, width, fillchar_arg)
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
