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


def _solve_a_impl(command):
    gate_args = []
    gate_regs = []
    tokens = command[1:]
    reg_start = 0
    if "(" in tokens and ")" in tokens:
        bopen = tokens.index("(")
        bclose = tokens.index(")")
        gate_args = tokens[bopen+1:bclose]
        reg_start = bclose+1
    gate_regs = tokens[reg_start:]
    return gate_args, gate_regs

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
        # Generate the 'command' argument for _gate_processor.
        # 'command' is expected to be a list of strings.
        # The first element command[0] is ignored by the function, but the list must contain at least one element.
        # The remaining elements (tokens) can be '(', ')', or generic strings.

        # Determine the length of the command list. It must be at least 1.
        command_length = fdp.ConsumeIntInRange(1, 20) # A reasonable range for list length

        command = []
        for i in range(command_length):
            # For each element in the command list, decide its content.
            # It can be a literal '(', a literal ')', or a generic token string.
            # Use fdp.PickValueInList to choose the type of token for this position.
            token_choice = fdp.PickValueInList(["paren_open", "paren_close", "generic_string"])

            if token_choice == "paren_open":
                command.append("(")
            elif token_choice == "paren_close":
                command.append(")")
            else: # generic_string
                # Generate a generic Unicode string for this token.
                # The length of the generic string should also be fuzzed.
                string_len = fdp.ConsumeIntInRange(1, 10) # A reasonable range for individual token string length
                command.append(''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10))))

        # Call the function under test with the generated 'command'.
        out_a = solve_a(command)
        out_b = solve_b(command)
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
