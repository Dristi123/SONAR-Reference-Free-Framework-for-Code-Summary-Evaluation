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


def _solve_a_impl(pipeline, train_input, predict_input):
    pipeline.fit_from_scratch(train_input)
    predicted_values = pipeline.predict(predict_input)
    preds = np.ravel(np.array(predicted_values.predict))
    return preds

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
        # Definition of Mock classes to simulate the pipeline behavior.
        # These classes are defined inside the try block to be self-contained within the fuzzer's context.

        # Step 1: Pre-generate the fuzzed data that the 'predict' method's return object will hold.
        # This ensures that both 'solve_a' and 'solve_b' receive an identically constructed 'pipeline'
        # that yields the same internal prediction values.
        num_inner_preds = fdp.ConsumeIntInRange(1, 10)
        inner_preds_list = [fdp.ConsumeIntInRange(-10000, 10000) / 100.0 for _ in range(num_inner_preds)]

        # Mock class for the object returned by pipeline.predict()
        class MockPredictionResult:
            def __init__(self, values_list):
                self.predict = values_list

        # Mock class for the pipeline itself
        class MockPipeline:
            def __init__(self, predicted_result_to_return):
                self._predicted_result = predicted_result_to_return

            def fit_from_scratch(self, train_input):
                # For fuzzing this specific function, the fit operation's internal state
                # is not directly observed in the return value. A no-op is sufficient.
                pass

            def predict(self, predict_input):
                # This method returns the pre-generated mock prediction result.
                return self._predicted_result

        # Generate fuzzed inputs for the function under test:

        # 1. train_input: A list of floats
        num_train_elements = fdp.ConsumeIntInRange(1, 10)
        train_input_arg = [fdp.ConsumeIntInRange(-10000, 10000) / 100.0 for _ in range(num_train_elements)]

        # 2. predict_input: A list of floats
        num_predict_elements = fdp.ConsumeIntInRange(1, 10)
        predict_input_arg = [fdp.ConsumeIntInRange(-10000, 10000) / 100.0 for _ in range(num_predict_elements)]

        # 3. pipeline: An instance of MockPipeline
        # Create the specific MockPredictionResult once using the pre-generated list.
        predicted_result_instance = MockPredictionResult(inner_preds_list)

        # Create two independent MockPipeline instances, both configured to return the *same*
        # `predicted_result_instance` when their `predict` method is called.
        # This ensures arguments are "identical" for comparison purposes.
        pipeline_arg_a = MockPipeline(predicted_result_instance)
        pipeline_arg_b = MockPipeline(predicted_result_instance)

        # Call the function under test (assuming `fit_predict_for_pipeline` is `solve_a` and `solve_b`)
        out_a = solve_a(pipeline_arg_a, train_input_arg, predict_input_arg)
        out_b = solve_b(pipeline_arg_b, train_input_arg, predict_input_arg)
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
