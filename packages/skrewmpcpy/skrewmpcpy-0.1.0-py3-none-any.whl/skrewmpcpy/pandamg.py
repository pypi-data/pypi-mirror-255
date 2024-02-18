from __future__ import annotations

import numpy as np
from dqrobotics import C8, DQ, haminus8, vec8
from dqrobotics.robots import FrankaEmikaPandaRobot
from dqrobotics.utils.DQ_LinearAlgebra import pinv

from .basemg import BaseMotionGenerator
from .skrewmpc import BOUND


class PandaSkrewMotionGenerator(BaseMotionGenerator):
    r"""Motion generator for Panda robot using Dual Quaternions, while considering jerk-, acceleration- and velocity constraints.

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

        self._kin = FrankaEmikaPandaRobot.kinematics()

    def step(self, q_robot: np.ndarray, goal: DQ) -> np.ndarray:
        r"""Perform one step for motion generation.

        :param q_robot: robot joint angles :math:`q \in \mathbb{R}^7`.
        :type q_robot: np.ndarray
        :param goal: Goal pose represented as Dual Quaternion.
        :type goal: DQ
        :return: commanded joint velocity :math:`\dot{\boldsymbol{q}} \in \mathbb{R}^7`.
        :rtype: np.ndarray
        """

        x_current = self._kin.fkm(q_robot)
        error, smooth_traj = super()._step(x_current, goal)
        dot_x = vec8(error)
        j_pose = np.linalg.multi_dot(
            [haminus8(smooth_traj), C8(), self._kin.pose_jacobian(q_robot)]
        )

        return pinv(j_pose) @ dot_x
