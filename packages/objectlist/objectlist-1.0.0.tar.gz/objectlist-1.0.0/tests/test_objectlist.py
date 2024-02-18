import pytest
import numpy as np
from objectlist import ObjectList

@pytest.fixture
def number_objectlist():
    return ObjectList([0, 1, 2])
@pytest.fixture
def numpy_objectlist():
    return ObjectList([np.array([1,2]), np.array([3,4]), np.array([5,6])])

def test_method(numpy_objectlist):
    assert numpy_objectlist.serial.sum() == [3, 7, 11]

def test_str(number_objectlist):
    assert number_objectlist.str == ['0', '1', '2']