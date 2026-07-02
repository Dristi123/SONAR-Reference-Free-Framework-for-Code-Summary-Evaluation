import atheris
import sys
import random
from typing import List, Tuple, Dict, Optional, Any, Set
from collections import defaultdict, Counter, OrderedDict
from itertools import combinations, permutations, product
from functools import reduce
import math, re, hashlib, copy, string
import numpy as np
total = 0
matches = 0
_discarded = 0
MAX_CASES = 1000
_attempts = 0
MAX_ATTEMPTS = MAX_CASES * 5


def _solve_a_impl(boxes, overlap_thresh):
    if len(boxes) == 0:
        return []
    pick = []
    x_1 = boxes[:, 0]
    y_1 = boxes[:, 1]
    x_2 = boxes[:, 2]
    y_2 = boxes[:, 3]
    area = (x_2 - x_1 + 1) * (y_2 - y_1 + 1)  
    idxs = np.argsort(y_2)
    while len(idxs) > 0:
        last = len(idxs) - 1
        i = idxs[last]
        pick.append(i)
        xx1 = np.maximum(x_1[i], x_1[idxs[:last]])
        yy1 = np.maximum(y_1[i], y_1[idxs[:last]])
        xx2 = np.minimum(x_2[i], x_2[idxs[:last]])
        yy2 = np.minimum(y_2[i], y_2[idxs[:last]])
        w = np.maximum(0, xx2 - xx1 + 1)
        h = np.maximum(0, yy2 - yy1 + 1)
        overlap = (w * h) / area[idxs[:last]]
        idxs = np.delete(idxs, np.concatenate(([last], np.where(overlap > overlap_thresh)[0])))
    return pick

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
        # Generate overlap_thresh. It's a ratio, typically between 0.0 and 1.0.
        overlap_thresh = fdp.ConsumeIntInRange(0, 100) / 100.0

        # Generate boxes.
        # The `boxes` argument is expected to be a 2D NumPy array of shape (N, 4),
        # where each row is [x1, y1, x2, y2].
        # N (number of boxes) can range from 0 to a small number for fuzzing efficiency.
        num_boxes = fdp.ConsumeIntInRange(0, 10) 
        boxes_list = []
        for _ in range(num_boxes):
            # Generate coordinates for a bounding box.
            # To ensure valid bounding boxes (x1 <= x2, y1 <= y2) and prevent division by zero for area,
            # generate x2 >= x1 and y2 >= y1.
            # Coordinates are typically non-negative integers representing pixel locations.
            x1 = fdp.ConsumeIntInRange(0, 100)
            y1 = fdp.ConsumeIntInRange(0, 100)
            x2 = fdp.ConsumeIntInRange(x1, 100) # x2 must be >= x1
            y2 = fdp.ConsumeIntInRange(y1, 100) # y2 must be >= y1
            boxes_list.append([x1, y1, x2, y2])

        # Convert the list of boxes to a NumPy array with integer data type.
        import numpy as np # Assuming numpy is available in the fuzzing environment.
        boxes = np.array(boxes_list, dtype=np.int32)

        # Call the function under test with the generated arguments.
        out_a = solve_a(boxes, overlap_thresh)
        out_b = solve_b(boxes, overlap_thresh)
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
