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


def _solve_a_impl(path):
        if isinstance(path, (str, bytes)):
            return path
        path_type = type(path)
        try:
            path = path_type.__fspath__(path)
        except AttributeError:
            if hasattr(path_type, "__fspath__"):
                raise
        else:
            if isinstance(path, (str, bytes)):
                return path
            else:
                raise TypeError(
                    "expected __fspath__() to return str or bytes, "
                    "not " + type(path).__name__
                )
        raise TypeError(
            "expected str, bytes or os.PathLike object, not "
            + path_type.__name__
        )

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
        # Helper classes for fuzzing os.PathLike objects.
        # In a real Atheris script, these would typically be defined outside TestOneInput,
        # usually at the top level of the fuzzing script.
        class PathLikeObject:
            """A custom object that implements the __fspath__ method."""
            def __init__(self, fspath_return_value):
                self._fspath_return_value = fspath_return_value

            def __fspath__(self):
                return self._fspath_return_value

        class PathLikeRaisesAttributeError:
            """A custom object whose __fspath__ method raises AttributeError."""
            def __fspath__(self):
                raise AttributeError("Simulated AttributeError from __fspath__")

        # Choose the main category of input for the 'path' argument
        category_choice = fdp.PickValueInList([0, 1, 2, 3])
        # 0: str
        # 1: bytes
        # 2: os.PathLike object (i.e., an object with a __fspath__ method)
        # 3: Other types (objects without a __fspath__ method)

        path = None

        if category_choice == 0:  # str input
            path = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))
        elif category_choice == 1:  # bytes input
            path = fdp.ConsumeBytes(fdp.ConsumeIntInRange(0, 100))
        elif category_choice == 2:  # os.PathLike object
            # Further choose the behavior of the __fspath__ method for the PathLike object
            pathlike_behavior_choice = fdp.PickValueInList([0, 1, 2])
            # 0: __fspath__ returns str or bytes (valid return type)
            # 1: __fspath__ returns a non-str/bytes type (invalid return type)
            # 2: __fspath__ raises an AttributeError

            if pathlike_behavior_choice == 0:  # Valid __fspath__ return
                fspath_inner_return_type = fdp.PickValueInList([0, 1])  # 0: str, 1: bytes
                if fspath_inner_return_type == 0:  # __fspath__ returns str
                    fspath_return_value = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))
                else:  # __fspath__ returns bytes
                    fspath_return_value = fdp.ConsumeBytes(fdp.ConsumeIntInRange(0, 100))
                path = PathLikeObject(fspath_return_value)
            elif pathlike_behavior_choice == 1:  # Invalid __fspath__ return (non-str/bytes)
                invalid_return_type_choice = fdp.PickValueInList([0, 1, 2, 3, 4, 5])
                if invalid_return_type_choice == 0:  # int
                    fspath_return_value = fdp.ConsumeInt(4)
                elif invalid_return_type_choice == 1:  # float
                    fspath_return_value = fdp.ConsumeFloat()
                elif invalid_return_type_choice == 2:  # list
                    list_len = fdp.ConsumeIntInRange(0, 5)
                    fspath_return_value = [fdp.ConsumeInt(4) for _ in range(list_len)]
                elif invalid_return_type_choice == 3:  # tuple
                    tuple_len = fdp.ConsumeIntInRange(0, 5)
                    fspath_return_value = tuple(fdp.ConsumeInt(4) for _ in range(tuple_len))
                elif invalid_return_type_choice == 4:  # bool
                    fspath_return_value = fdp.ConsumeBool()
                else:  # object (plain instance)
                    fspath_return_value = object()
                path = PathLikeObject(fspath_return_value)
            else:  # __fspath__ raises AttributeError
                path = PathLikeRaisesAttributeError()
        else:  # category_choice == 3: Other types (no __fspath__ method)
            # These types should trigger the final TypeError in the fspath function
            other_type_choice = fdp.PickValueInList([0, 1, 2, 3, 4, 5, 6])
            if other_type_choice == 0:  # int
                path = fdp.ConsumeInt(8)
            elif other_type_choice == 1:  # float
                path = fdp.ConsumeFloat()
            elif other_type_choice == 2:  # list
                list_len = fdp.ConsumeIntInRange(0, 5)
                path = [fdp.ConsumeInt(4) for _ in range(list_len)]
            elif other_type_choice == 3:  # dict
                dict_len = fdp.ConsumeIntInRange(0, 3)
                path = {''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10))): fdp.ConsumeInt(4) for _ in range(dict_len)}
            elif other_type_choice == 4:  # bool
                path = fdp.ConsumeBool()
            elif other_type_choice == 5:  # complex
                path = complex(fdp.ConsumeFloat(), fdp.ConsumeFloat())
            else:  # NoneType
                path = None

        # Call the functions under test with the generated path argument
        out_a = solve_a(path)
        out_b = solve_b(path)
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
