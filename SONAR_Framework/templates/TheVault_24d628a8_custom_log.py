import atheris
import sys
import random
from typing import List, Tuple, Dict, Optional, Any, Set
from collections import defaultdict, Counter, OrderedDict
from itertools import combinations, permutations, product
from functools import reduce
import math, re, hashlib, copy, string
import logging
total = 0
matches = 0
_discarded = 0
MAX_CASES = 1000
_attempts = 0
MAX_ATTEMPTS = MAX_CASES * 5


def _solve_a_impl(gear_context):
    log_level = gear_context.config.get('gear-log-level', 'INFO')
    try:
        suite = gear_context.manifest_json['custom']['flywheel']['suite']
    except KeyError:
        suite = 'flywheel'
    gear_name = gear_context.manifest_json['name']
    log_name = '/'.join([suite, gear_name])
    fmt = '%(asctime)s.%(msecs)03d %(levelname)-8s [%(name)s %(funcName)s()]: %(message)s'
    logging.basicConfig(level=log_level, format=fmt, 
                        datefmt='%Y-%m-%d %H:%M:%S')
    log = logging.getLogger()
    log.critical('log level is {}'.format( log_level))
    return log

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
        # Mock classes to simulate the 'gear_context' object and its attributes.
        # These classes are defined within the TestOneInput scope as requested by "ONLY your code here".

        class MockConfig:
            def __init__(self, gear_log_level_val):
                self._gear_log_level_val = gear_log_level_val

            def get(self, key, default=None):
                if key == 'gear-log-level':
                    return self._gear_log_level_val
                return default

        class MockManifestJson:
            def __init__(self, name_val, suite_val, include_full_suite_path, fdp_instance):
                self._data = {'name': name_val}
                if include_full_suite_path:
                    # If the full path should be included, create the nested dictionary structure.
                    self._data['custom'] = {
                        'flywheel': {
                            'suite': suite_val
                        }
                    }
                else:
                    # If the full path is not included, we fuzz how the KeyError is triggered.
                    # The 'custom_log' function tries to access `manifest_json['custom']['flywheel']['suite']`.
                    # A KeyError can occur if 'custom' is missing, or 'flywheel' is missing, or 'suite' is missing.
                    if fdp_instance.ConsumeBool():  # Decide if 'custom' key exists
                        self._data['custom'] = {}
                        if fdp_instance.ConsumeBool():  # If 'custom' exists, decide if 'flywheel' key exists
                            self._data['custom']['flywheel'] = {}
                            # If 'flywheel' exists, we intentionally do NOT add 'suite' here,
                            # so a KeyError will be raised when accessing 'suite'.
                    # If the first ConsumeBool() is False, 'custom' will not exist, leading to a KeyError
                    # when `manifest_json['custom']` is accessed.

            def __getitem__(self, key):
                # This method allows dictionary-like access (e.g., manifest_json['name'])
                return self._data[key]

        class MockGearContext:
            def __init__(self, config_obj, manifest_json_obj):
                self.config = config_obj
                self.manifest_json = manifest_json_obj

        # Fuzzed data generation using fdp.
        # 1. log_level: A string from a predefined list of logging levels.
        log_level_choice = fdp.PickValueInList(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])

        # 2. gear_name: A generic Unicode string.
        gear_name_str = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))

        # 3. suite_val: A generic Unicode string, used if the 'suite' path exists.
        suite_name_str = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))

        # 4. include_full_suite_path: A boolean to control whether the full 'custom.flywheel.suite' path
        #    is present in manifest_json, exercising the KeyError handling in custom_log.
        include_full_suite_path = fdp.ConsumeBool()

        # Create instances of the mock objects with fuzzed data.
        mock_config = MockConfig(log_level_choice)
        # Pass fdp_instance to MockManifestJson to allow internal fuzzing of KeyError paths.
        mock_manifest_json = MockManifestJson(gear_name_str, suite_name_str, include_full_suite_path, fdp)
        mock_gear_context = MockGearContext(mock_config, mock_manifest_json)

        # Call the function under test.
        # As per the prompt's template, we call solve_a and solve_b.
        # In this context, 'custom_log' is the function being tested, so it serves as both.
        # Note: Calling logging.basicConfig multiple times only configures the root logger once
        # unless `force=True` is used (which is not the case here).
        # Therefore, out_a and out_b will likely return the same Logger instance.
        # The primary goal of fuzzing here is to check for crashes or unexpected exceptions.
        out_a = solve_a(mock_gear_context)
        out_b = solve_b(mock_gear_context)
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
