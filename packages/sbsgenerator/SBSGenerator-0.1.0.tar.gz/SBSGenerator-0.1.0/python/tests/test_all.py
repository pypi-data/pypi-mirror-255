import pytest
import SBSGenerator


def test_sum_as_string():
    assert SBSGenerator.sum_as_string(1, 1) == "2"
