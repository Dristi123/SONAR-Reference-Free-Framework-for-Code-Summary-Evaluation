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


import sys 

def _solve_a_impl(A, B, C, p, q, r): 
	diff = sys.maxsize 
	res_i = 0
	res_j = 0
	res_k = 0
	i = 0
	j = 0
	k = 0
	while(i < p and j < q and k < r): 
		minimum = min(A[i], min(B[j], C[k])) 
		maximum = max(A[i], max(B[j], C[k])); 
		if maximum-minimum < diff: 
			res_i = i 
			res_j = j 
			res_k = k 
			diff = maximum - minimum; 
		if diff == 0: 
			break
		if A[i] == minimum: 
			i = i+1
		elif B[j] == minimum: 
			j = j+1
		else: 
			k = k+1
	return A[res_i],B[res_j],C[res_k]

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
        n1 = fdp.ConsumeIntInRange(1, 10)
        array1 = [fdp.ConsumeInt(4) for _ in range(n1)]

        n2 = fdp.ConsumeIntInRange(1, 10)
        array2 = [fdp.ConsumeInt(4) for _ in range(n2)]

        n3 = fdp.ConsumeIntInRange(1, 10)
        array3 = [fdp.ConsumeInt(4) for _ in range(n3)]

        out_a = solve_a(array1, array2, array3, n1, n2, n3)
        out_b = solve_b(array1, array2, array3, n1, n2, n3)
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
