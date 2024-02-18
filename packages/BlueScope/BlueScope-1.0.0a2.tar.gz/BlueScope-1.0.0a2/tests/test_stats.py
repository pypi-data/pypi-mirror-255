from unittest import mock
import pytest

from bluescope.statsutils import calculate_sample_size, find_significance

def test_sample_size():
    sample_size = calculate_sample_size(confidence_level=0.95, margin_of_error=0.05, p=0.5)
    assert sample_size == 384

def test_significance():
    t_stat, p_value = find_significance(10, 11.3, 2.5, 2.5, 384, 384)
    assert p_value < 0.05