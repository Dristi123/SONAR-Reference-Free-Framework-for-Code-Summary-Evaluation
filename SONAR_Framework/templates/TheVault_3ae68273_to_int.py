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


def _solve_a_impl(s, fallback=0):
    try:
        result = int(s)
    except ValueError:
        result = fallback
    except TypeError:
        result = fallback
    return result

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
        # The function `to_int(s, fallback=0)` attempts to convert `s` to an integer.
                # The `try...except ValueError` and `try...except TypeError` blocks indicate
                # that `s` is expected to be a type that `int()` can process, which might
                # fail (`ValueError` for malformed strings) or not be directly convertible
                # (`TypeError` for types like None, list).
                # The natural language description "Try to cast an int to a string" is
                # inverted relative to the function's operation. We will derive the input
                # domain from the *code's behavior* and exception handling, which is a
                # stronger indicator for fuzzing than a potentially misleading description.

                # 's' can be a string, integer, float, None, or a list (to trigger TypeError)
                s_choice = fdp.ConsumeIntInRange(0, 4) # 0: str, 1: int, 2: float, 3: None, 4: list

                s = None
                if s_choice == 0:  # String input for 's'
                    # Rule: if function body checks specific characters, restrict to them.
                    # `int()` checks for digits '0'-'9' and optional '+' or '-' signs.
                    # Length between 1 and 100 to avoid empty strings, which are not
                    # explicitly mentioned in the description as an accepted input for fuzzing.
                    s = ''.join(fdp.PickValueInList(list('0123456789+-')) for _ in range(fdp.ConsumeIntInRange(1, 100)))
                elif s_choice == 1:  # Integer input for 's'
                    s = fdp.ConsumeInt(8) # 8-byte integer for a wide range
                elif s_choice == 2:  # Float input for 's'
                    s = fdp.ConsumeIntInRange(-10000, 10000) / 100.0
                elif s_choice == 3:  # NoneType input for 's' (causes TypeError)
                    s = None
                elif s_choice == 4:  # List input for 's' (causes TypeError)
                    list_len = fdp.ConsumeIntInRange(0, 5) # Keep lists simple
                    s = [fdp.ConsumeInt(2) for _ in range(list_len)]

                # 'fallback' is an integer
                fallback = fdp.ConsumeInt(4) # 4-byte integer

                out_a = solve_a(s, fallback)
                out_b = solve_b(s, fallback)
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
