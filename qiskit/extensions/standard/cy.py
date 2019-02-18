# -*- coding: utf-8 -*-

# Copyright 2017, IBM.
#
# This source code is licensed under the Apache License, Version 2.0 found in
# the LICENSE.txt file in the root directory of this source tree.

# pylint: disable=invalid-name

"""
controlled-Y gate.
"""
from qiskit.circuit import CompositeGate
from qiskit.circuit import Gate
from qiskit.circuit import QuantumCircuit
from qiskit.circuit import QuantumRegister
from qiskit.circuit.decorators import _op_expand
from qiskit.dagcircuit import DAGCircuit
from qiskit.extensions.standard.s import SGate
from qiskit.extensions.standard.s import SdgGate
from qiskit.extensions.standard.cx import CnotGate


class CyGate(Gate):
    """controlled-Y gate."""

    def __init__(self, circ=None):
        """Create new CY gate."""
        super().__init__("cy", [], circ)

    def _define_decompositions(self):
        """
        gate cy a,b { sdg b; cx a,b; s b; }
        """
        decomposition = DAGCircuit()
        q = QuantumRegister(2, "q")
        decomposition.add_qreg(q)
        rule = [
            (SdgGate(), [q[1]], []),
            (CnotGate(), [q[0], q[1]], []),
            (SGate(), [q[1]], [])
        ]
        for inst in rule:
            decomposition.apply_operation_back(*inst)
        self._decompositions = [decomposition]

    def inverse(self):
        """Invert this gate."""
        return self  # self-inverse


@_op_expand(2)
def cy(self, ctl, tgt):
    """Apply CY to circuit."""
    return self._attach(CyGate(self), [ctl, tgt], [])


QuantumCircuit.cy = cy
CompositeGate.cy = cy
