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


import json
import random
import hashlib
from datetime import datetime


def _solve_a_impl(utc_datetime, salt='salt', password_length=10, seed=0):
    """
    Generate a random lowercase alphanumeric password of length password_length
    and then encrypt it as a JSON string. The password is hashed using SHA-256.
    The hashing uses the combination of the user provided salt and the complete 
    conventional string representation of the user provided UTC datetime. 
    
    Parameters:
    utc_datetime (datetime): The datetime in UTC.
    salt (str, optional): The salt to be used for hashing the password. Defaults to 'salt'.
    password_length (int, optional): The length of the password to be generated. Defaults to 10.
    seed (int, optional): The seed for the random number generator. Defaults to 0.
    
    Returns:
    str: The hashed password encoded as a JSON string.
    
    Requirements:
    - json
    - datetime
    - random
    - hashlib

    Raises:
    - ValueError: If the utc_datetime is not a datetime object or the salt is not a string.
    
    Example:
    >>> utc_time = datetime(2023, 6, 15, 12, 0, 0, tzinfo=pytz.UTC)
    >>> password_json_str = _solve_a_impl(utc_time)
    """
    random.seed(seed)
    # Test if the utc_datetime is a datetime object and the salt is a string
    if not isinstance(utc_datetime, datetime):
        raise ValueError("Input should be a datetime object")
    if not isinstance(salt, str):
        raise ValueError("Salt should be a string")

    # Convert the datetime to a string
    utc_time_str = utc_datetime.strftime("%Y-%m-%d %H:%M:%S")
    # Create the salted string
    salted_string = utc_time_str + salt

    # Generate a random password
    password = ''.join(random.choice('abcdefghijklmnopqrstuvwxyz0123456789') for _ in range(password_length))
    
    # Hash the password
    hashed_password = hashlib.sha256((password + salted_string).encode('utf-8')).hexdigest()
    
    # Encode the hashed password as a JSON string
    password_json_str = json.dumps(hashed_password)
    
    return password_json_str

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
        # Generate utc_datetime components
                year = fdp.ConsumeIntInRange(1, 9999)
                month = fdp.ConsumeIntInRange(1, 12)
                # To ensure a valid date and avoid ValueError from datetime constructor,
                # we restrict the day to 1-28, which is valid for all months.
                day = fdp.ConsumeIntInRange(1, 28)
                hour = fdp.ConsumeIntInRange(0, 23)
                minute = fdp.ConsumeIntInRange(0, 59)
                second = fdp.ConsumeIntInRange(0, 59)
                microsecond = fdp.ConsumeIntInRange(0, 999999)
                arg_utc_datetime = datetime(year, month, day, hour, minute, second, microsecond)

                # Generate salt (string)
                # Allow empty string as a valid salt.
                arg_salt = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))

                # Generate password_length (integer)
                # Allow password length to be 0, which results in an empty password.
                arg_password_length = fdp.ConsumeIntInRange(0, 100)

                # Generate seed (integer)
                arg_seed = fdp.ConsumeInt(4) # Consume a 4-byte integer

                # Call the functions with identical arguments and fixed random seed
                random.seed(arg_seed)
                out_a = solve_a(arg_utc_datetime, arg_salt, arg_password_length, arg_seed)
                random.seed(arg_seed)
                out_b = solve_b(arg_utc_datetime, arg_salt, arg_password_length, arg_seed)
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
