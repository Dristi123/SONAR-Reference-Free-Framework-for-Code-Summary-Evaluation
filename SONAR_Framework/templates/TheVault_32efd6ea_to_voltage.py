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


def _solve_a_impl(_, int_value, gain, vref, bipolar, scale):
        voltage = float(int_value)
        if bipolar:
            voltage -= float(1)
            voltage /= float(0x7FFFFF)
        else:
            voltage /= float(0xFFFFFF)
        voltage *= float(vref)
        voltage /= float(gain)
        voltage *= float(scale)
        return voltage

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
        # Generate inputs
                # The first argument `_` is not used in the function, so we can pass None.
                arg__ = None

                # int_value: "integer value". The divisors (0x7FFFFF, 0xFFFFFF) suggest a 24-bit ADC context.
                # Let's use a range that covers signed and unsigned 24-bit values, plus some buffer.
                # 2^24 is 16,777,216.
                arg_int_value = fdp.ConsumeIntInRange(-(2**24), 2**24)

                # gain: float, used as a divisor. Must not be zero.
                # Follow float rule, but ensure non-zero.
                gain_raw_int = fdp.ConsumeIntInRange(-10000, 10000)
                if gain_raw_int == 0:
                    gain_raw_int = 1  # Avoid division by zero, pick an arbitrary non-zero
                arg_gain = float(gain_raw_int) / 100.0

                # vref: float, reference voltage. Can be zero, positive, or negative.
                arg_vref = float(fdp.ConsumeIntInRange(-10000, 10000)) / 100.0

                # bipolar: boolean.
                arg_bipolar = fdp.ConsumeBool()

                # scale: float, scale factor. Can be zero, positive, or negative.
                arg_scale = float(fdp.ConsumeIntInRange(-10000, 10000)) / 100.0

                # Call both implementations with identical arguments
                out_a = solve_a(arg__, arg_int_value, arg_gain, arg_vref, arg_bipolar, arg_scale)
                out_b = solve_b(arg__, arg_int_value, arg_gain, arg_vref, arg_bipolar, arg_scale)
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
