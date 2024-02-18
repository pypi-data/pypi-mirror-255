"""Test the MPC stuff."""
from __future__ import annotations

import numpy as np
from dqrobotics import C8, DQ, exp, haminus8, log, pow, vec6, vec8
from dqrobotics.robots import FrankaEmikaPandaRobot
from dqrobotics.utils.DQ_LinearAlgebra import pinv

from skrewmpcpy.skrewmpc import BOUND, SkrewMPC


def test_skrew_mpc():
    """Test MPC."""
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

    mpc = SkrewMPC(Np, Nc, Q, R, vel_bound, acc_bound, jerk_bound)
    A = mpc.a_matrix
    B = mpc.b_matrix
    C = mpc.c_matrix

    franka_kin = FrankaEmikaPandaRobot.kinematics()
    x_goal = franka_kin.fkm(
        [0.173898, 0.667434, 0.782032, -1.86421, 1.44847, 1.57491, 0.889156]
    )
    u_state = np.zeros((6,))
    mpc_state = np.zeros((18,))

    # setup everything for mpc
    q_current = JOINT_STATE[: JOINT_STATE.shape[0] // 2]
    x_current = franka_kin.fkm(q_current)
    delta_dq = x_current.inv() * x_goal
    next_point = x_current * pow(delta_dq, 0.1)
    desired_twist = vec6(log(next_point * x_current.conj()))
    du = mpc.solve(desired_twist, u_state, mpc_state)[:6]

    # calculate the errors and compute commanded dq
    twist_out = DQ(C @ mpc_state)
    smooth_traj = exp(twist_out) * x_current
    error = DQ(1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0) - (
        x_current.conj() * smooth_traj
    )
    dot_x = vec8(error)
    j_pose = np.linalg.multi_dot(
        [haminus8(smooth_traj), C8(), franka_kin.pose_jacobian(q_current)]
    )

    dq = pinv(j_pose) @ dot_x

    mpc_state = A @ mpc_state + B @ du
    u_state += du

    error_msg = f"dq_true: {JOINT_STATE[JOINT_STATE.shape[0] // 2:]}\n"
    error_msg += f"dq_opt: {dq}"
    np.testing.assert_almost_equal(
        dq, JOINT_STATE[JOINT_STATE.shape[0] // 2 :], err_msg=error_msg
    )
