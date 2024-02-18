"""Test the motion generator for panda robot."""
from __future__ import annotations

import numpy as np
from dqrobotics.robots import FrankaEmikaPandaRobot

from skrewmpcpy.pandamg import PandaSkrewMotionGenerator
from skrewmpcpy.skrewmpc import BOUND


def test_panda_mg():
    """Test panda motion generator."""
    Np = 50  # prediction horizon, can be tuned;
    Nc = 10  # control horizon, can be tuned
    R = 10e-3  # weight matirix
    Q = 10e9  # weight matrix

    JOINT_STATE = np.array(
        [
            0.000165068,
            -0.785579,
            0.000134417,
            -2.35485,
            0.00100466,
            1.57225,
            0.785951,
            -6.904296578564673e-18,
            7.806316005606509e-17,
            -3.694169137454414e-17,
            1.075687377186247e-16,
            -2.603546867034339e-17,
            -2.953811484569149e-17,
            -5.316185667767154e-17,
        ]
    )

    ub_jerk = np.array([8500.0, 8500.0, 8500.0, 4500.0, 4500.0, 4500.0])
    lb_jerk = -ub_jerk.copy()

    ub_acc = np.array([17.0, 17.0, 17.0, 9.0, 9.0, 9.0])
    lb_acc = -ub_acc.copy()

    ub_v = np.array([2.5, 2.5, 2.5, 3.0, 3.0, 3.0])
    lb_v = -ub_v.copy()

    jerk_bound = BOUND(lb_jerk, ub_jerk)
    acc_bound = BOUND(lb_acc, ub_acc)
    vel_bound = BOUND(lb_v, ub_v)

    franka_kin = FrankaEmikaPandaRobot.kinematics()
    goal = franka_kin.fkm(
        [0.173898, 0.667434, 0.782032, -1.86421, 1.44847, 1.57491, 0.889156]
    )

    mg = PandaSkrewMotionGenerator(Np, Nc, Q, R, vel_bound, acc_bound, jerk_bound)
    dq = mg.step(JOINT_STATE[: JOINT_STATE.shape[0] // 2], goal)

    np.testing.assert_almost_equal(dq, JOINT_STATE[JOINT_STATE.shape[0] // 2 :])
