"""Base motion generation module."""
from __future__ import annotations

import numpy as np
from dqrobotics import DQ, exp, log, pow, vec6

from .skrewmpc import BOUND, SkrewMPC


class BaseMotionGenerator(SkrewMPC):
    r"""Base Motion generat for Dual Quaternions, while considering jerk-, acceleration- and velocity constraints.

    :param n_p: Prediction horizon :math:`n_p`.
    :type n_p: int
    :param n_c: Control horizon :math:`n_c`.
    :type n_c: int
    :param q_mpc: :math:`\boldsymbol{Q}=q_{mpc}\boldsymbol{I}`.
    :type q_mpc: float
    :param r_mpc: :math:`\boldsymbol{R}=r_{mpc}\boldsymbol{I}.
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
        super().__init__(
            n_p, n_c, q_mpc, r_mpc, lu_bound_vel, lu_bound_acc, lu_bound_jerk
        )

        # setup internal states and kinematics
        self._mpc_state = np.zeros((18,))
        self._u_state = np.zeros((6,))

    def _step(self, current_dq: DQ, goal_dq: DQ) -> tuple[DQ, DQ]:
        """Perform one step for motion generation.

        :param current_dq: Current pose represented as Dual Quaternion.
        :type current_dq: DQ
        :param goal_dq: Goal pose represented as Dual Quaternion.
        :type goal_dq: DQ
        :return: Cartesian pose error represented and smooth trajectory.
        :rtype: tuple[DQ, DQ]
        """

        # perform optimization
        delta_dq = current_dq.inv() * goal_dq
        next_point = current_dq * pow(delta_dq, 0.1)
        desired_twist = vec6(log(next_point * current_dq.conj()))
        du = super().solve(desired_twist, self._u_state, self._mpc_state)[:6]

        # calculate the errors and compute commanded dq
        twist_out = DQ(self.c_matrix @ self._mpc_state)
        smooth_traj = exp(twist_out) * current_dq
        error = DQ(1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0) - (
            current_dq.conj() * smooth_traj
        )

        # update necessary states
        self._mpc_state = self.a_matrix @ self._mpc_state + self.b_matrix @ du
        self._u_state += du

        return error, smooth_traj

    def step(self, q_robot: np.ndarray, goal: DQ) -> np.ndarray:  # noqa: ARG002
        """Base step method (needs to be overwritten)

        Args:
            q_robot (np.ndarray): robot joint angles :math:`q \in \mathbb{R}^n`.
            goal (DQ): Goal pose represented as Dual Quaternion.

        Raises:
            NotImplementedError: Method needs overwrite

        Returns:
            np.ndarray: 1D numpy array
        """
        msg = "Step method needs to be implemented!"
        raise NotImplementedError(msg)
