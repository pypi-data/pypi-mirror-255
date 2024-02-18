"""Usage example for the panda robot arm."""
from __future__ import annotations

import numpy as np
from dqrobotics.robots import FrankaEmikaPandaRobot

from skrewmpcpy.pandamg import PandaSkrewMotionGenerator
from skrewmpcpy.skrewmpc import BOUND


def main() -> None:
    """Print the results for further plotting."""

    Np = 50  # prediction horizon, can be tuned;
    Nc = 10  # control horizon, can be tuned
    R = 10e-3  # weight matirix
    Q = 10e9  # weight matrix

    ub_jerk = np.array([8500.0, 8500.0, 8500.0, 4500.0, 4500.0, 4500.0])
    lb_jerk = -ub_jerk.copy()

    ub_acc = np.array([17.0, 17.0, 17.0, 9.0, 9.0, 9.0])
    lb_acc = -ub_acc.copy()

    ub_v = np.array([2.5, 2.5, 2.5, 3.0, 3.0, 3.0])
    lb_v = -ub_v.copy()

    jerk_bound = BOUND(lb_jerk, ub_jerk)
    acc_bound = BOUND(lb_acc, ub_acc)
    vel_bound = BOUND(lb_v, ub_v)
    mg = PandaSkrewMotionGenerator(Np, Nc, Q, R, vel_bound, acc_bound, jerk_bound)

    joint_state = np.array(
        [
            [
                0.000165068,
                -0.785579,
                0.000134417,
                -2.35485,
                0.00100466,
                1.57225,
                0.785951,
            ],
            [
                0.00022957,
                -0.785435,
                0.000182788,
                -2.35475,
                0.00136424,
                1.57195,
                0.786283,
            ],
            [0.00022911, -0.785431, 0.000181117, -2.35475, 0.001366, 1.57195, 0.786281],
            [
                0.00022886,
                -0.785433,
                0.000178987,
                -2.35475,
                0.00136455,
                1.57195,
                0.786284,
            ],
            [
                0.000231004,
                -0.785432,
                0.000184026,
                -2.35475,
                0.00136311,
                1.57195,
                0.786281,
            ],
        ]
    )

    kin = FrankaEmikaPandaRobot.kinematics()
    goal = kin.fkm(joint_state[0, :])

    for state in joint_state:
        dq = mg.step(state, goal)
        out = [str(_dq) for _dq in dq]
        msg = ",".join(out)
        print(f"dq: {msg}")  # noqa: T201


if __name__ == "__main__":
    main()
