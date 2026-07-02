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


import hashlib
import binascii

def _solve_a_impl(salt, cursor):
    """
    Updates the passwords in a user table of an SQLite database by hashing them with SHA256, 
    using a provided salt. The function directly modifies the database via the given cursor.

    Parameters:
    - salt (str): The salt value to be appended to each password before hashing.
    - cursor (sqlite3.Cursor): A cursor object through which SQL commands are executed.

    Returns:
    - int: The number of users whose passwords were successfully updated.

    Requirements:
    - hashlib
    - binascii

    Raises:
    TypeError if the salt is not a string
    
    Example:
    >>> conn = sqlite3.connect('sample.db')
    >>> cursor = conn.cursor()
    >>> num_updated = _solve_a_impl('mysalt', cursor)
    >>> print(num_updated)
    5
    """
    if not isinstance(salt, str):
        raise TypeError
    cursor.execute("SELECT id, password FROM users")
    users = cursor.fetchall()
    count_updated = 0

    for user in users:
        password = user[1].encode('utf-8')
        salted_password = password + salt.encode('utf-8')
        hash_obj = hashlib.sha256(salted_password)
        hashed_password = binascii.hexlify(hash_obj.digest()).decode('utf-8')

        cursor.execute(f"UPDATE users SET password = '{hashed_password}' WHERE id = {user[0]}")
        count_updated += 1

    return count_updated

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
        import sqlite3

        # Generate salt input
        salt_len = fdp.ConsumeIntInRange(1, 100)
        salt = fdp.ConsumeUnicodeNoSurrogates(salt_len)

        # Create an in-memory SQLite database and cursor for solve_a
        conn_a = sqlite3.connect(":memory:")
        cursor_a = conn_a.cursor()
        cursor_a.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, password TEXT)")

        # Generate fuzzed user data and populate the database for solve_a
        num_users = fdp.ConsumeIntInRange(0, 10) # Number of users to insert (0 to 10)
        initial_users_data = []
        for i in range(num_users):
            user_id = fdp.ConsumeIntInRange(1, 100000) # User ID
            password_len = fdp.ConsumeIntInRange(0, 50) # Password length (can be empty)
            user_password = fdp.ConsumeUnicodeNoSurrogates(password_len)
            initial_users_data.append((user_id, user_password))
            cursor_a.execute("INSERT INTO users (id, password) VALUES (?, ?)", (user_id, user_password))
        conn_a.commit()

        # Create an identical in-memory SQLite database and cursor for solve_b
        # This ensures both functions operate on the same initial state
        conn_b = sqlite3.connect(":memory:")
        cursor_b = conn_b.cursor()
        cursor_b.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, password TEXT)")
        for user_id, user_password in initial_users_data:
            cursor_b.execute("INSERT INTO users (id, password) VALUES (?, ?)", (user_id, user_password))
        conn_b.commit()

        # Call the functions under test with identical arguments
        out_a = solve_a(salt, cursor_a)
        out_b = solve_b(salt, cursor_b)

        # Close database connections
        conn_a.close()
        conn_b.close()
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
