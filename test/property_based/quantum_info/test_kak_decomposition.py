# -*- coding: utf-8 -*-

# Copyright 2019, IBM.
#
# This source code is licensed under the Apache License, Version 2.0 found in
# the LICENSE.txt file in the root directory of this source tree.

# pylint: disable=invalid-name

"""Kak decomposition property-based testing."""

import unittest
from hypothesis import given, settings
from hypothesis.strategies import integers

from qiskit.test import QiskitTestCase
from qiskit.tools.qi.qi import random_unitary_matrix
from qiskit.mapper.compiling import two_qubit_kak

settings.register_profile("default", max_examples=1000)
settings.load_profile("default")

class TestKakDecomposition(QiskitTestCase):
    """Tests for kak decomposition."""

    @given(integers(min_value=0, max_value=2**32 - 1))
    def test_kak_decomposition(self, seed):
        """Verify KAK decomposition for random Haar unitaries."""
        unitary = random_unitary_matrix(4, seed=seed)
        two_qubit_kak(unitary, verify_gate_sequence=True)

if __name__ == '__main__':
    unittest.main()
