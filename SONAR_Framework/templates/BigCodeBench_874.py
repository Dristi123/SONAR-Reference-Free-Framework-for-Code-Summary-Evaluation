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


from itertools import zip_longest
from scipy.spatial import distance

def _solve_a_impl(points):
    """
    Calculate the Euclidean distances between consecutive points in a provided 
    list of 2D coordinates.

    This function takes a list of tuples, where each tuple contains two numbers
    representing a point in 2D space. It computes the Euclidean distance between
    each consecutive pair of points.

    If an empty list or a single point is passed, the function returns an empty list.
    If a tuple contains just one number it is assumed that both coordinates are equal to this number.
    Example: (2) == (2, 2)

    Parameters:
    points (list of tuples): A list of tuples where each tuple contains two 
                             numbers (x, y), representing a point in 2D space.

    Returns:
    list of floats: A list containing the Euclidean distances between 
                    consecutive points. Each distance is a float.
    
    Requirements:
    - itertools
    - scipy.spatial

    Example:
    >>> _solve_a_impl([(1, 2), (3, 4), (5, 6), (7, 8)])
    [2.8284271247461903, 2.8284271247461903, 2.8284271247461903]

    >>> _solve_a_impl([(1, 2), (4), (-1.2, 4)])
    [3.605551275463989, 5.2]
    """
    distances = []
    for point1, point2 in zip_longest(points, points[1:]):
        if point2 is not None:
            distances.append(distance.euclidean(point1, point2))
            
    return distances

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
        # Generate the list of points
                num_points = fdp.ConsumeIntInRange(0, 10) # Number of points in the list (0 to 10 for reasonable fuzzing)
                points = []
                for _ in range(num_points):
                    # As per the description: "If a tuple contains just one number it is assumed that
                    # both coordinates are equal to this number."
                    # Therefore, generate tuples that can have 1 or 2 elements.
                    num_coords = fdp.PickValueInList([1, 2]) # Decide if the point is (x,) or (x, y)

                    if num_coords == 1:
                        # Generate a single float coordinate for the (x,) case
                        coord = fdp.ConsumeIntInRange(-10000, 10000) / 100.0
                        point_tuple = (coord,) # Create a single-element tuple
                    else: # num_coords == 2
                        # Generate two float coordinates for the (x, y) case
                        x = fdp.ConsumeIntInRange(-10000, 10000) / 100.0
                        y = fdp.ConsumeIntInRange(-10000, 10000) / 100.0
                        point_tuple = (x, y)
                    points.append(point_tuple)

                # Call the function under test (solve_a) and the reference function (solve_b)
                out_a = solve_a(points)
                out_b = solve_b(points)
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
