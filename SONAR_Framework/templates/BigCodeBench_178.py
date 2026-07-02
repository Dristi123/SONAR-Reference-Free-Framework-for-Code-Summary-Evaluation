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


import re
import json

# Constants
IP_REGEX = r'[0-9]+(?:\.[0-9]+){3}'

def _solve_a_impl(ip_address):
    """
    Get the public IP address from a JSON response containing the IP address.
    
    Parameters:
    ip_address (str): JSON-formatted string containing the IP address. 

    Returns:
    str: The public IP address.
    
    Note:
    - The function needs to check whether the provided IP address is valid.
      If the IP address is not valid, the function will return 'Invalid IP address received'.

    Requirements:
    - re
    - json
    
    Example:
    >>> ip_address = '{"ip": "192.168.1.1"}'
    >>> _solve_a_impl(ip_address)
    '192.168.1.1'
    """

    try:
        response = ip_address
        data = json.loads(response)
        ip = data['ip']
        if re.match(IP_REGEX, ip):
            return ip
        else:
            return 'Invalid IP address received'
    except Exception as e:
        return str(e)

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
        # Generate a mix of valid and invalid IP strings
        use_valid_ip = fdp.ConsumeBool()
        if use_valid_ip:
            ip_value = '.'.join(str(fdp.ConsumeIntInRange(0, 255)) for _ in range(4))
        else:
            ip_value = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz0123456789.-')) for _ in range(fdp.ConsumeIntInRange(1, 20)))

        # Create a Python dictionary that represents the expected JSON structure.
        # The key "ip" is used as per the example and the function's internal logic (data['ip']).
        json_data_dict = {"ip": ip_value}

        # Convert the dictionary into a JSON-formatted string. This ensures the
        # 'ip_address' argument is always valid JSON, as stated in the function description.
        ip_address = json.dumps(json_data_dict)

        # Call both implementations with the identical, fuzzed argument.
        out_a = solve_a(ip_address)
        out_b = solve_b(ip_address)
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
