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


import collections
import random
from queue import PriorityQueue


def _solve_a_impl(number_teams=5):
    """
    Create a random sports ranking and sort it by points in descending order.
    
    Note:
    - Each team is assigned a name in the format "Team i" and a corresponding random number of points, where i ranges from 1 to the specified number of teams. 
    - The ranking is then sorted in descending order of points and returned as an OrderedDict.

    Parameters:
    number_teams (int, optional): The number of teams in the ranking. Default is 5.

    Returns:
    OrderedDict: Sorted dictionary where keys are team names and values are points.

    Requirements:
    - collections
    - random
    - queue.PriorityQueue


    Example:
    >>> random.seed(0)
    >>> ranking = _solve_a_impl()
    >>> print(ranking)
    OrderedDict([('Team 4', 50), ('Team 5', 40), ('Team 1', 30), ('Team 2', 20), ('Team 3', 10)])
    """

    # Constants
    
    TEAMS = []
    POINTS = []

    for i in range(1, number_teams+1):
        TEAMS.append("Team "+str(i))
        POINTS.append(10*i)
    
    shuffled_points = POINTS.copy()
    random.shuffle(shuffled_points)
    ranking = dict(zip(TEAMS, shuffled_points))

    sorted_ranking = PriorityQueue()
    for team, points in ranking.items():
        sorted_ranking.put((-points, team))

    sorted_ranking_dict = collections.OrderedDict()
    while not sorted_ranking.empty():
        points, team = sorted_ranking.get()
        sorted_ranking_dict[team] = -points

    return sorted_ranking_dict

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
   
            number_teams_arg = fdp.ConsumeIntInRange(1, 20) # number_teams is an int, minimum 1 implied by "i ranges from 1 to number_teams"

            random.seed(42)
            out_a = solve_a(number_teams_arg)
            random.seed(42)
            out_b = solve_b(number_teams_arg)
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
