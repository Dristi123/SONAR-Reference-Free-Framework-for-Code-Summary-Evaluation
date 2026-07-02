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


def _solve_a_impl(nsx_object, path):
    path_list = path.split("/")
    selected_obj = nsx_object
    for path in path_list[:-1]:
        if path not in selected_obj:
            selected_obj[path] = {}
        selected_obj = selected_obj[path]
    last_part = path_list[-1]
    if last_part not in selected_obj:
        selected_obj[last_part] = []
    if isinstance(selected_obj[last_part], dict):
        selected_obj[last_part] = [selected_obj[last_part]]
    return selected_obj[last_part]

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
        import copy

        # Helper for generating strings for dictionary keys and path components
        def _generate_key_string(fdp):
            # Consuming a string between 1 and 10 characters long for keys/path parts
            return ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))

        # Recursive helper to generate a complex nested dictionary/list structure for nsx_object
        def _generate_nsx_object_structure(fdp, current_depth):
            # Limit recursion depth to avoid excessively large or deeply nested objects
            if current_depth > 3:
                # At max depth, return a simple value (string, int, or bool)
                return fdp.PickValueInList([
                    _generate_key_string(fdp),
                    fdp.ConsumeIntInRange(-1000, 1000),
                    fdp.ConsumeBool()
                ])

            # Choose type for the current level from a predefined set
            choice = fdp.PickValueInList(['dict', 'list', 'string', 'int', 'bool'])

            if choice == 'dict':
                num_elements = fdp.ConsumeIntInRange(0, 5) # 0 to 5 key-value pairs
                obj = {}
                for _ in range(num_elements):
                    key = _generate_key_string(fdp)
                    obj[key] = _generate_nsx_object_structure(fdp, current_depth + 1)
                return obj
            elif choice == 'list':
                num_elements = fdp.ConsumeIntInRange(0, 5) # 0 to 5 elements
                obj = []
                for _ in range(num_elements):
                    obj.append(_generate_nsx_object_structure(fdp, current_depth + 1))
                return obj
            elif choice == 'string':
                return ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))
            elif choice == 'int':
                return fdp.ConsumeIntInRange(-1000, 1000)
            else: # 'bool'
                return fdp.ConsumeBool()

        # Generate the initial nsx_object, which can be an arbitrary nested structure
        initial_nsx_object = _generate_nsx_object_structure(fdp, 0)

        # Generate the path string
        # Determine the number of "logical" components (non-empty strings that would serve as keys)
        num_logical_path_components = fdp.ConsumeIntInRange(1, 5) 
        logical_path_parts = []
        for _ in range(num_logical_path_components):
            logical_path_parts.append(_generate_key_string(fdp))

        # Construct the actual path string, introducing potential empty components or leading/trailing slashes,
        # as `path.split("/")` handles these cases.
        path_segments = []

        # Optionally add a leading slash, which results in an empty string as the first path component
        if fdp.ConsumeBool():
            path_segments.append('')

        # Add logical parts and occasionally an empty segment between them (e.g., "a//b")
        for i, part in enumerate(logical_path_parts):
            path_segments.append(part)
            # Optionally insert an empty string as a segment between parts
            if i < num_logical_path_components - 1 and fdp.ConsumeBool():
                path_segments.append('')

        # Optionally add a trailing slash, which results in an empty string as the last path component
        if fdp.ConsumeBool():
            path_segments.append('')

        # Join the segments to form the final path string.
        # Since `num_logical_path_components` is at least 1 and `_generate_key_string` produces
        # non-empty strings, `logical_path_parts` will always contain at least one non-empty string.
        # This ensures that `path_segments` will result in a non-empty `path` string.
        path = "/".join(path_segments)

        # Create deep copies of the initial nsx_object for both function calls.
        # This is crucial because `nsx_struct_get_list` modifies the `nsx_object` argument in place.
        nsx_object_a = copy.deepcopy(initial_nsx_object)
        nsx_object_b = copy.deepcopy(initial_nsx_object)

        # Call the functions under test with identical arguments
        out_a = solve_a(nsx_object_a, path)
        out_b = solve_b(nsx_object_b, path)
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
