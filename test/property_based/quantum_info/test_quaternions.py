# -*- coding: utf-8 -*-

# Copyright 2019, IBM.
#
# This source code is licensed under the Apache License, Version 2.0 found in
# the LICENSE.txt file in the root directory of this source tree.

"""Property-based tests quaternion conversion"""

import math
import numpy as np
import scipy.linalg as la
from hypothesis import given, settings
from hypothesis.strategies import floats, integers
from hypothesis.extra.numpy import arrays

from qiskit.quantum_info.operators.quaternion import quaternion_from_euler
from qiskit.test import QiskitTestCase

settings.register_profile("default", max_examples=1000)
settings.load_profile("default")


class TestQuaternions(QiskitTestCase):
    """Tests qiskit.quantum_info.operators.quaternion"""

    @given(arrays(np.float, 3, elements=floats(-0.5, 0.5)),
           arrays(np.int, 3, elements=integers(0, 2)))
    def test_random_euler(self, random_float_array, random_int_array):
        """Quaternion from random Euler rotations."""
        # Random angles and axes
        axes = {0: 'x', 1: 'y', 2: 'z'}
        rnd = 4 * np.pi * random_float_array
        idx = random_int_array
        mat1 = rotation_matrix(rnd[0], axes[idx[0]]).dot(
            rotation_matrix(rnd[1], axes[idx[1]]).dot(
                rotation_matrix(rnd[2], axes[idx[2]])))
        axes_str = ''.join(axes[i] for i in idx)
        quat = quaternion_from_euler(rnd, axes_str)
        mat2 = quat.to_matrix()
        self.assertTrue(np.allclose(mat1, mat2))

    @given(arrays(np.float, 3, elements=floats(-0.5, 0.5)),
           arrays(np.int, 3, elements=integers(0, 2)))
    def test_orthogonality(self, random_float_array, random_int_array):
        """Quaternion rotation matrix orthogonality"""
        # Check orthogonality of generated rotation matrix
        axes = {0: 'x', 1: 'y', 2: 'z'}
        rnd = 4 * np.pi * random_float_array
        idx = random_int_array
        axes_str = ''.join(axes[i] for i in idx)
        quat = quaternion_from_euler(rnd, axes_str)
        mat = quat.to_matrix()
        self.assertTrue(np.allclose(mat.dot(mat.T), np.identity(3, dtype=float)))

    @given(arrays(np.float, 3, elements=floats(-0.5, 0.5)),
           arrays(np.int, 3, elements=integers(0, 2)))
    def test_det(self, random_float_array, random_int_array):
        """Quaternion det = 1"""
        # Check det for rotation and not reflection
        axes = {0: 'x', 1: 'y', 2: 'z'}
        rnd = 4 * np.pi * random_float_array
        idx = random_int_array
        axes_str = ''.join(axes[i] for i in idx)
        quat = quaternion_from_euler(rnd, axes_str)
        mat = quat.to_matrix()
        self.assertTrue(np.allclose(la.det(mat), 1))

    @given(arrays(np.float, 3, elements=floats(-0.5, 0.5)))
    def test_equiv_quaternions(self, random_float_array):
        """Different Euler rotations give same quaternion, up to sign."""
        # Check if euler angles from to_zyz return same quaternion
        # up to a sign (2pi rotation)
        rot = ['xyz', 'xyx', 'xzy', 'xzx', 'yzx', 'yzy', 'yxz', 'yxy', 'zxy', 'zxz', 'zyx', 'zyz']
        for value in rot:
            rnd = 4 * np.pi * random_float_array
            quat1 = quaternion_from_euler(rnd, value)
            euler = quat1.to_zyz()
            quat2 = quaternion_from_euler(euler, 'zyz')
            self.assertTrue(np.allclose(abs(quat1.data.dot(quat2.data)), 1))


def rotation_matrix(angle, axis):
    """Generates a rotation matrix for a given angle and axis.

    Args:
        angle (float): Rotation angle in radians.
        axis (str): Axis for rotation: 'x', 'y', 'z'

    Returns:
        ndarray: Rotation matrix.

    Raises:
        ValueError: Invalid input axis.
    """
    direction = np.zeros(3, dtype=float)
    if axis == 'x':
        direction[0] = 1
    elif axis == 'y':
        direction[1] = 1
    elif axis == 'z':
        direction[2] = 1
    else:
        raise ValueError('Invalid axis.')
    direction = np.asarray(direction, dtype=float)
    sin_angle = math.sin(angle)
    cos_angle = math.cos(angle)
    rot = np.diag([cos_angle, cos_angle, cos_angle])
    rot += np.outer(direction, direction) * (1.0 - cos_angle)
    direction *= sin_angle
    rot += np.array([
        [0, -direction[2], direction[1]],
        [direction[2], 0, -direction[0]],
        [-direction[1], direction[0], 0]
    ])
    return rot
