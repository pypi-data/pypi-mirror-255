<p align="center">
  <img src="logo.jpg">
</p>
<h1 align="center">skrewmpcpy</h1>

[![Actions Status][actions-badge]][actions-link]
[![Documentation Status][rtd-badge]][rtd-link]
[![PyPI version][pypi-version]][pypi-link]
[![PyPI platforms][pypi-platforms]][pypi-link]
[![GitHub Discussion][github-discussions-badge]][github-discussions-link]

<!-- SPHINX-START -->

<!-- prettier-ignore-start -->
[actions-badge]:            https://github.com/greinerth/skrewmpcpy/actions/workflows/python-package.yml/badge.svg
[actions-link]:             https://github.com/greinerth/skrewmpcpy/actions
[github-discussions-badge]: https://img.shields.io/static/v1?label=Discussions&message=Ask&color=blue&logo=github
[github-discussions-link]:  https://github.com/greinerth/skrewmpcpy/discussions
[pypi-link]:                https://pypi.org/project/skrewmpcpy/
[pypi-platforms]:           https://img.shields.io/pypi/pyversions/skrewmpcpy
[pypi-version]:             https://img.shields.io/pypi/v/skrewmpcpy
[rtd-badge]:                https://readthedocs.org/projects/skrewmpcpy/badge/?version=latest
[rtd-link]:                 https://skrewmpcpy.readthedocs.io/en/latest/?badge=latest

<!-- prettier-ignore-end -->
Generate smooth motions for a n-DOF robot arm end effector using Dual Quaternions while enforcing velocity-, acceleration- and jerk constraints.
The package includes a base optimization scheme and a base motion generator, which can be easily extended for custom robot arms.
A motion generator for the Franka Emika Panda robot is included.
## Install

## Getting started

## Extending the available robots
For adding your custom robot arm, you easily can extend the base class. Make sure the forward kinematics of your robot are available.\
Create a new file ```your_robot_mg.py``` in folder ```src/skrewmpc.py```.
#### Costum robot example
```
from dqrobotics import DQ
from .basemg import BaseMotionGenerator
from .skrewmpc import BOUND


class YourRobotMotionGenerator(BaseMotionGenerator):

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
        # custom attributes here
        self._kin = YourRobotKinematics()

    def step(self, q_robot: np.ndarray, goal: DQ) -> np.ndarray:

        # Initialize Dual Quaternion with 6D pose
        x_current = DQ(self._kin.your_forward_kinematics(q_robot))
        error, smooth_traj = super()._step(x_current, goal)
        # calculate commanded dq here
        ...
        return dq
```
