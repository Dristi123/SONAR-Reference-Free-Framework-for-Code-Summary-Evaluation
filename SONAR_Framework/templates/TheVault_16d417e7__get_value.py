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


def _solve_a_impl(data, tag):
    if len(tag) < 4:
        tag = "v" + tag[1:].zfill(3)
    try:
        return data[tag][0]['_']
    except (KeyError, IndexError):
        return None

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
        # Generate 'original_tag' for the function call.
        # Length is chosen to cover cases where len(tag) < 4 and len(tag) >= 4.
        original_tag_length = fdp.ConsumeIntInRange(1, 10)
        original_tag = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))

        # Initialize the 'data' dictionary.
        data = {}

        # Replicate the internal logic to determine the 'effective_tag' that
        # the function will actually use to access the dictionary. This is
        # crucial for setting up 'data' correctly to hit different code paths.
        if len(original_tag) < 4:
            # Example: "a" -> "v00a", "ab" -> "v0ab", "abc" -> "vabc"
            effective_tag = "v" + original_tag[1:].zfill(3)
        else:
            effective_tag = original_tag

        # Decide if the 'effective_tag' should be a key in the 'data' dictionary.
        # This allows testing the `KeyError` for `data[tag]`.
        should_contain_effective_tag = fdp.ConsumeBool()

        if should_contain_effective_tag:
            # If 'effective_tag' is present, decide what kind of value it holds
            # to cover various error scenarios and the success path:
            # 0: Correct structure (list of dicts with '_')
            # 1: List of dicts, but without '_' key (leads to `KeyError` inside the inner dict)
            # 2: Empty list (leads to `IndexError` when trying to access `[0]`)
            # 3: Not a list (e.g., an integer) (leads to `TypeError` when trying to access `[0]`)
            # 4: Not a list (e.g., a string) (leads to `TypeError` when trying to access `[0]`)
            tag_value_type_choice = fdp.ConsumeIntInRange(0, 4)

            if tag_value_type_choice == 0:
                # Success path: data[effective_tag] is a list, its first element is a dict, and that dict has '_'
                final_value = fdp.ConsumeInt(4) # The actual value _get_value should return
                inner_dict = {'_': final_value}

                # Optionally add other keys to the inner dictionary for more complexity
                num_other_inner_keys = fdp.ConsumeIntInRange(0, 1)
                for _ in range(num_other_inner_keys):
                    rand_key_len = fdp.ConsumeIntInRange(1, 3)
                    rand_key = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))
                    if rand_key != '_': # Ensure we don't accidentally overwrite the crucial '_' key
                        inner_dict[rand_key] = fdp.ConsumeInt(4)

                # The list must have at least one element for `[0]` to exist
                data[effective_tag] = [inner_dict]

                # Optionally add more elements to the list to fuzz list length beyond 1
                if fdp.ConsumeBool():
                    data[effective_tag].append({'_': fdp.ConsumeInt(4)}) # Another simple valid dict

            elif tag_value_type_choice == 1:
                # Invalid path: List of dicts, but the first dict does not have the '_' key
                inner_dict_no_underscore = {'x': fdp.ConsumeInt(4)} # Some other key instead of '_'
                data[effective_tag] = [inner_dict_no_underscore]

            elif tag_value_type_choice == 2:
                # Invalid path: Empty list (causes IndexError when accessing `[0]`)
                data[effective_tag] = []

            elif tag_value_type_choice == 3:
                # Invalid path: Not a list (e.g., an integer) (causes TypeError when accessing `[0]`)
                data[effective_tag] = fdp.ConsumeInt(4)

            else: # tag_value_type_choice == 4
                # Invalid path: Not a list (e.g., a string) (causes TypeError when accessing `[0]`)
                data[effective_tag] = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))

        # Add some other random keys to the dictionary for more varied and realistic input,
        # ensuring they don't overwrite the 'effective_tag' entry if it was specifically set.
        num_random_keys = fdp.ConsumeIntInRange(0, 2) # Generate 0 to 2 additional keys
        for _ in range(num_random_keys):
            random_key_length = fdp.ConsumeIntInRange(1, 5)
            random_key = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))

            # Avoid overwriting the 'effective_tag' entry if it was already configured
            if random_key == effective_tag:
                continue

            # Choose a random value type for these additional keys
            random_value_type = fdp.ConsumeIntInRange(0, 2)
            if random_value_type == 0:
                data[random_key] = fdp.ConsumeInt(4)
            elif random_value_type == 1:
                data[random_key] = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))
            else: # A list of dictionaries (can also be empty or malformed for other keys)
                inner_list_len = fdp.ConsumeIntInRange(0, 2)
                inner_list = []
                for _ in range(inner_list_len):
                    inner_dict_rand = {}
                    num_inner_dict_keys = fdp.ConsumeIntInRange(0, 1)
                    for _ in range(num_inner_dict_keys):
                        dict_key_len = fdp.ConsumeIntInRange(1, 3)
                        dict_key = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))
                        dict_value = fdp.ConsumeInt(4)
                        inner_dict_rand[dict_key] = dict_value
                    inner_list.append(inner_dict_rand)
                data[random_key] = inner_list

        # Call the function under test (`solve_a`) with the generated 'data' and 'original_tag'.
        out_a = solve_a(data, original_tag)
        # Call the function again with identical arguments (`solve_b`) for comparison purposes.
        # In a typical scenario, solve_b would be an alternative implementation.
        out_b = solve_b(data, original_tag)
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
