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

def test_cudaawkward_ListArray_fill_to64_from64_1():
    tostarts = cupy.array([123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    tostartsoffset = 3
    tostops = cupy.array([123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    tostopsoffset = 3
    fromstarts = cupy.array([2, 0, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1], dtype=cupy.int64)
    fromstops = cupy.array([3, 2, 4, 5, 3, 4, 2, 5, 3, 4, 6, 11], dtype=cupy.int64)
    length = 3
    base = 3
    funcC = cupy_backend['awkward_ListArray_fill', cupy.int64, cupy.int64, cupy.int64, cupy.int64]
    funcC(tostarts, tostartsoffset, tostops, tostopsoffset, fromstarts, fromstops, length, base)

    try:
        ak_cu.synchronize_cuda()
    except:
        pytest.fail("This test case shouldn't have raised an error")
    pytest_tostarts = [123, 123, 123, 5.0, 3.0, 5.0]
    assert cupy.array_equal(tostarts[:len(pytest_tostarts)], cupy.array(pytest_tostarts))
    pytest_tostops = [123, 123, 123, 6.0, 5.0, 7.0]
    assert cupy.array_equal(tostops[:len(pytest_tostops)], cupy.array(pytest_tostops))

def test_cudaawkward_ListArray_fill_to64_from64_2():
    tostarts = cupy.array([123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    tostartsoffset = 3
    tostops = cupy.array([123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    tostopsoffset = 3
    fromstarts = cupy.array([1, 0, 0, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1], dtype=cupy.int64)
    fromstops = cupy.array([8, 4, 5, 6, 5, 5, 7], dtype=cupy.int64)
    length = 3
    base = 3
    funcC = cupy_backend['awkward_ListArray_fill', cupy.int64, cupy.int64, cupy.int64, cupy.int64]
    funcC(tostarts, tostartsoffset, tostops, tostopsoffset, fromstarts, fromstops, length, base)

    try:
        ak_cu.synchronize_cuda()
    except:
        pytest.fail("This test case shouldn't have raised an error")
    pytest_tostarts = [123, 123, 123, 4.0, 3.0, 3.0]
    assert cupy.array_equal(tostarts[:len(pytest_tostarts)], cupy.array(pytest_tostarts))
    pytest_tostops = [123, 123, 123, 11.0, 7.0, 8.0]
    assert cupy.array_equal(tostops[:len(pytest_tostops)], cupy.array(pytest_tostops))

def test_cudaawkward_ListArray_fill_to64_from64_3():
    tostarts = cupy.array([123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    tostartsoffset = 3
    tostops = cupy.array([123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    tostopsoffset = 3
    fromstarts = cupy.array([1, 4, 5, 6, 5, 5, 7, 1, 2, 1, 3, 1, 5, 3, 2], dtype=cupy.int64)
    fromstops = cupy.array([1, 4, 5, 6, 5, 5, 7, 1, 2, 1, 3, 1, 5, 3, 2], dtype=cupy.int64)
    length = 3
    base = 3
    funcC = cupy_backend['awkward_ListArray_fill', cupy.int64, cupy.int64, cupy.int64, cupy.int64]
    funcC(tostarts, tostartsoffset, tostops, tostopsoffset, fromstarts, fromstops, length, base)

    try:
        ak_cu.synchronize_cuda()
    except:
        pytest.fail("This test case shouldn't have raised an error")
    pytest_tostarts = [123, 123, 123, 4.0, 7.0, 8.0]
    assert cupy.array_equal(tostarts[:len(pytest_tostarts)], cupy.array(pytest_tostarts))
    pytest_tostops = [123, 123, 123, 4.0, 7.0, 8.0]
    assert cupy.array_equal(tostops[:len(pytest_tostops)], cupy.array(pytest_tostops))

def test_cudaawkward_ListArray_fill_to64_from64_4():
    tostarts = cupy.array([123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    tostartsoffset = 3
    tostops = cupy.array([123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    tostopsoffset = 3
    fromstarts = cupy.array([1, 7, 6, 1, 3, 4, 2, 5, 2, 3, 1, 2, 3, 4, 5, 6, 7, 1, 2], dtype=cupy.int64)
    fromstops = cupy.array([1, 9, 6, 2, 4, 5, 3, 6, 3, 4, 2, 4, 5, 5, 7, 8, 2, 3], dtype=cupy.int64)
    length = 3
    base = 3
    funcC = cupy_backend['awkward_ListArray_fill', cupy.int64, cupy.int64, cupy.int64, cupy.int64]
    funcC(tostarts, tostartsoffset, tostops, tostopsoffset, fromstarts, fromstops, length, base)

    try:
        ak_cu.synchronize_cuda()
    except:
        pytest.fail("This test case shouldn't have raised an error")
    pytest_tostarts = [123, 123, 123, 4.0, 10.0, 9.0]
    assert cupy.array_equal(tostarts[:len(pytest_tostarts)], cupy.array(pytest_tostarts))
    pytest_tostops = [123, 123, 123, 4.0, 12.0, 9.0]
    assert cupy.array_equal(tostops[:len(pytest_tostops)], cupy.array(pytest_tostops))

def test_cudaawkward_ListArray_fill_to64_from64_5():
    tostarts = cupy.array([123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    tostartsoffset = 3
    tostops = cupy.array([123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    tostopsoffset = 3
    fromstarts = cupy.array([0, 0, 0, 0, 0, 0, 0, 0], dtype=cupy.int64)
    fromstops = cupy.array([1, 1, 1, 1, 1, 1, 1, 1], dtype=cupy.int64)
    length = 3
    base = 3
    funcC = cupy_backend['awkward_ListArray_fill', cupy.int64, cupy.int64, cupy.int64, cupy.int64]
    funcC(tostarts, tostartsoffset, tostops, tostopsoffset, fromstarts, fromstops, length, base)

    try:
        ak_cu.synchronize_cuda()
    except:
        pytest.fail("This test case shouldn't have raised an error")
    pytest_tostarts = [123, 123, 123, 3.0, 3.0, 3.0]
    assert cupy.array_equal(tostarts[:len(pytest_tostarts)], cupy.array(pytest_tostarts))
    pytest_tostops = [123, 123, 123, 4.0, 4.0, 4.0]
    assert cupy.array_equal(tostops[:len(pytest_tostops)], cupy.array(pytest_tostops))

