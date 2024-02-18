"""Test the utility functions."""
from __future__ import annotations

import numpy as np
import pytest

from skrewmpcpy.util import (
    calculate_e_constraint,
    calculate_f,
    calculate_h1_constraint,
    calculate_h2_constraint,
    calculate_h3_constraint,
    calculate_phi,
    calculate_pow_series,
)


def test_power_series():
    """Test the power series."""

    matrix_a = np.identity(18)
    matrix_a[:6, 6:12] = np.identity(6) * 0.1
    matrix_a[12:18, 6:12] = np.identity(6) * 0.1
    matrix_a[12:18, 0:6] = np.identity(6)
    n_power = 4

    out = calculate_pow_series(matrix_a, n_power)
    assert out.shape[0] == n_power
    assert out.shape[1] == 18
    assert out.shape[2] == 18

    current_a = np.identity(18)

    for i in range(n_power):
        np.testing.assert_array_equal(current_a, out[i])
        current_a = matrix_a @ current_a


def test_f():
    """Unit test for matrix F."""
    matrix_a = np.identity(18)
    matrix_a[:6, 6:12] = np.identity(6) * 0.1
    matrix_a[12:18, 6:12] = np.identity(6) * 0.1
    matrix_a[12:18, 0:6] = np.identity(6)

    matrix_c = np.zeros((6, 18))
    matrix_c[:6, 12:18] = np.identity(6)

    series = calculate_pow_series(matrix_a, 5)
    f_matrix = calculate_f(series, matrix_c)

    assert f_matrix.shape[1] == 18
    assert f_matrix.shape[0] == 4 * 6

    f_dense = f_matrix.toarray()
    a_current = matrix_a.copy()

    for i in range(4):
        top = 6 * i
        bottom = top + 6
        np.testing.assert_equal(matrix_c @ a_current, f_dense[top:bottom, :])
        a_current = matrix_a @ a_current


def test_phi():
    """Unit test for matrix Phi"""

    matrix_a = np.identity(18)
    matrix_a[:6, 6:12] = np.identity(6) * 0.1
    matrix_a[12:18, 6:12] = np.identity(6) * 0.1
    matrix_a[12:18, 0:6] = np.identity(6)

    matrix_b = np.zeros((18, 6))
    matrix_b[:6, :6] = np.identity(6) * 0.005
    matrix_b[6:12, :6] = np.identity(6) * 0.1
    matrix_b[12:, :6] = np.identity(6) * 0.005

    matrix_c = np.zeros((6, 18))
    matrix_c[:6, 12:18] = np.identity(6)
    series = calculate_pow_series(matrix_a, 5)

    phi = calculate_phi(series, matrix_b, matrix_c, 3)
    blocks = matrix_c[None] @ (series[:-1] @ matrix_b[None])

    assert phi.shape[0] == 6 * 4
    assert phi.shape[1] == 6 * 3

    np.testing.assert_array_equal(phi[:6, 6:].todense(), np.zeros((6, 12)))
    np.testing.assert_array_equal(phi[6:12, 12:].todense(), np.zeros((6, 6)))
    np.testing.assert_array_equal(phi[:, :6].todense(), np.concatenate(blocks, axis=0))
    np.testing.assert_array_equal(
        phi[6:, 6:12].todense(), np.concatenate(blocks[:-1], axis=0)
    )
    np.testing.assert_array_equal(
        phi[12:, 12:18].todense(), np.concatenate(blocks[:-2], axis=0)
    )

    error = "Control horizon must smaller than prediction horizon."
    error += " The prediction horizon is defined by the series."
    with pytest.raises(ValueError, match=error):
        calculate_phi(series, matrix_b, matrix_c, 14)


def test_h1_constraint():
    """Test H1 constraint matrix"""

    matrix_a = np.identity(18)
    matrix_a[:6, 6:12] = np.identity(6) * 0.1
    matrix_a[12:18, 6:12] = np.identity(6) * 0.1
    matrix_a[12:18, 0:6] = np.identity(6)

    matrix_b = np.zeros((18, 6))
    matrix_b[:6, :6] = np.identity(6) * 0.005
    matrix_b[6:12, 0:6] = np.identity(6) * 0.1
    matrix_b[12:, :6] = np.identity(6) * 0.005

    matrix_c = np.zeros((6, 18))
    matrix_c[:6, 12:18] = np.identity(6)
    series = calculate_pow_series(matrix_a, 12)
    phi = calculate_phi(series, matrix_b, matrix_c, 10)
    h1 = calculate_h1_constraint(phi, 10)

    assert h1.shape[0] == 6
    assert h1.shape[1] == 6 * 10

    if isinstance(h1, np.ndarray):
        np.testing.assert_equal(phi[:6, :60].todense(), h1)
    else:
        np.testing.assert_equal(phi[:6, :60].todense(), h1.todense())


def test_h2_constraint():
    """ "Test H2 constraint matrix"""

    # manualy construct the H2 constraint matrix
    test_constraint = np.zeros((60, 60))
    for i in range(10):
        for j in range(i + 1):
            test_constraint[i * 6 : 6 * (i + 1), j * 6 : 6 * (j + 1)] = np.eye(6)

    np.testing.assert_array_equal(
        test_constraint, calculate_h2_constraint(10).todense()
    )


def test_h3_constraint():
    """Test H3 constraint matrix"""

    test = np.eye(60)
    res = calculate_h3_constraint(10)
    assert res.shape[0] == 60
    assert res.shape[1] == 60
    np.testing.assert_equal(test, res.todense())


def test_e_constraint():
    """Test E constraint matrix"""

    # Setup matrix according original cpp implementation
    test_constraint = np.zeros((60, 6))
    for i in range(10):
        test_constraint[6 * i : 6 * (i + 1), :] = np.eye(6)
    res = calculate_e_constraint(10)

    assert res.shape[0] == 60
    assert res.shape[1] == 6

    np.testing.assert_equal(test_constraint, res.todense())
