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


def _solve_a_impl(image):
    orig = image
    qa = image.select('pixel_qa')
    cloudBitMask = 1 << 10
    cirrusBitMask = 1 << 11
    mask = qa.bitwiseAnd(cloudBitMask).eq(0) \
    .And(qa.bitwiseAnd(cirrusBitMask).eq(0))
    return (image.updateMask(mask).copyProperties(orig, orig.propertyNames()))

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
        # Define a minimal mock Earth Engine Image class to satisfy the function's requirements.
                # This class mimics the behavior of ee.Image methods used in maskS2clouds.
                class MockEEImage:
                    def __init__(self, value, properties=None):
                        # _value represents the pixel data relevant for 'pixel_qa' band operations.
                        # It can be an integer, or None if the image is masked out.
                        self._value = value
                        # _properties stores metadata for copyProperties.
                        self._properties = properties if properties is not None else {}

                    def select(self, band_name):
                        # For this specific function, only 'pixel_qa' band is selected.
                        # We return a new MockEEImage representing the value of this band.
                        # In a real EE scenario, this would be specific band data.
                        if band_name == 'pixel_qa':
                            return MockEEImage(self._value)
                        raise ValueError(f"MockEEImage: Band '{band_name}' not supported by mock.")

                    def bitwiseAnd(self, other):
                        # Performs a bitwise AND operation. 'other' is expected to be an integer bitmask.
                        if isinstance(self._value, int) and isinstance(other, int):
                            return MockEEImage(self._value & other)
                        # If _value is None (masked), or other is not int, this operation is undefined in mock.
                        # Returning 0 or raising an error are options; 0 is safer for fuzzing.
                        return MockEEImage(0)

                    def eq(self, other):
                        # Performs an equality comparison. 'other' is expected to be an integer (0).
                        # Returns a new MockEEImage with a boolean-like value (1 for True, 0 for False).
                        if isinstance(self._value, int) and isinstance(other, int):
                            return MockEEImage(1 if self._value == other else 0)
                        # If _value is None (masked), or other is not int, return 0 (False).
                        return MockEEImage(0)

                    def And(self, other_mask_image):
                        # Performs a logical AND operation between two mask images.
                        # Both self._value and other_mask_image._value are expected to be 0 or 1.
                        if isinstance(self._value, int) and isinstance(other_mask_image, MockEEImage) and \
                           isinstance(other_mask_image._value, int):
                            return MockEEImage(self._value & other_mask_image._value)
                        # If any value is not int (e.g., None), default to 0.
                        return MockEEImage(0)

                    def updateMask(self, mask_image):
                        # Updates the image based on a mask. If mask_image._value is 0, the image is masked out.
                        # Otherwise, the original value is retained. Properties are copied.
                        if isinstance(mask_image, MockEEImage) and isinstance(mask_image._value, int):
                            new_value = None if mask_image._value == 0 else self._value
                            return MockEEImage(new_value, self._properties.copy())
                        # If mask_image is invalid, just return a copy of self (unmasked, or whatever self was).
                        return MockEEImage(self._value, self._properties.copy())

                    def propertyNames(self):
                        # Returns a list of property names.
                        return list(self._properties.keys())

                    def copyProperties(self, source_image, properties_to_copy):
                        # Copies specified properties from source_image to a new image.
                        new_props = self._properties.copy()
                        if isinstance(source_image, MockEEImage) and isinstance(properties_to_copy, list):
                            for prop_name in properties_to_copy:
                                if prop_name in source_image._properties:
                                    new_props[prop_name] = source_image._properties[prop_name]
                        # Returns a new image with the current value and updated properties.
                        return MockEEImage(self._value, new_props)

                    # Essential for `out_a == out_b` comparison in the fuzzer.
                    def __eq__(self, other):
                        if not isinstance(other, MockEEImage):
                            return NotImplemented
                        return self._value == other._value and self._properties == other._properties

                    # Helpful for debugging fuzzer outputs.
                    def __repr__(self):
                        return f"MockEEImage(value={self._value}, properties={self._properties})"


                # Generate the integer value for the 'pixel_qa' band of the Sentinel-2 image.
                # This value is involved in bitwise operations with 1<<10 (1024) and 1<<11 (2048).
                # A 16-bit integer range (0 to 65535) is appropriate for these bitmasks.
                pixel_qa_band_value = fdp.ConsumeIntInRange(0, 65535)

                # Generate mock properties for the image.
                num_properties = fdp.ConsumeIntInRange(0, 5) # Generate up to 5 properties
                image_properties = {}
                for _ in range(num_properties):
                    prop_name = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10))) # Property name string

                    # Fuzz the type of property values as well
                    prop_value_type = fdp.PickValueInList(['int', 'str', 'bool'])
                    if prop_value_type == 'int':
                        prop_value = fdp.ConsumeIntInRange(-1000, 1000)
                    elif prop_value_type == 'str':
                        prop_value = ''.join(fdp.PickValueInList(list('abcdefghijklmnopqrstuvwxyz')) for _ in range(fdp.ConsumeIntInRange(1, 10)))
                    else: # 'bool'
                        prop_value = fdp.ConsumeBool()

                    image_properties[prop_name] = prop_value

                # Create the mock Sentinel-2 image object
                image_arg = MockEEImage(pixel_qa_band_value, image_properties)

                # Call both implementations with the fuzzed input
                out_a = solve_a(image_arg)
                out_b = solve_b(image_arg)
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
