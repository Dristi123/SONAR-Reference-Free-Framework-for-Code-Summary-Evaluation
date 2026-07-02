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


def _solve_a_impl(nn_last_layer, correct_label, learning_rate, num_classes):
    with tf.name_scope("xent"):
        cross_entropy = tf.nn.softmax_cross_entropy_with_logits_v2(labels=correct_label,
        logits=nn_last_layer)
    with tf.name_scope("loss"):
        cross_entropy_loss = tf.reduce_mean(cross_entropy)
        reg_losses = tf.get_collection(tf.GraphKeys.REGULARIZATION_LOSSES)
        reg_loss = sum(reg_losses)
        total_loss = tf.add(cross_entropy_loss, reg_loss)
    with tf.name_scope("train"):
        optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
        train_op = optimizer.minimize(total_loss)
    return None, train_op, total_loss

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
        num_classes = fdp.ConsumeIntInRange(2, 10)
        batch_size = fdp.ConsumeIntInRange(1, 5)

        nn_last_layer_val = []
        for _ in range(batch_size):
            row = []
            for _ in range(num_classes):
                # Logits can be any float value
                row.append(fdp.ConsumeIntInRange(-10000, 10000) / 100.0)
            nn_last_layer_val.append(row)

        correct_label_val = []
        for _ in range(batch_size):
            row = []
            for _ in range(num_classes):
                # Labels for cross-entropy are typically probabilities or one-hot (values 0 to 1)
                row.append(fdp.ConsumeIntInRange(0, 100) / 100.0)
            correct_label_val.append(row)

        # Learning rate is a positive float, often small (e.g., 0.0001 to 1.0)
        learning_rate = fdp.ConsumeIntInRange(1, 10000) / 10000.0

        out_a = solve_a(nn_last_layer_val, correct_label_val, learning_rate, num_classes)
        out_b = solve_b(nn_last_layer_val, correct_label_val, learning_rate, num_classes)
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
