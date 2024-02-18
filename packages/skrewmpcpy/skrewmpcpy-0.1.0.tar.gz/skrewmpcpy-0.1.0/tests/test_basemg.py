"""BaseMotiongenerator testing."""
from __future__ import annotations

import numpy as np
import pytest
from dqrobotics import DQ

from skrewmpcpy.basemg import BaseMotionGenerator
from skrewmpcpy.skrewmpc import BOUND


def test_basemg():
    """Test the base motion generator."""
    ub_jerk = np.array([8500.0, 8500.0, 8500.0, 4500.0, 4500.0, 4500.0])
    lb_jerk = -ub_jerk.copy()

    ub_acc = np.array([17.0, 17.0, 17.0, 9.0, 9.0, 9.0])
    lb_acc = -ub_acc.copy()

    ub_v = np.array([2.5, 2.5, 2.5, 3.0, 3.0, 3.0])
    lb_v = -ub_v.copy()

    jerk_bound = BOUND(lb_jerk, ub_jerk)
    acc_bound = BOUND(lb_acc, ub_acc)
    vel_bound = BOUND(lb_v, ub_v)

    mg = BaseMotionGenerator(50, 10, 1e10, 1e-3, vel_bound, acc_bound, jerk_bound)
    msg = "Step method needs to be implemented!"

    with pytest.raises(NotImplementedError, match=msg):
        mg.step(np.zeros((7,)), DQ(1, 0, 0, 0, 0, 0, 0, 0))
