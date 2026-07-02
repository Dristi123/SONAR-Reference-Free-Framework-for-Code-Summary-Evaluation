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


def _solve_a_impl(itunes_lookup_response):
    if len(itunes_lookup_response.get('results')) == 0:
        raise LookupError("iTunes response has no results")
    url = itunes_lookup_response.get('results')[0].get('feedUrl')
    if url is None:
        raise LookupError("feedUrl field is not present in response")
    return url

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
        # Generate the dictionary for the first item in the 'results' list
        first_result_item = {}

        # Decide if the 'feedUrl' key should be present in the first item's dictionary
        include_feed_url_key = fdp.ConsumeBool()
        if include_feed_url_key:
            # Decide if the 'feedUrl' value should be a string or None
            feed_url_value_is_string = fdp.ConsumeBool()
            if feed_url_value_is_string:
                feed_url_length = fdp.ConsumeIntInRange(1, 100)
                first_result_item['feedUrl'] = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))
            else:
                first_result_item['feedUrl'] = None
        # Add some other random keys to the first_result_item to make it more realistic
        num_other_keys_in_item = fdp.ConsumeIntInRange(0, 2)
        for _ in range(num_other_keys_in_item):
            key_len = fdp.ConsumeIntInRange(1, 10)
            value_len = fdp.ConsumeIntInRange(1, 20)
            first_result_item[''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))] = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))

        # Generate the 'results' list
        results_list = []
        # Decide the type of value for the 'results' key in the main dictionary
        # 0: a list (expected), 1: a string, 2: an integer (both leading to TypeError on len())
        results_value_type_choice = fdp.ConsumeIntInRange(0, 2)

        if results_value_type_choice == 0: # The value for 'results' is a list
            # Decide the number of items in the results list (0 for LookupError, 1+ to proceed)
            num_items_in_results_list = fdp.ConsumeIntInRange(0, 3) # Allows for 0, 1, 2, or 3 items
            if num_items_in_results_list > 0:
                results_list.append(first_result_item)
                # Add additional dummy dictionaries to the list if length > 1
                for _ in range(num_items_in_results_list - 1):
                    dummy_dict = {}
                    dummy_key_len = fdp.ConsumeIntInRange(1, 10)
                    dummy_value_len = fdp.ConsumeIntInRange(1, 20)
                    dummy_dict[''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))] = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))
                    results_list.append(dummy_dict)
            itunes_lookup_response_results_value = results_list
        elif results_value_type_choice == 1: # The value for 'results' is a string
            string_len = fdp.ConsumeIntInRange(1, 20)
            itunes_lookup_response_results_value = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))
        else: # The value for 'results' is an integer
            itunes_lookup_response_results_value = fdp.ConsumeIntInRange(-1000, 1000)

        # Construct the main itunes_lookup_response dictionary
        itunes_lookup_response = {}
        # Decide if the 'results' key should be present in the main dictionary at all
        # If not present, .get('results') will return None, leading to TypeError on len(None)
        include_results_key_in_main_dict = fdp.ConsumeBool()

        if include_results_key_in_main_dict:
            itunes_lookup_response['results'] = itunes_lookup_response_results_value

        # Add some other random keys to the main dictionary to make it more realistic
        num_other_keys_in_main = fdp.ConsumeIntInRange(0, 2)
        for _ in range(num_other_keys_in_main):
            key_len = fdp.ConsumeIntInRange(1, 10)
            value_len = fdp.ConsumeIntInRange(1, 20)
            itunes_lookup_response[''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))] = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))

        # Call the function under test
        out_a = solve_a(itunes_lookup_response)
        out_b = solve_b(itunes_lookup_response) # Assuming solve_b is identical for this exercise
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
