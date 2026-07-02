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
from datetime import time

def _solve_a_impl(logs: list):
    """
    Analyze the given list of logs for the occurrence of errors and calculate the average time of occurrence of errors.
    
    Parameters:
    - logs (list): A list of log strings.
    
    Returns:
    - list: A list of times when errors occurred.
    - time: The average time of occurrence of these errors.
    
    Requirements:
    - re
    - datetime
    
    Example:
    >>> _solve_a_impl(['2021-06-15 09:45:00 ERROR: Failed to connect to database',\
            '2021-06-15 10:15:00 WARNING: Low disk space',\
            '2021-06-15 10:35:00 INFO: Backup completed successfully'])
    ([datetime.time(9, 45)], datetime.time(9, 45))
    """
    
    error_times = []
    total_time = 0

    for log in logs:
        if "ERROR" in log:
            time_match = re.search(r'(\d{2}):(\d{2}):\d{2}', log)
            if time_match:
                hour, minute = map(int, time_match.groups())
                error_times.append(time(hour, minute))
                total_time += hour * 60 + minute

    if error_times:
        avg_hour = (total_time // len(error_times)) // 60
        avg_minute = (total_time // len(error_times)) % 60
        avg_time = time(avg_hour, avg_minute)
    else:
        avg_time = time(0, 0)

    return error_times, avg_time

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
        # Generate the list of logs
                num_logs = fdp.ConsumeIntInRange(0, 10) # Fuzz the number of log entries
                logs = []
                for _ in range(num_logs):
                    # Construct a log string that can vary in structure but allows for time and error detection.
                    # Example format: '2021-06-15 09:45:00 ERROR: Failed to connect to database'

                    # Generate parts of the log string
                    # Date part (not parsed by the function, so general unicode is fine)
                    date_part = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))

                    # Time part (crucial for regex matching)
                    hour = fdp.ConsumeIntInRange(0, 23)
                    minute = fdp.ConsumeIntInRange(0, 59)
                    second = fdp.ConsumeIntInRange(0, 59)
                    time_part = f"{hour:02d}:{minute:02d}:{second:02d}" # Ensures HH:MM:SS format

                    # Log level (to test "ERROR" presence)
                    log_level = fdp.PickValueInList(["ERROR", "WARNING", "INFO", "DEBUG", "TRACE"])

                    # Message part (general unicode)
                    message_part = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))

                    # Assemble the log string
                    # Ensure the structure allows the regex to find time if it exists, and "ERROR" to be detected.
                    log_string = f"{date_part} {time_part} {log_level}: {message_part}"
                    logs.append(log_string)

                # Call the function under test with the generated logs
                out_a = solve_a(logs)
                out_b = solve_b(logs) # Call the function again with identical arguments
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
