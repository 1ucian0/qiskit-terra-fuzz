# -*- coding: utf-8 -*-

# Copyright 2018, IBM.
#
# This source code is licensed under the Apache License, Version 2.0 found in
# the LICENSE.txt file in the root directory of this source tree.

# pylint: disable=invalid-name

"""Pauli property testing."""

import unittest
import numpy as np
from hypothesis import given, settings
from hypothesis.strategies import composite, data, integers

from qiskit.quantum_info import Pauli
from qiskit.test import QiskitTestCase

settings.register_profile("default", max_examples=1000)
settings.load_profile("default")

@composite
def bool_array(_, length):
    return np.random.randint(2, size=length).astype(np.bool)

class TestPauli(QiskitTestCase):
    """Tests for Pauli class."""

    @given(data())
    def test_pauli(self, data):
        """Test pauli creation."""
        length = data.draw(integers(1, 10), label='length')
        z = data.draw(bool_array(length), label='z')
        x = data.draw(bool_array(length), label='x')
        q = Pauli(z, x)
        self.assertEqual(q.numberofqubits, length)
        self.assertEqual(len(q.z), length)
        self.assertEqual(len(q.x), length)
        self.assertEqual(len(q.to_label()), length)
        self.assertEqual(len(q.to_matrix()), 2 ** length)

if __name__ == '__main__':
    unittest.main()
