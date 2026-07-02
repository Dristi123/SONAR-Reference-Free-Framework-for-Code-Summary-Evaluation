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


def _solve_a_impl(in_bval, in_bvec, dti_fn, b0_idx=0):
    import os.path as op
    import numpy as np
    from os import getcwd
    if isinstance(in_bval, list):
        in_bval = in_bval[0]
    if isinstance(in_bvec, list):
        in_bvec = in_bvec[0]
    fn_base = op.basename(dti_fn).split('.')[0]
    bvec_arr = np.loadtxt(in_bvec).T
    out_bvec = np.zeros((bvec_arr.shape[0] + 1,
                         bvec_arr.shape[1]))
    out_bvec[:] = np.nan
    out_bvec[b0_idx, :] = 0
    out_bvec[np.where(np.isnan(out_bvec))] = bvec_arr.flatten()
    bval_arr = np.loadtxt(in_bval)
    out_bval = np.zeros((bval_arr.shape[0] + 1,))
    out_bval[:] = np.nan
    out_bval[b0_idx] = 0
    out_bval[np.isnan(out_bval)] = bval_arr
    out_bvec_fn = op.join(getcwd(), fn_base + '.bvec')
    np.savetxt(out_bvec_fn, out_bvec, fmt='%.8f')
    out_bval_fn = op.join(getcwd(), fn_base + '.bval')
    np.savetxt(out_bval_fn, out_bval, fmt='%.6f')
    return out_bvec_fn, out_bval_fn

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
        import numpy as np
        import os.path as op
        import tempfile
        import os

        # Fuzzed input for dti_fn
        # dti_fn is used for op.basename(dti_fn).split('.')[0]
        # It needs to be a string that can potentially contain a dot for splitting.
        dti_fn_length = fdp.ConsumeIntInRange(1, 50)
        dti_fn = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))

        # To ensure op.basename(dti_fn).split('.')[0] works reasonably,
        # add a common extension if the fuzzed string doesn't have one, or handle trailing dot.
        if '.' not in dti_fn:
            dti_fn += fdp.PickValueInList(['.nii', '.mif', '.img']) # Add a plausible extension
        elif dti_fn.endswith('.'): # Avoid cases like 'filename.' leading to empty extension
            dti_fn += ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10))) # Add some random chars

        # Fuzzed length for b-values/vectors (N in bvec/bval files)
        # np.loadtxt expects at least one element.
        b_data_len = fdp.ConsumeIntInRange(1, 10) # Number of actual b-values/vectors

        # --- Generate in_bval file ---
        # Create a temporary file for bval data (mode='w', delete=False to keep it for the function)
        temp_bval_file_obj = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.bval')
        # Generate space-separated b-values (non-negative integers as typically expected)
        bval_data = ' '.join(str(fdp.ConsumeIntInRange(0, 5000)) for _ in range(b_data_len))
        temp_bval_file_obj.write(bval_data)
        temp_bval_file_obj.close()
        in_bval_path = temp_bval_file_obj.name

        # Decide if in_bval argument should be a path string or a list containing the path
        if fdp.ConsumeBool():
            in_bval_arg = [in_bval_path]
        else:
            in_bval_arg = in_bval_path

        # --- Generate in_bvec file ---
        # Create a temporary file for bvec data
        temp_bvec_file_obj = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.bvec')
        # Generate 3 lines of space-separated b-vector components (floats, typically between -1.0 and 1.0)
        # Each line must have b_data_len floats to match the b-values.
        bvec_line_x = ' '.join(str(fdp.ConsumeIntInRange(-100, 100) / 100.0) for _ in range(b_data_len))
        bvec_line_y = ' '.join(str(fdp.ConsumeIntInRange(-100, 100) / 100.0) for _ in range(b_data_len))
        bvec_line_z = ' '.join(str(fdp.ConsumeIntInRange(-100, 100) / 100.0) for _ in range(b_data_len))
        temp_bvec_file_obj.write(f"{bvec_line_x}\n{bvec_line_y}\n{bvec_line_z}\n")
        temp_bvec_file_obj.close()
        in_bvec_path = temp_bvec_file_obj.name

        # Decide if in_bvec argument should be a path string or a list containing the path
        if fdp.ConsumeBool():
            in_bvec_arg = [in_bvec_path]
        else:
            in_bvec_arg = in_bvec_path

        # --- Generate b0_idx ---
        # The function inserts a b0 value at b0_idx in both bval and bvec.
        # out_bvec will have (bvec_arr.shape[0] + 1) rows, which is 3 + 1 = 4 rows. So b0_idx must be in [0, 3].
        # out_bval will have (bval_arr.shape[0] + 1) elements, which is b_data_len + 1 elements. So b0_idx must be in [0, b_data_len].
        # Therefore, b0_idx must be within the range [0, min(3, b_data_len)].
        # Since b_data_len is guaranteed to be >= 1, min(3, b_data_len) will be >= 1.
        b0_idx_max = min(3, b_data_len)
        b0_idx_arg = fdp.ConsumeIntInRange(0, b0_idx_max)

        # Call the functions with identical arguments
        # Assuming `cat_n_transpose_b0_in_vects` is the `solve_a` function, and `solve_b` is provided.
        out_a = solve_a(in_bval_arg, in_bvec_arg, dti_fn, b0_idx_arg)
        out_b = solve_b(in_bval_arg, in_bvec_arg, dti_fn, b0_idx_arg)

        # Cleanup of temporary input files
        # In a real Atheris setup, this cleanup would typically be handled in a tearDown method
        # or by running each test in an isolated environment. For this specific task,
        # where ONLY the try block content is requested, we do not include explicit cleanup here
        # as it would typically be outside this scope. However, for robustness,
        # a global list `_fuzzer_created_files` could be populated for later cleanup.
        os.remove(in_bval_path)
        os.remove(in_bvec_path)

        # Also delete the output files generated by the function under test,
        # otherwise they will accumulate in getcwd().
        # Note: This is an important step for practical fuzzing but often omitted from "only try block" requests.
        # However, given the function *creates* files, it's crucial for resource management.
        fn_base_for_output = op.basename(dti_fn).split('.')[0]
        out_bvec_path = op.join(os.getcwd(), fn_base_for_output + '.bvec')
        out_bval_path = op.join(os.getcwd(), fn_base_for_output + '.bval')
        if os.path.exists(out_bvec_path):
            os.remove(out_bvec_path)
        if os.path.exists(out_bval_path):
            os.remove(out_bval_path)
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
