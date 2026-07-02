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


import inspect
import types
import json

def _solve_a_impl(f):
    """
    Inspects the given function 'f' and returns its specifications as a JSON string. This includes
    the function's name, arguments, default values, annotations in a string format, and a boolean
    indicating if it's a lambda function.

    Parameters:
    f (function): The function to inspect.

    Returns:
    str: A JSON string containing the function's specifications.

    Requirements:
    - inspect
    - types
    - json

    Examples:
    >>> def sample_function(x, y=2): return x + y
    >>> 'sample_function' in _solve_a_impl(sample_function)
    True
    >>> def sample_function2(x, y=2): return x * y
    >>> 'sample_function2' in _solve_a_impl(sample_function2)
    True
    """
    spec = inspect.getfullargspec(f)
    annotations = {k: v.__name__ if isinstance(v, type) else str(v) for k, v in spec.annotations.items()}

    info = {
        'function_name': f.__name__,
        'args': spec.args,
        'defaults': spec.defaults,
        'annotations': annotations,
        'is_lambda': isinstance(f, types.LambdaType)
    }

    return json.dumps(info)

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
        # Define possible annotation types that are guaranteed to be in Python's global scope
            # or explicitly provided in the eval scope for generated lambda functions.
            annotation_types_str = ['int', 'str', 'float', 'bool', 'list', 'dict', 'set', 'tuple', 'object', 'NoneType']

            # eval_scope for `eval()` to resolve annotation types
            eval_scope = {
                'int': int, 'str': str, 'float': float, 'bool': bool,
                'list': list, 'dict': dict, 'set': set, 'tuple': tuple,
                'object': object, 'NoneType': type(None)
            }

            # Predefined 'def' functions to cover different signatures and ensure
            # both lambda and regular functions are fuzzed.
            # These are defined within the `try` block to adhere to the prompt's structure,
            # though typically they would be global for efficiency.
            def _fuzz_predefined_func_0():
                """A function with no arguments."""
                return 1

            def _fuzz_predefined_func_1(arg_x, arg_y: int = 10):
                """A function with positional and annotated default arguments."""
                return arg_x + arg_y

            def _fuzz_predefined_func_2(z: str, value=None):
                """A function with annotations and default None."""
                return z if value is None else str(value)

            def _fuzz_predefined_func_3(param_a: float):
                """A function with a single annotated argument."""
                return param_a * 2

            # List of predefined functions to pick from
            predefined_funcs = [
                _fuzz_predefined_func_0,
                _fuzz_predefined_func_1,
                _fuzz_predefined_func_2,
                _fuzz_predefined_func_3
            ]

            f_input = None

            # Decide whether to generate a lambda function or pick a predefined 'def' function.
            if fdp.ConsumeBool(): # True: generate a lambda, False: pick a predefined func
                # Logic for generating a lambda function string and evaluating it
                args_list = []
                arg_names_for_body = [] # To store just the names for use in the lambda body

                num_args = fdp.ConsumeIntInRange(0, 5) # Fuzz the number of arguments (0 to 5)

                for i in range(num_args):
                    arg_name_length = fdp.ConsumeIntInRange(1, 10)

                    # Generate a valid Python identifier for the argument name
                    first_char_options = [chr(ord('a') + j) for j in range(26)] + ['_']
                    first_char = fdp.PickValueInList(first_char_options)

                    other_char_options = first_char_options + [chr(ord('0') + j) for j in range(10)]

                    arg_name_chars = [first_char]
                    for _ in range(arg_name_length - 1):
                        arg_name_chars.append(fdp.PickValueInList(other_char_options))

                    arg_name = "".join(arg_name_chars)
                    arg_names_for_body.append(arg_name) # Store pure name for body creation

                    current_arg_parts = [arg_name]

                    # Decide if the argument has an annotation
                    if fdp.ConsumeBool():
                        annot_choice = fdp.PickValueInList(annotation_types_str)
                        current_arg_parts.append(f": {annot_choice}")

                    # Decide if the argument has a default value
                    if fdp.ConsumeBool():
                        # Default values need to be simple and representable in a string that `eval()` can parse
                        default_val_choice = fdp.ConsumeIntInRange(0, 3)
                        default_value_repr = None
                        if default_val_choice == 0: # Integer
                            default_value_repr = str(fdp.ConsumeIntInRange(-100, 100))
                        elif default_val_choice == 1: # String
                            str_len = fdp.ConsumeIntInRange(0, 10)
                            s_val = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))
                            default_value_repr = repr(s_val) # Use repr to handle quotes and escaping
                        elif default_val_choice == 2: # Boolean
                            default_value_repr = str(fdp.ConsumeBool())
                        else: # None
                            default_value_repr = "None"

                        current_arg_parts.append(f"={default_value_repr}")

                    args_list.append("".join(current_arg_parts))

                signature_str = ", ".join(args_list)

                # Fuzz the body of the lambda function. Keep it simple to avoid complex runtime errors,
                # focusing the fuzzing on the function's signature and metadata.
                body_str = ""
                body_choice = fdp.ConsumeIntInRange(0, 2)
                if body_choice == 0:
                    body_str = str(fdp.ConsumeIntInRange(-100, 100)) # Return a random integer
                elif body_choice == 1:
                    body_str = "None" # Return None
                else:
                    # If arguments exist, return the first one. Otherwise, return a constant.
                    if arg_names_for_body:
                        body_str = arg_names_for_body[0]
                    else:
                        body_str = "0" # Default body if no arguments

                lambda_code = f"lambda {signature_str}: {body_str}"

                try:
                    f_input = eval(lambda_code, eval_scope)
                except (SyntaxError, NameError, TypeError, ValueError):
                    # Fallback to a simple, valid lambda if the dynamically generated string is invalid.
                    f_input = lambda x: None # Ensures `task_func` always receives a valid function object

            else:
                # Pick one of the predefined 'def' functions for fuzzing
                f_input = fdp.PickValueInList(predefined_funcs)

            # Call the functions under test with the fuzzed input 'f_input'
            out_a = solve_a(f_input)
            out_b = solve_b(f_input)
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
