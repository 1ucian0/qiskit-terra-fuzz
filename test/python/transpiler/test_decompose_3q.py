# -*- coding: utf-8 -*-

# Copyright 2018, IBM.
#
# This source code is licensed under the Apache License, Version 2.0 found in
# the LICENSE.txt file in the root directory of this source tree.

"""Test the decompose 3q pass"""

from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit.transpiler.passes import Decompose3Q
from qiskit.converters import circuit_to_dag
from ..common import QiskitTestCase


class TestDecompose3Q(QiskitTestCase):
    """Tests the decompose 3q pass."""

    def test_ccx(self):
        """Test decompose CCX.
        """
        qr1 = QuantumRegister(2, 'qr1')
        qr2 = QuantumRegister(1, 'qr2')
        circuit = QuantumCircuit(qr1, qr2)
        circuit.ccx(qr1[0], qr1[1], qr2[0])
        dag = circuit_to_dag(circuit)
        pass_ = Decompose3Q()
        after_dag = pass_.run(dag)
        op_nodes = after_dag.get_op_nodes(data=True)
        self.assertEqual(len(op_nodes), 15)
        for node in op_nodes:
            op = node[1]["op"]
            self.assertIn(op.name, ['h', 't', 'tdg', 'cx'])

    def test_cswap(self):
        """Test decompose CSwap (recursively).
        """
        qr1 = QuantumRegister(2, 'qr1')
        qr2 = QuantumRegister(1, 'qr2')
        circuit = QuantumCircuit(qr1, qr2)
        circuit.cswap(qr1[0], qr1[1], qr2[0])
        dag = circuit_to_dag(circuit)
        pass_ = Decompose3Q()
        after_dag = pass_.run(dag)
        op_nodes = after_dag.get_op_nodes(data=True)
        self.assertEqual(len(op_nodes), 17)
        for node in op_nodes:
            op = node[1]["op"]
            self.assertIn(op.name, ['h', 't', 'tdg', 'cx'])

    def test_decompose_conditional(self):
        """Test decompose a 3-qubit gates with a conditional.
        """
        qr = QuantumRegister(3, 'qr')
        cr = ClassicalRegister(1, 'cr')
        circuit = QuantumCircuit(qr, cr)
        circuit.ccx(qr[0], qr[1], qr[2]).c_if(cr, 1)
        dag = circuit_to_dag(circuit)
        pass_ = Decompose3Q()
        after_dag = pass_.run(dag)

        ref_circuit = QuantumCircuit(qr, cr)
        ref_circuit.h(qr[2]).c_if(cr, 1)
        ref_circuit.cx(qr[1], qr[2]).c_if(cr, 1)
        ref_circuit.tdg(qr[2]).c_if(cr, 1)
        ref_circuit.cx(qr[0], qr[2]).c_if(cr, 1)
        ref_circuit.t(qr[2]).c_if(cr, 1)
        ref_circuit.cx(qr[1], qr[2]).c_if(cr, 1)
        ref_circuit.t(qr[1]).c_if(cr, 1)
        ref_circuit.tdg(qr[2]).c_if(cr, 1)
        ref_circuit.cx(qr[0], qr[2]).c_if(cr, 1)
        ref_circuit.cx(qr[0], qr[1]).c_if(cr, 1)
        ref_circuit.tdg(qr[1]).c_if(cr, 1)
        ref_circuit.t(qr[0]).c_if(cr, 1)
        ref_circuit.cx(qr[0], qr[1]).c_if(cr, 1)
        ref_circuit.t(qr[2]).c_if(cr, 1)
        ref_circuit.h(qr[2]).c_if(cr, 1)

        ref_dag = circuit_to_dag(ref_circuit)

        self.assertEqual(after_dag, ref_dag)
