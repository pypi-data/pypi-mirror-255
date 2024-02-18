"""Utility functions for MPC."""
from __future__ import annotations

import numpy as np
import scipy as scp


def calculate_pow_series(matrix_a: np.ndarray, n_pow: int) -> np.ndarray:
    r"""Calculate the power series of matrix :math:`\boldsymbol{A} \in \mathbb{R}^{18 \times 18}`
        :math:`\left[\boldsymbol{I},\boldsymbol{A},\cdots,\boldsymbol{A}^{n_{pow} - 1}\right]`.

    :param matrix_a: matrix_a (np.ndarray): Input matrix :math:`\boldsymbol{A}`.
    :type matrix_a: np.ndarray
    :param n_pow: Maximum exponent.
    :type n_pow: int
    :return: :math:`\mathcal{A} \in \mathbb{R}^{n_{pow} \times 18 \times 18}`.
    :rtype: np.ndarray
    """

    out = np.zeros((n_pow, matrix_a.shape[0], matrix_a.shape[1]))
    out[0] = np.identity(matrix_a.shape[0])

    for i in range(1, n_pow):
        out[i] = matrix_a @ out[i - 1]

    return out


def calculate_f(
    pow_series_a: np.ndarray, matrix_c: np.ndarray
) -> scp.sparse.csc_matrix:
    r"""Calculate matrix :math:`\boldsymbol{F}`.

    :param pow_series_a: Power series calculated by function "calulate_pow_series".
    :type pow_series_a: np.ndarray
    :param matrix_c: :math:`\boldsymbol{C} \in \mathbb{R}^{6 \times 18}`.
    :type matrix_c: np.ndarray
    :return: :math:`\begin{bmatrix} \boldsymbol{CA} \\ \boldsymbol{CA}^2 \\ \vdots \\ \boldsymbol{CA}^{n_{pow}-1} \end{bmatrix}`.
    :rtype: scp.sparse.csc_matrix
    """

    out = matrix_c[None] @ pow_series_a[1:]
    return scp.sparse.csc_matrix(np.concatenate(out, axis=0))


def calculate_phi(
    pow_series_a: np.ndarray, matrix_b: np.ndarray, matrix_c: np.ndarray, n_c: int
) -> scp.sparse.csc_matrix:
    r"""Calculate matrix :math:`\boldsymbol{\Phi} \in \mathbb{R}^{6 n_p \times 6 n_c}.`

    :param pow_series_a: Power series calculated by function "calulate_pow_series".
    :type pow_series_a: np.ndarray
    :param matrix_b: :math:`\boldsymbol{B} \in \mathbb{R}^{18 \times 6}`.
    :type matrix_b: np.ndarray
    :param matrix_c: :math:`\boldsymbol{C} \in \mathbb{R}^{6 \times 18}`.
    :type matrix_c: np.ndarray
    :param n_c: :math:`n_c` describes the control horizon.
    :type n_c: int
    :raises ValueError: If control horizon is greater than prediction horizon :math:`n_c > n_p, n_p = n_{pow}`.
    :return: :math:`\boldsymbol{\Phi} \in \mathbb{R}^{6 n_p \times 6 n_c}.`
    :rtype: scp.sparse.csc_matrix
    """

    # blocks = np.linalg.multi_dot([matrix_c[None], pow_series_a[:-1], matrix_b[None]])
    if n_c > pow_series_a.shape[0]:
        error = "Control horizon must smaller than prediction horizon."
        error += " The prediction horizon is defined by the series."
        raise ValueError(error)

    blocks = pow_series_a[:-1] @ matrix_b[None]
    blocks = matrix_c[None] @ blocks
    dense_bmatrix = np.zeros((blocks.shape[0] * blocks[0].shape[0], 6 * n_c))
    n_rows, n_cols = blocks[0].shape

    for i in range(n_c):
        top = n_rows * i
        left = 6 * i
        right = left + n_cols
        dense_bmatrix[top:, left:right] = np.concatenate(
            blocks[: blocks.shape[0] - i], axis=0
        )

    return scp.sparse.csc_matrix(dense_bmatrix)


def calculate_h1_constraint(
    phi: np.ndarray | scp.sparse.csc_matrix, n_c: int
) -> np.ndarray | scp.sparse.csc_matrix:
    r"""Calculate :math:`H_1` constraint.

    :param phi: Sparse matrix `\boldsymbol{\Phi}` calculated by "calculate_phi".
    :type phi: np.ndarray | scp.sparse.csc_matrix
    :param n_c: Control horizon :math:`n_c`
    :type n_c: int
    :return: :math:`\boldsymbol{H}_1 \in \mathbb{R}^{6 \times 6 n_c}`.
    :rtype: np.ndarray | scp.sparse.csc_matrix
    """

    return phi[:6, : 6 * n_c]


def calculate_h2_constraint(n_c: int) -> scp.sparse.csc_matrix:
    r"""Calculate :math:`H_2` constraint.

    :param n_c: Control horizon :math:`n_c`
    :type n_c: int
    :return: :math:`\boldsymbol{H}_2 \in \mathbb{R}^{6 n_c \times 6 n_c}`.
    :rtype: scp.sparse.csc_matrix
    """

    h2 = np.zeros((6 * n_c, 6 * n_c))

    for i in range(n_c):
        for j in range(i + 1):
            top = i * 6
            bottom = top + 6
            left = 6 * j
            right = left + 6
            h2[top:bottom, left:right] = np.identity(6)

    return scp.sparse.csc_matrix(h2)


def calculate_h3_constraint(n_c: int) -> scp.sparse.csc_matrix:
    r"""Calculate :math:`H_3` constraint.

    :param n_c: Control horizon :math:`n_c`.
    :type n_c: int
    :return: :math:`\boldsymbol{H}_2 \in \mathbb{R}^{6 n_c \times 6 n_c}`.
    :rtype: scp.sparse.csc_matrix
    """

    return scp.sparse.eye(n_c * 6).tocsc()


def calculate_e_constraint(n_c: int) -> scp.sparse.csc_matrix:
    r"""Calculate :math:`E` constraint.

    :param n_c: Control horizon :math:`n_c`.
    :type n_c: int
    :return: :math:`\boldsymbol{H}_2 \in \mathbb{R}^{6 n_c \times 6}`.
    :rtype: scp.sparse.csc_matrix
    """

    e_constraint = np.repeat(np.eye(6)[None], n_c, axis=0).reshape(n_c * 6, -1)
    return scp.sparse.csc_matrix(e_constraint)
