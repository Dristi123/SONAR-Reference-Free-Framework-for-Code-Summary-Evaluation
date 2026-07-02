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


from itertools import cycle
from random import choice, seed


def _solve_a_impl(n_colors, colors=['Red', 'Green', 'Blue', 'Yellow', 'Purple'], rng_seed=None):
    """
    Generates a list representing a color pattern. The pattern consists of 'n_colors' elements 
    and alternates between a cyclic sequence of colors as defined in the parameter 'colors',
    and random colors from the same list.
    Optionally, a seed for the random number generator can be provided for repeatable randomness.

    If n_colors is smaller than or equal to zero an empty list is returned.

    Parameters:
    n_colors (int): The number of colors to include in the pattern. This number indicates the total 
                    elements in the returned list, alternating between cyclic and random colors.
    colors (list of str, optional): The list of colors to generate from. 
                Defaults to  ['Red', 'Green', 'Blue', 'Yellow', 'Purple'].
    rng_seed (int, optional): A seed for the random number generator to ensure repeatability of the color selection. 
                              If 'None', the randomness is based on system time or other sources of entropy.

    Returns:
    list: A list representing the color pattern. Each element of the list is a string indicating 
          the color. For example, with n_colors=4 and a specific seed, the result could be consistent 
          across calls with the same seed.

    Requirements:
    - itertools
    - random

    Examples:
    >>> color_pattern = _solve_a_impl(4, rng_seed=123)
    >>> print(color_pattern)
    ['Red', 'Red', 'Green', 'Blue']

    >>> colors = ['Brown', 'Green', 'Black']
    >>> color_pattern = _solve_a_impl(12, colors=colors, rng_seed=42)
    >>> print(color_pattern)
    ['Brown', 'Black', 'Green', 'Brown', 'Black', 'Brown', 'Brown', 'Black', 'Green', 'Green', 'Black', 'Brown']
    """

    # Setting the seed for the random number generator
    if rng_seed is not None:
        seed(rng_seed)

    color_cycle = cycle(colors)
    color_pattern = []

    for _ in range(n_colors):
        color = next(color_cycle) if _ % 2 == 0 else choice(colors)
        color_pattern.append(color)

    return color_pattern

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
        # Generate n_colors
                n_colors = fdp.ConsumeIntInRange(0, 100)

                # Generate colors list
                # Decide whether to use the default colors or a custom list
                use_default_colors_option = fdp.ConsumeBool()
                if use_default_colors_option:
                    # Use the default colors list explicitly
                    colors_arg = ['Red', 'Green', 'Blue', 'Yellow', 'Purple']
                else:
                    # Generate a custom list of colors
                    num_custom_colors = fdp.ConsumeIntInRange(1, 10) # Ensure at least one color to avoid errors with cycle/choice
                    colors_arg = []
                    for _ in range(num_custom_colors):
                        color_len = fdp.ConsumeIntInRange(1, 100)
                        colors_arg.append(''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10))))

                # Generate rng_seed
                # To ensure deterministic behavior for comparison (out_a == out_b),
                # we always pass an integer seed to task_func.
                # If the fuzzed input suggests 'None', we use a fixed seed (e.g., 42).
                # Otherwise, we use the fuzzed integer seed.
                provide_explicit_seed = fdp.ConsumeBool()
                if provide_explicit_seed:
                    rng_seed_arg = fdp.ConsumeIntInRange(-1000000, 1000000)
                else:
                    # If the fuzzer input implied None for rng_seed,
                    # we use a fixed arbitrary seed to make task_func deterministic for comparison.
                    rng_seed_arg = 42 

                # Call the function under test (twice for comparison)
                out_a = solve_a(n_colors=n_colors, colors=colors_arg, rng_seed=rng_seed_arg)
                out_b = solve_b(n_colors=n_colors, colors=colors_arg, rng_seed=rng_seed_arg)
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
