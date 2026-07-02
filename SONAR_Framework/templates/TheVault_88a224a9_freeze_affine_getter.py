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


def _solve_a_impl(getter, *args, **kwargs):
    name = args[0] if len(args) else kwargs.get("name")  
    if name.endswith("/gamma") or name.endswith("/beta"):
        kwargs["trainable"] = False
        ret = getter(*args, **kwargs)
        tf.add_to_collection(tf.GraphKeys.MODEL_VARIABLES, ret)  
    else:
        ret = getter(*args, **kwargs)
    return ret

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
        # Generate the return value for the mock getter.
                # This needs to be generated ONCE per TestOneInput call, so both `solve_a` and `solve_b`
                # receive a getter that returns the same pre-fuzzed value for deterministic comparison.
                getter_return_value = fdp.ConsumeInt(4) # A fuzzed integer of 4 bytes

                # Define the mock getter function.
                def mock_getter(*g_args, **g_kwargs):
                    return getter_return_value

                # Generate components for the 'name' argument
                # Base name will be at least 1 character long.
                base_name = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))
                # Decide if the name should end with '/gamma', '/beta', or something else.
                # Including an empty string and an 'other_suffix' to cover all branches.
                suffix_choice = fdp.PickValueInList(['', '/gamma', '/beta', '/other_suffix'])
                final_name = base_name + suffix_choice

                # Decide whether 'name' is passed as the first positional argument or as a keyword argument.
                pass_name_via_args = fdp.ConsumeBool()

                # Build the *args and **kwargs for freeze_affine_getter.
                fag_args = []
                fag_kwargs = {}

                if pass_name_via_args:
                    fag_args.append(final_name)
                else:
                    # If not passed via args, ensure it's passed via kwargs to avoid `name` being None.
                    fag_kwargs["name"] = final_name

                # Add other arbitrary positional arguments for the `getter` function (passed through freeze_affine_getter)
                num_other_args = fdp.ConsumeIntInRange(0, 3)
                for _ in range(num_other_args):
                    fag_args.append(fdp.ConsumeInt(4)) # Add fuzzed integer arguments

                # Add other arbitrary keyword arguments for the `getter` function (passed through freeze_affine_getter)
                num_other_kwargs = fdp.ConsumeIntInRange(0, 3)
                for _ in range(num_other_kwargs):
                    # Generate a unique keyword name to avoid accidental clashes with "name" or "trainable"
                    # unless specifically intended for the fuzzer to explore overwrites.
                    kw_name_base = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))
                    # Prepend a distinct prefix to avoid clashes with "name" or "trainable" keys,
                    # ensuring they are considered "other" kwargs passed to the getter.
                    kw_name = f"arg_{kw_name_base}" 
                    kw_value = fdp.ConsumeInt(4)
                    fag_kwargs[kw_name] = kw_value

                # Decide if the 'trainable' kwarg is initially present in kwargs before freeze_affine_getter potentially modifies it.
                add_initial_trainable_kwarg = fdp.ConsumeBool()
                if add_initial_trainable_kwarg:
                    fag_kwargs["trainable"] = fdp.ConsumeBool() # Initial value can be True or False

                # Convert the list of args to a tuple for *args unpacking.
                fag_args_tuple = tuple(fag_args)

                # Call freeze_affine_getter for both solve_a and solve_b.
                # Ensure identical initial states for mutable arguments (kwargs) by using a deep copy.
                # The 'tf' object is assumed to be globally available or mocked externally if needed.

                fag_kwargs_copy_a = copy.deepcopy(fag_kwargs)
                out_a = solve_a(mock_getter, *fag_args_tuple, **fag_kwargs_copy_a)

                fag_kwargs_copy_b = copy.deepcopy(fag_kwargs)
                out_b = solve_b(mock_getter, *fag_args_tuple, **fag_kwargs_copy_b)
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
