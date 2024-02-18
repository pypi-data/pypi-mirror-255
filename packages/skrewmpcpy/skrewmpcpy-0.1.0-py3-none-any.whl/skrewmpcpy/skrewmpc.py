"""SkrewMPC class for managing the control stuff."""
from __future__ import annotations

from typing import NamedTuple

import numpy as np
import scipy as scp
from osqp import OSQP

from .util import (
    calculate_e_constraint,
    calculate_f,
    calculate_h1_constraint,
    calculate_h2_constraint,
    calculate_h3_constraint,
    calculate_phi,
    calculate_pow_series,
)


# named tuples for the SkrewMPC class
# set boundary conditions via the named tuples
class BOUND(NamedTuple):
    """Lower- and upper bound definitions for constraint optimization."""

    lower: np.ndarray
    upper: np.ndarray


class SkrewMPC:
    r"""Model Predictive Control for Dual Quaternion related control.

    :param n_p: Prediction horizon :math:`n_p`.
    :type n_p: int
    :param n_c: Control horizon :math:`n_c`.
    :type n_c: int
    :param q_mpc: :math:`\boldsymbol{Q}=q_{mpc}\boldsymbol{I}`.
    :type q_mpc: float
    :param r_mpc: :math:`\boldsymbol{R}=r_{mpc}\boldsymbol{I}`.
    :type r_mpc: float
    :param lu_bound_vel: lower- and upper bound for velocity.
    :type lu_bound_vel: BOUND
    :param lu_bound_acc: lower- and upper bound for accerlation.
    :type lu_bound_acc: BOUND
    :param lu_bound_jerk: lower- and upper bound for jerk.
    :type lu_bound_jerk: BOUND
    """

    def __init__(
        self,
        n_p: int,
        n_c: int,
        q_mpc: float,
        r_mpc: float,
        lu_bound_vel: BOUND,
        lu_bound_acc: BOUND,
        lu_bound_jerk: BOUND,
    ) -> None:
        # setup required matrices for the optimization.
        matrix_a = self.a_matrix
        matrix_b = self.b_matrix
        matrix_c = self.c_matrix

        series = calculate_pow_series(matrix_a, n_p + 1)
        self._mat_f = calculate_f(series, matrix_c)
        self._mat_f_block = self._mat_f[:6, :18]
        self._phi = calculate_phi(series, matrix_b, matrix_c, n_c)
        self._lb_vel = lu_bound_vel.lower
        self._ub_vel = lu_bound_vel.upper
        self._lb_acc = lu_bound_acc.lower
        self._ub_acc = lu_bound_acc.upper
        self._lb_jerk = lu_bound_jerk.lower
        self._ub_jerk = lu_bound_jerk.upper

        h1 = calculate_h1_constraint(self._phi, n_c)
        h2 = calculate_h2_constraint(n_c)
        h3 = calculate_h3_constraint(n_c)
        h_constraint = scp.sparse.vstack([h3, h2, h1]).tocsc()

        self._q_mpc = q_mpc
        self._r_mpc = r_mpc
        self._n_p = n_p
        self._n_c = n_c
        self._m_e_constraint = calculate_e_constraint(n_c)

        p_matrix = q_mpc * (self._phi.T @ self._phi) + r_mpc * scp.sparse.eye(n_c * 6)
        self._p_matrix = scp.sparse.triu(p_matrix, format="csc")

        self._a_matrix = h_constraint
        self._solver: OSQP = None

    def solve(
        self, desired_twist: np.ndarray, current_u: np.ndarray, mpc_state: np.ndarray
    ) -> np.ndarray:
        r"""Perform the optimization.

        :param desired_twist: 6D desired twist :math:`\mathcal{V} \in \mathbb{R}^6`.
        :type desired_twist: np.ndarray
        :param current_u: 6D state.
        :type current_u: np.ndarray
        :param mpc_state: State of mpc s.t.
            :math:`\boldsymbol{s} = \boldsymbol{As} + \boldsymbol{B}\Delta\boldsymbol{u} \in \mathbb{R}^6`.
        :type mpc_state: np.ndarray
        :return: Change of action :math:`\Delta\boldsymbol{u} \in \mathbb{R}^{6 n_c}`.
        :rtype: np.ndarray
        """

        ub_jerk = np.tile(self._ub_jerk, self._n_c)
        lb_jerk = np.tile(self._lb_jerk, self._n_c)

        e_dot_u = self._m_e_constraint @ current_u
        ub_acc = np.tile(self._ub_acc, self._n_c) + e_dot_u
        lb_acc = np.tile(self._lb_acc, self._n_c) - e_dot_u

        matf_dot_mpc_state = self._mat_f_block @ mpc_state
        ub_vel = self._ub_vel - matf_dot_mpc_state
        lb_vel = self._lb_vel + matf_dot_mpc_state

        q_vec = -self._q_mpc * (
            self._phi.T @ (np.tile(desired_twist, self._n_p) - self._mat_f @ mpc_state)
        )
        lower = np.concatenate([lb_jerk, lb_acc, lb_vel])
        upper = np.concatenate([ub_jerk, ub_acc, ub_vel])

        if self._solver is None:
            self._solver = OSQP()
            self._solver.setup(
                P=self._p_matrix,
                A=self._a_matrix,
                q=q_vec,
                l=lower,
                u=upper,
                verbose=False,
            )
        else:
            self._solver.update(q=q_vec, l=lower, u=upper)

        return self._solver.solve().x

    @property
    def a_matrix(self) -> np.ndarray:
        r"""Generate matrix A.

        :return: Matrix :math:`\boldsymbol{A} \in \mathbb{R}^{18 \times 18}`.
        :rtype: np.ndarray
        """

        matrix_a = np.identity(18)
        matrix_a[:6, 6:12] = np.identity(6) * 0.1
        matrix_a[12:18, 6:12] = np.identity(6) * 0.1
        matrix_a[12:18, 0:6] = np.identity(6)
        return matrix_a

    @property
    def b_matrix(self) -> np.ndarray:
        r"""Generate matrix B.

        :return: Matrix :math:`\boldsymbol{B} \in \mathbb{R}^{18 \times 6}`.
        :rtype: np.ndarray
        """

        matrix_b = np.zeros((18, 6))
        matrix_b[:6, :6] = np.identity(6) * 0.005
        matrix_b[6:12, 0:6] = np.identity(6) * 0.1
        matrix_b[12:, :6] = np.identity(6) * 0.005
        return matrix_b

    @property
    def c_matrix(self) -> np.ndarray:
        r"""Generate matrix C.

        :return: Matrix :math:`\boldsymbol{C} \in \mathbb{R}^{6 \times 18}`.
        :rtype: np.ndarray
        """

        matrix_c = np.zeros((6, 18))
        matrix_c[:6, 12:18] = np.identity(6)
        return matrix_c
