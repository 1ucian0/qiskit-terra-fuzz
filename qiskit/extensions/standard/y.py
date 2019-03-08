# -*- coding: utf-8 -*-

# Copyright 2017, IBM.
#
# This source code is licensed under the Apache License, Version 2.0 found in
# the LICENSE.txt file in the root directory of this source tree.

# pylint: disable=invalid-name

"""
Pauli Y (bit-phase-flip) gate.
"""
from qiskit.circuit import CompositeGate
from qiskit.circuit import Gate
from qiskit.circuit import QuantumCircuit
from qiskit.circuit import QuantumRegister
from qiskit.circuit.decorators import _op_expand
from qiskit.dagcircuit import DAGCircuit
from qiskit.qasm import pi
from qiskit.extensions.standard.u3 import U3Gate


class YGate(Gate):
    """Pauli Y (bit-phase-flip) gate."""

    def __init__(self, circ=None):
        """Create new Y gate."""
        super().__init__("y", 1, [], circ)

    def _define_decompositions(self):
        decomposition = DAGCircuit()
        q = QuantumRegister(1, "q")
        decomposition.add_qreg(q)
        rule = [
            U3Gate(pi, pi/2, pi/2)
        ]
        for inst in rule:
            decomposition.apply_operation_back(inst, [q[0]], [])
        self._decompositions = [decomposition]

    def inverse(self):
        """Invert this gate."""
        return self  # self-inverse


@_op_expand(1)
def y(self, q):
    """Apply Y to q."""
    return self.append(YGate(self), [q], [])


QuantumCircuit.y = y
CompositeGate.y = y
