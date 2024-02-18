"""
Copyright (c) 2024 Gerhard Reinerth. All rights reserved.

skrewmpcpy: Dual Quaternion based MPC generating skrew motion for n-DOF robot arm.

Generate smooth motions for a n-DOF robot arm end effector using Dual Quaternions while enforcing velocity-, acceleration- and jerk constraints.
The package includes a base optimization scheme and a base motion generator, which can be easily extended for custom robot arms.
A motion generator for the Franka Emika Panda robot is included.
"""


from __future__ import annotations

from ._version import version as __version__

__all__ = ["__version__"]
