# AUTO GENERATED ON 2024-01-31 AT 17:52:22
# DO NOT EDIT BY HAND!
#
# To regenerate file, run
#
#     python dev/generate-tests.py
#

# fmt: off

import cupy
import pytest

import awkward as ak
import awkward._connect.cuda as ak_cu
from awkward._backends.cupy import CupyBackend

cupy_backend = CupyBackend.instance()

def test_cudaawkward_UnionArray_fillindex_to64_count_1():
    toindex = cupy.array([123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    toindexoffset = 3
    length = 3
    funcC = cupy_backend['awkward_UnionArray_fillindex_count', cupy.int64]
    funcC(toindex, toindexoffset, length)

    try:
        ak_cu.synchronize_cuda()
    except:
        pytest.fail("This test case shouldn't have raised an error")
    pytest_toindex = [123, 123, 123, 0.0, 1.0, 2.0]
    assert cupy.array_equal(toindex[:len(pytest_toindex)], cupy.array(pytest_toindex))

