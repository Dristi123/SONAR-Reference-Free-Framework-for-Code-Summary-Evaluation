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


def _solve_a_impl(target, loss_function, loss_params) -> bool:
    if loss_params is None:
        metric = loss_function(target, target)
    else:
        try:
            metric = loss_function(target, target, **loss_params)
        except Exception:
            metric = 1
    if int(round(metric)) == 0:
        return False
    else:
        return True

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
        # Generate inputs for the _greater_is_better function

        # target: The type doesn't fundamentally change the logic of _greater_is_better,
        # as it's just passed to loss_function. A float is a good general numeric type.
        target = fdp.ConsumeIntInRange(-100000, 100000) / 100.0

        # loss_function: This is a callable. We need to control its behavior
        # (return value or raise exception) to fully test _greater_is_better's branches.
        # We'll create a closure that captures fuzzed values for its behavior.
        fuzzed_metric_return_value = fdp.ConsumeIntInRange(-100000, 100000) / 100.0
        should_loss_function_raise_exception = fdp.ConsumeBool()

        # Define the mock loss_function. It must accept two positional args and **kwargs.
        # It will either return a fuzzed float or raise an exception.
        def mock_loss_function(t1, t2, **kwargs):
            if should_loss_function_raise_exception:
                # We raise a generic Exception or specific one; here, RuntimeError.
                raise RuntimeError("Simulated exception from loss_function")
            return fuzzed_metric_return_value

        loss_function = mock_loss_function

        # loss_params: Can be None or a dictionary.
        use_loss_params_dict = fdp.ConsumeBool()
        if use_loss_params_dict:
            num_params = fdp.ConsumeIntInRange(0, 5) # Max 5 parameters in the dict for reasonable complexity
            loss_params = {}
            for _ in range(num_params):
                # Fuzz key (string)
                key_len = fdp.ConsumeIntInRange(1, 10)
                key = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))

                # Fuzz value type (int, float, or bool) and then the value itself
                value_type_choice = fdp.ConsumeIntInRange(0, 2) # 0: int, 1: float, 2: bool
                if value_type_choice == 0:
                    value = fdp.ConsumeIntInRange(-10000, 10000)
                elif value_type_choice == 1:
                    value = fdp.ConsumeIntInRange(-10000, 10000) / 100.0
                else: # value_type_choice == 2
                    value = fdp.ConsumeBool()

                loss_params[key] = value
        else:
            loss_params = None

        # Call the function under test.
        # Assuming _greater_is_better is the function being tested,
        # it replaces 'solve_a' and 'solve_b'.
        out_a = solve_a(target, loss_function, loss_params)
        out_b = solve_b(target, loss_function, loss_params)
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
