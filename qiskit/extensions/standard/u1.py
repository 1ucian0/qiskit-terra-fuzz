# -*- coding: utf-8 -*-

# Copyright 2017, IBM.
#
# This source code is licensed under the Apache License, Version 2.0 found in
# the LICENSE.txt file in the root directory of this source tree.

# pylint: disable=invalid-name

"""
Diagonal single qubit gate.
"""
from qiskit.circuit import CompositeGate
from qiskit.circuit import Gate
from qiskit.circuit import QuantumCircuit
from qiskit.circuit import QuantumRegister
from qiskit.circuit.decorators import _op_expand
from qiskit.dagcircuit import DAGCircuit
from qiskit.extensions.standard.u3 import U3Gate


class U1Gate(Gate):
    """Diagonal single-qubit gate."""

    def __init__(self, theta, circ=None):
        """Create new diagonal single-qubit gate."""
        super().__init__("u1", [theta], circ)

    def _define_decompositions(self):
        decomposition = DAGCircuit()
        q = QuantumRegister(1, "q")
        decomposition.add_qreg(q)
        rule = [
            (U3Gate(0, 0, self.params[0]), [q[0]], [])
        ]
        for inst in rule:
            decomposition.apply_operation_back(*inst)
        self._decompositions = [decomposition]

    def inverse(self):
        """Invert this gate."""
        self.params[0] = -self.params[0]
        self._decompositions = None
        return self


@_op_expand(1)
def u1(self, theta, q):
    """Apply u1 with angle theta to q."""
    return self._attach(U1Gate(theta, self), [q], [])


QuantumCircuit.u1 = u1
CompositeGate.u1 = u1
